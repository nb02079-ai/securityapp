#!/usr/bin/env python3
"""
학습·개발 예시 만들기. 대화 하나 × 관점 하나 × 상대 메시지 위치(접두) 여러 개 → 예시 한 줄.
사기 대화의 모든 접두는 1, 일반 대화는 0 (대화 단위 정답, docs/v3_plan.md 3단계).

  py tools/model/build_examples.py --input <폴더> [--input ...] --out <파일.jsonl> [--per-conv 16] [--max-convs-per-source callcenter=3000] [--seed 20261028]

평가 세트(test 폴더, data/eval)는 받지 않음.
"""
import argparse
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import load_dir, perspectives, prefix_text  # noqa: E402


def positions(n, k):
    """1..n 중 k개를 고르게 (마지막 포함)."""
    if n <= k:
        return list(range(1, n + 1))
    return sorted({max(1, round(n * (i + 1) / k)) for i in range(k)})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", action="append", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--per-conv", type=int, default=16)
    ap.add_argument("--max-convs-per-source", action="append", default=[], help="출처=최대 대화 수 (예: callcenter=3000)")
    ap.add_argument("--max-chars", type=int, default=600)
    ap.add_argument("--seed", type=int, default=20261028)
    a = ap.parse_args()
    for p in a.input:
        norm = os.path.abspath(p).replace("\\", "/")
        if norm.rstrip("/").endswith("/test") or "/data/eval" in norm:
            sys.exit(f"[멈춤] 평가 세트는 학습 예시에 넣지 않습니다: {p}")
    caps = {k: int(v) for k, v in (x.split("=") for x in a.max_convs_per_source)}
    rng = random.Random(a.seed)
    convs = [c for p in a.input for c in load_dir(p)]
    by_src = {}
    for c in convs:
        by_src.setdefault(c["source"], []).append(c)
    chosen = []
    for src, cs in sorted(by_src.items()):
        if src in caps and len(cs) > caps[src]:
            cs = rng.sample(cs, caps[src])
        chosen += cs
    n = {0: 0, 1: 0}
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as f:
        for c in chosen:
            y = 1 if c["label"] == "scam" else 0
            for pname, cp in perspectives(c):
                for k in positions(len(cp), a.per_conv):
                    t = prefix_text(cp, k, a.max_chars)
                    if not t:
                        continue
                    f.write(json.dumps({"conv": c["id"], "source": c["source"], "persp": pname, "k": k,
                                        "label": y, "text": t}, ensure_ascii=False) + "\n")
                    n[y] += 1
    print(f"대화 {len(chosen)}개 → 예시 {n[0] + n[1]}개 (사기 {n[1]}, 일반 {n[0]}) → {a.out}")
    for src, cs in sorted(by_src.items()):
        print(f"  {src}: {sum(1 for c in chosen if c['source'] == src)}/{len(cs)} 대화")


if __name__ == "__main__":
    main()
