#!/usr/bin/env python3
"""
5단계-1: 고정한 모델(model-v2)을 ONNX로 바꾸고 int8로 줄인다. 휴대폰에서 ONNX Runtime으로 돌리기 위한 것.

  py tools/model/export_onnx.py --model <model_v2>\best --out <저장소 밖 폴더>

결과 (<out>)
  model.onnx        fp32 (입력 input_ids·attention_mask·token_type_ids, 출력 logits, 배치·길이 가변)
  model_int8.onnx   가중치 int8 동적 양자화
  vocab.txt 등      토크나이저 파일 (휴대폰에서 같은 토큰화를 하려고 함께 둠)
  export_info.json  원본 모델 해시 확인 결과, 파일 크기, 설정
원본 모델이 docs/results/model-v2/freeze.json과 같은지 먼저 확인한다 (--freeze, 기본 경로).
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from freeze import digest  # noqa: E402

NAMES = ("input_ids", "attention_mask", "token_type_ids")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--freeze", default=os.path.join("docs", "results", "model-v2", "freeze.json"))
    ap.add_argument("--opset", type=int, default=18)
    ap.add_argument("--exporter", choices=("dynamo", "legacy"), default="dynamo",
                    help="dynamo = torch.export 기반(기본). legacy(TorchScript)는 transformers 마스크 계산을 상수로 굳혀 점수가 틀어짐(11-18 확인)")
    ap.add_argument("--tol", type=float, default=1e-3, help="원본과 fp32 ONNX 점수 차이 허용치")
    a = ap.parse_args()

    with open(a.freeze, encoding="utf-8") as f:
        rec = json.load(f)
    if digest(a.model) != rec["files"]:
        sys.exit("[멈춤] 모델 파일이 고정 기록(freeze.json)과 다릅니다")
    print(f"고정한 모델과 같음 ({rec['name']}, 문턱 {rec['threshold']})")

    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    os.makedirs(a.out, exist_ok=True)
    tok = AutoTokenizer.from_pretrained(a.model)
    model = AutoModelForSequenceClassification.from_pretrained(a.model, attn_implementation="eager").eval()

    class Wrap(torch.nn.Module):
        def __init__(self, m):
            super().__init__()
            self.m = m

        def forward(self, input_ids, attention_mask, token_type_ids):
            return self.m(input_ids=input_ids, attention_mask=attention_mask, token_type_ids=token_type_ids).logits

    enc = tok(["예시 문장입니다 | 둘째 메시지", "안녕하세요 서울중앙지검 수사관입니다 | 본인 명의 계좌가 범죄에 연루되어"],
              return_tensors="pt", padding=True, truncation=True)
    if "token_type_ids" not in enc:
        enc["token_type_ids"] = torch.zeros_like(enc["input_ids"])
    args = tuple(enc[n] for n in NAMES)
    fp32 = os.path.join(a.out, "model.onnx")
    kw = dict(input_names=list(NAMES), output_names=["logits"], opset_version=a.opset,
              dynamic_axes={**{n: {0: "batch", 1: "seq"} for n in NAMES}, "logits": {0: "batch"}})
    if a.exporter == "dynamo":
        torch.onnx.export(Wrap(model), args, fp32, dynamo=True, external_data=False, **kw)
    else:
        torch.onnx.export(Wrap(model), args, fp32, dynamo=False, **kw)
    print("ONNX fp32 →", fp32)

    import numpy as np
    import onnxruntime as ort
    from onnxruntime.quantization import QuantType, quantize_dynamic

    int8 = os.path.join(a.out, "model_int8.onnx")
    quantize_dynamic(fp32, int8, weight_type=QuantType.QInt8)
    print("ONNX int8 →", int8)
    tok.save_pretrained(a.out)

    # 점검: 길이가 다른 입력(패딩 있음/없음, 배치 1·3)에서 원본과 ONNX 점수가 같은지
    checks = [["짧은 문장"],
              ["오늘 저녁 뭐 먹을까 | 김치찌개 어때", "고객님 명의로 대출이 접수되어 확인차 연락드렸습니다 | 지금 안전계좌로 옮기셔야 합니다",
               "네 | 알겠습니다 | 내일 봬요"]]
    sessions = {name: ort.InferenceSession(path, providers=["CPUExecutionProvider"])
                for name, path in (("fp32", fp32), ("int8", int8))}
    rows, worst = [], {"fp32": 0.0, "int8": 0.0}
    for texts in checks:
        e = tok(texts, return_tensors="pt", padding=True, truncation=True, max_length=256)
        if "token_type_ids" not in e:
            e["token_type_ids"] = torch.zeros_like(e["input_ids"])
        with torch.no_grad():
            ref = torch.softmax(Wrap(model)(*(e[n] for n in NAMES)), -1)[:, 1].numpy()
        feed = {n: e[n].numpy().astype(np.int64) for n in NAMES}
        got = {}
        for name, sess in sessions.items():
            lg = sess.run(["logits"], feed)[0]
            z = np.exp(lg - lg.max(-1, keepdims=True))
            got[name] = z[:, 1] / z.sum(-1)
            worst[name] = max(worst[name], float(np.abs(got[name] - ref).max()))
        for i, t in enumerate(texts):
            rows.append({"text": t[:30], "torch": round(float(ref[i]), 6),
                         "fp32": round(float(got["fp32"][i]), 6), "int8": round(float(got["int8"][i]), 6)})
    info = {"source_model": rec["name"], "threshold": rec["threshold"], "opset": a.opset, "exporter": a.exporter,
            "sizes_mb": {os.path.basename(p): round(os.path.getsize(p) / 2**20, 1) for p in (fp32, int8)},
            "max_abs_diff": worst, "checks": rows}
    with open(os.path.join(a.out, "export_info.json"), "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=1)
    print(json.dumps(info, ensure_ascii=False, indent=1))
    if worst["fp32"] > a.tol:
        sys.exit(f"[실패] fp32 ONNX 점수가 원본과 {worst['fp32']:.4f}만큼 다릅니다 (허용 {a.tol}). 변환이 잘못됐습니다")
    print(f"[통과] fp32 차이 {worst['fp32']:.2e}, int8 차이 {worst['int8']:.2e}")


if __name__ == "__main__":
    main()
