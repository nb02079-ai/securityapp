#!/usr/bin/env python3
"""
두 점수 파일(score.py 결과)을 위치마다 맞대어 비교 — 변환(ONNX·int8) 전후가 같은 판정을 내는지.

  py tools/model/compare_scores.py --a <원본 scores.csv> --b <변환 scores.csv> --threshold 0.843446001
"""
import argparse
import csv
import statistics
from collections import defaultdict


def read(path):
    d = {}
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["seq"]:
                d[(r["conv"], r["persp"], int(r["seq"]))] = (float(r["score"]), r["label"])
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", required=True)
    ap.add_argument("--b", required=True)
    ap.add_argument("--threshold", type=float, required=True)
    a = ap.parse_args()
    A, B = read(a.a), read(a.b)
    keys = sorted(set(A) & set(B))
    if len(keys) != len(A) or len(keys) != len(B):
        print(f"[주의] 위치 수가 다름: a {len(A)}, b {len(B)}, 공통 {len(keys)}")
    if not keys:
        raise SystemExit("[오류] 공통 위치가 없음")
    diffs = [abs(A[k][0] - B[k][0]) for k in keys]
    same = sum((A[k][0] >= a.threshold) == (B[k][0] >= a.threshold) for k in keys)
    conv = defaultdict(lambda: [False, False])
    for k in keys:
        conv[k[0]][0] |= A[k][0] >= a.threshold
        conv[k[0]][1] |= B[k][0] >= a.threshold
    flips = [c for c, (x, y) in conv.items() if x != y]
    print(f"위치 {len(keys)}개: 점수 차이 최대 {max(diffs):.4f}, 평균 {statistics.mean(diffs):.6f}")
    print(f"위치별 판정 일치 {same}/{len(keys)} ({100 * same / len(keys):.2f}%)")
    print(f"대화별 경고 여부 일치 {len(conv) - len(flips)}/{len(conv)} — 달라진 대화 {len(flips)}개: {flips[:10]}")


if __name__ == "__main__":
    main()
