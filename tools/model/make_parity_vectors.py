"""파이썬 판정기 결과를 Kotlin 이식(scorer 모듈)과 맞춰 보기 위한 벡터 만들기 (docs/v3_plan.md 5단계-2).

저장소에 있는 합성·재구성 대화(재배포 문제 없음)와 직접 만든 경계 문장만 씁니다. 평가 세트는 거부합니다.
  py tools/model/make_parity_vectors.py --onnx <model_v2_onnx>\\model_int8.onnx --out <저장소 밖>\\parity_vectors.jsonl

한 줄 = 한 관점: {"conv","persp","msgs":[상대 메시지…],"items":[{"k","text","ids","score"}…]}
  text  = prefix_text(msgs, k)            (common.py)
  ids   = 토크나이저 결과 (truncation left, max_len 256)
  score = ONNX 점수, 배치 1개·덧대기 없음 (앱과 같은 조건)
그다음 Kotlin 쪽: gradlew :eval:parity --args="--vectors … --tokenizer …\\tokenizer.json --onnx …\\model_int8.onnx"
"""
import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import load_dir, perspectives, prefix_text  # noqa: E402

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DEFAULT_INPUTS = ["data/dev/synthetic", "data/dev/synthetic2", "data/dev/reconstructed"]

# 글 정리·토큰 나누기의 경계 사례 (직접 만든 문장)
EDGE = [
    ["고객님 명의로 대출이 접수되어 확인차 연락드렸습니다.", "안전계좌로 옮기셔야 합니다."],
    ["010-1234-5678로 전화 주세요!!", "계좌 000-00-0000 / 금액 1,500,000원"],
    ["OOO 수사관입니다", "○○지검 김○ 검사", "XX은행 ●●● 팀장", "**카드 ＊＊＊"],
    ["ＡＢＣ　전각 공백", "줄 바꿈 없는 공백", "탭\t줄\n바꿈\r\n끝"],
    ["Hello WORLD İstanbul ΣΑΣ", "café naïve é", "ẞ ß ﬁ Ⓐ x² ①②③ Ⅻ"],
    ["😀😀 웃음 ㅋㅋㅋ ㅠㅠ 👍🏻", "漢字 섞인 金融 문장 𠀀", "١٢٣ ٤ 𝟏𝟐 ｱｲｳ"],
    ["under_score_test __init__", "#해시 |파이프| a|b#c", "!!!", "   ", "", "?"],
    ["zero​width ﻿BOM \u0000ctrl\u0007 � 대체"],
    ["가" * 150, "님" * 30 + "고객" * 20],
    ["오늘 회의는 3시입니다. " * 40, "확인 부탁드립니다 " * 30],
    ["https://bit.ly/abc123 링크 눌러서 앱 설치하세요", "kakao@pay.com 으로 메일 주세요"],
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--onnx", required=True, help="model_int8.onnx (토크나이저도 같은 폴더에서 읽음)")
    ap.add_argument("--model", help="토크나이저 폴더 (기본: --onnx 폴더)")
    ap.add_argument("--input", nargs="*", default=DEFAULT_INPUTS)
    ap.add_argument("--out", required=True)
    ap.add_argument("--max-len", type=int, default=256)
    ap.add_argument("--max-chars", type=int, default=600)
    ap.add_argument("--no-score", action="store_true", help="ONNX 점수 없이 글·토큰만")
    a = ap.parse_args()

    for p in a.input:
        ap_ = os.path.abspath(p).replace("\\", "/")
        if "/data/eval" in ap_ or "test" in os.path.basename(ap_).lower():
            sys.exit(f"[오류] 평가 세트는 쓰지 않습니다: {p}")
    out_abs = os.path.abspath(a.out)
    if os.path.commonpath([out_abs, REPO]) == REPO:
        sys.exit("[오류] --out 은 저장소 밖에 두세요 (큰 파일)")

    import numpy as np
    import onnx
    from transformers import AutoTokenizer
    tok_dir = a.model or os.path.dirname(os.path.abspath(a.onnx))
    tok = AutoTokenizer.from_pretrained(tok_dir)
    tok.truncation_side = "left"
    m = onnx.load(a.onnx, load_external_data=False)
    print(f"ONNX ir_version={m.ir_version}, opset={[(o.domain or 'ai.onnx', o.version) for o in m.opset_import]}")
    tj_path = os.path.join(tok_dir, "tokenizer.json")
    tj = {}
    if os.path.exists(tj_path):
        with open(tj_path, encoding="utf-8") as f:
            tj = json.load(f)
    else:
        print(f"(참고) {tj_path} 없음 → 설정 출력 생략")
    print(f"normalizer={json.dumps(tj.get('normalizer'), ensure_ascii=False)}")
    print(f"pre_tokenizer={tj.get('pre_tokenizer', {}).get('type')}, post_processor={(tj.get('post_processor') or {}).get('type')}, "
          f"추가 토큰 {len(tj.get('added_tokens', []))}개(특수 아님 {sum(1 for t in tj.get('added_tokens', []) if not t.get('special'))})")

    sess = None
    if not a.no_score:
        import onnxruntime as ort
        so = ort.SessionOptions()
        so.intra_op_num_threads = 1
        sess = ort.InferenceSession(a.onnx, so, providers=["CPUExecutionProvider"])
        names = [i.name for i in sess.get_inputs()]

    def score(ids):
        x = np.array([ids], dtype=np.int64)
        feed = {"input_ids": x, "attention_mask": np.ones_like(x), "token_type_ids": np.zeros_like(x)}
        lg = sess.run(None, {n: feed[n] for n in names})[0]
        e = np.exp(lg - lg.max(-1, keepdims=True))
        return float((e[:, 1] / e.sum(-1))[0])

    groups = []
    for p in a.input:
        for c in load_dir(os.path.join(REPO, p) if not os.path.isabs(p) else p):
            for pname, cp in perspectives(c):
                groups.append((c["id"], pname, [t for _, t in cp]))
    for i, msgs in enumerate(EDGE, 1):
        groups.append((f"edge{i:02d}", "edge", msgs))

    n = 0
    t0 = time.time()
    os.makedirs(os.path.dirname(out_abs), exist_ok=True)
    with open(out_abs, "w", encoding="utf-8", newline="\n") as f:
        for cid, pname, msgs in groups:
            items = []
            cp = [(None, t) for t in msgs]
            for k in range(1, len(msgs) + 1):
                text = prefix_text(cp, k, a.max_chars)
                ids = tok(text, truncation=True, max_length=a.max_len)["input_ids"]
                items.append({"k": k, "text": text, "ids": ids, "score": score(ids) if sess else None})
                n += 1
            f.write(json.dumps({"conv": cid, "persp": pname, "msgs": msgs, "items": items}, ensure_ascii=False) + "\n")
    print(f"관점 {len(groups)}개, 위치 {n}개 → {out_abs} ({time.time() - t0:.1f}초)")


if __name__ == "__main__":
    main()
