#!/usr/bin/env python3
"""
2단계 평가 라벨용 가림판 만들기 (docs/labeling/08_label_decisive.md).
평가(test) 사기 통화를 시드 고정으로 섞어 T001… 번호를 붙이고, 라벨러가 읽을 md 묶음과 빈 CSV를 만든다.

사용법
  py tools/korccvi/make_label_pack.py --calls <import_calls.py --out 폴더>/test --out <저장소 밖 폴더> [--parts 4] [--seed 20261028]

결과 (<out>)
  label_in/blind_part{1..N}.md   통화 원문 (라벨러에게 줌)
  label_in/label_points.csv      빈 양식 (call, decisive_seq, kind, reason) — 라벨러에게 줌
  blind_key.csv                  T번호 → call_id (라벨러에게 주지 않음)
  화면에는 통화 수·글자 수·파일 해시만 출력 (이 세션은 평가 통화 내용을 보지 않음)
"""
import argparse
import csv
import hashlib
import json
import os
import random
import sys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--calls", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--parts", type=int, default=4)
    ap.add_argument("--seed", type=int, default=20261028)
    args = ap.parse_args()
    if os.path.basename(os.path.normpath(args.calls)) != "test":
        sys.exit("[멈춤] --calls는 평가(test) 폴더여야 합니다")
    calls = []
    for f in sorted(os.listdir(args.calls)):
        if not f.endswith(".jsonl"):
            continue
        with open(os.path.join(args.calls, f), encoding="utf-8") as fh:
            rows = [json.loads(l) for l in fh if l.strip()]
        if rows[0]["label"] == "scam":
            calls.append((rows[0]["case_id"], rows[1:]))
    rng = random.Random(args.seed)
    rng.shuffle(calls)
    os.makedirs(os.path.join(args.out, "label_in"), exist_ok=True)
    n = len(calls)
    # 글자 수가 비슷하도록 순서대로 자름 (긴 통화가 한 파일에 몰리지 않게)
    lens = [sum(len(m["text"]) for m in msgs) for _, msgs in calls]
    total, chunks, cur, acc = sum(lens), [], [], 0
    for c, ln in zip(calls, lens):
        cur.append(c)
        acc += ln
        if len(chunks) < args.parts - 1 and acc >= total * (len(chunks) + 1) / args.parts:
            chunks.append(cur)
            cur = []
    if cur:
        chunks.append(cur)
    key, sizes, start = [], [], 1
    for p, chunk in enumerate(chunks):
        lines = [f"# 통화 가림판 {p + 1}/{len(chunks)}", "",
                 "각 줄: `번호 화자: 말`. 화자는 자동으로 나눈 것이라 틀릴 수 있습니다 (\"상대\" = 전화를 건 쪽으로 추정한 사람).", ""]
        for i, (cid, msgs) in enumerate(chunk, start):
            t = f"T{i:03d}"
            key.append((t, cid))
            lines += [f"## 통화 {t}", ""]
            for m in msgs:
                who = "나" if m.get("is_user") else "상대"
                lines.append(f"{m['seq']} {who}: {m['text']}")
            lines.append("")
        start += len(chunk)
        path = os.path.join(args.out, "label_in", f"blind_part{p + 1}.md")
        body = "\n".join(lines)
        with open(path, "w", encoding="utf-8") as f:
            f.write(body)
        sizes.append((os.path.basename(path), len(chunk), len(body), hashlib.sha256(body.encode()).hexdigest()[:12]))
    with open(os.path.join(args.out, "label_in", "label_points.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["call", "decisive_seq", "kind", "reason"])
        for t, _ in key:
            w.writerow([t, "", "", ""])
    with open(os.path.join(args.out, "blind_key.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["call", "call_id"])
        w.writerows(key)
    print(f"사기 통화 {n}건 → {len(chunks)}개 파일")
    for s in sizes:
        print("  %s: 통화 %d건, %d자, sha256 %s…" % s)


if __name__ == "__main__":
    main()
