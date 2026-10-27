#!/usr/bin/env python3
"""
대화마다·관점마다 상대 메시지가 하나 올 때마다 위험 점수 (0~1)를 매김 → scores.csv.

  py tools/model/score.py --model <모델 폴더>/best --input <폴더> [--input ...] --out scores.csv [--eval-set]
  py tools/model/score.py --scorer words --input ... --out scores.csv      (모델 없이 단어 기준선으로 파이프라인 점검)

평가(test) 폴더는 --eval-set 을 붙여야 함 (모델을 태그로 고정한 뒤 한 번만, plan.md 7.2).
"""
import argparse
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import load_dir, perspectives, prefix_text  # noqa: E402

WORDS = ("송금", "입금", "계좌", "투자", "수익")  # plan.md 7.2 단어 기준선


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", action="append", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--model")
    ap.add_argument("--scorer", choices=("model", "words"), default="model")
    ap.add_argument("--batch", type=int, default=64)
    ap.add_argument("--max-len", type=int, default=256)
    ap.add_argument("--max-chars", type=int, default=600)
    ap.add_argument("--eval-set", action="store_true")
    a = ap.parse_args()
    for p in a.input:
        norm = os.path.abspath(p).replace("\\", "/").rstrip("/")
        if (norm.endswith("/test") or "/data/eval" in norm) and not a.eval_set:
            sys.exit(f"[멈춤] 평가 세트입니다: {p}. 모델을 고정한 뒤 --eval-set 을 붙여 한 번만 돌립니다.")
    convs = [c for p in a.input for c in load_dir(p)]
    items = []
    for c in convs:
        ps = perspectives(c)
        if not ps:
            items.append((c, "-", None, ""))
        for pname, cp in ps:
            if not cp:
                items.append((c, pname, None, ""))
            for k in range(1, len(cp) + 1):
                items.append((c, pname, cp[k - 1][0], prefix_text(cp, k, a.max_chars)))
    print(f"대화 {len(convs)}개, 점수 매길 위치 {sum(1 for i in items if i[2] is not None)}개")

    if a.scorer == "words":
        def score_batch(texts):
            return [1.0 if any(w in t for w in WORDS) else 0.0 for t in texts]
    else:
        if not a.model:
            sys.exit("[오류] --model 이 필요합니다")
        import torch
        from transformers import AutoModelForSequenceClassification, AutoTokenizer
        dev = "cuda" if torch.cuda.is_available() else "cpu"
        tok = AutoTokenizer.from_pretrained(a.model)
        tok.truncation_side = "left"
        model = AutoModelForSequenceClassification.from_pretrained(a.model, attn_implementation="eager").to(dev).eval()

        def score_batch(texts):
            with torch.no_grad():
                enc = tok(texts, truncation=True, max_length=a.max_len, padding=True, return_tensors="pt").to(dev)
                return torch.softmax(model(**enc).logits.float(), -1)[:, 1].tolist()

    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["conv", "label", "source", "persp", "seq", "score"])
        todo = [i for i in items if i[2] is not None]
        for c, pname, seq, _ in items:
            if seq is None:
                w.writerow([c["id"], c["label"], c["source"], pname, "", ""])
        for s in range(0, len(todo), a.batch):
            chunk = todo[s:s + a.batch]
            for (c, pname, seq, _), sc in zip(chunk, score_batch([t for *_, t in chunk])):
                w.writerow([c["id"], c["label"], c["source"], pname, seq, f"{sc:.6f}"])
            if (s // a.batch) % 50 == 0:
                print(f"  {s + len(chunk)}/{len(todo)}", flush=True)
    print("→", a.out)


if __name__ == "__main__":
    main()
