#!/usr/bin/env python3
"""
개발 세트 점수로 문턱을 바꿔 가며 탐지율과 출처별 오탐을 한 표로 (문턱 고르기 참고용, 개발 세트 전용).

  py tools/model/sweep.py --scores dev_scores.csv [--out sweep.md]

각 줄: 어느 한 출처의 일반 대화 오탐을 0·1·3·5·10%에 맞춘 문턱과, 그때 다른 출처 오탐·탐지율·첫 경고 위치.
"""
import argparse
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from metrics import evaluate, pick_threshold, read_scores  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scores", action="append", required=True)
    ap.add_argument("--out")
    a = ap.parse_args()
    for p in a.scores:
        if "test" in os.path.basename(p).lower():
            sys.exit("[멈춤] 평가 세트 점수로 문턱을 고르지 않습니다")
    convs = read_scores(a.scores)
    srcs = sorted({c["source"] for c in convs.values() if c["label"] == "normal"})
    lines = ["| 맞춘 기준 | 문턱 | 탐지율 | " + " | ".join(f"{s} 오탐" for s in srcs) + " | 첫 경고 위치 중앙값 |",
             "|---|---|---|" + "---|" * len(srcs) + "---|"]
    for base in srcs + ["pooled"]:
        for fp in (0.0, 0.01, 0.03, 0.05, 0.10):
            th = pick_threshold(convs, fp, None if base == "pooled" else base)
            r = evaluate(convs, th, {})
            det = sum(x["detected"] for x in r["scam"])
            cells = []
            for s in srcs:
                rows = [x for x in r["normal"] if x["source"] == s]
                k = sum(x["warned"] for x in rows)
                cells.append(f"{k}/{len(rows)} ({100 * k / len(rows):.1f}%)")
            ks = [x["first_k"] for x in r["scam"] if x["detected"] and x["first_k"]]
            med = statistics.median(ks) if ks else "-"
            lines.append(f"| {base} ≤{int(fp * 100)}% | {th:.6f} | {det}/{len(r['scam'])} ({100 * det / len(r['scam']):.1f}%) | "
                         + " | ".join(cells) + f" | {med} |")
    text = "# 문턱별 탐지율·출처별 오탐 (개발 세트)\n\n" + "\n".join(lines) + "\n"
    print(text)
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            f.write(text)


if __name__ == "__main__":
    main()
