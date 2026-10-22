#!/usr/bin/env python3
"""
라벨링용 빈 시트를 만든다. 번호(C01~)는 make_blind.py와 같은 규칙으로 붙인다.

사용법
  python tools/scam/make_label_sheet.py data/eval/scam/*.jsonl --out <저장소 밖 폴더> --shuffle-seed N [--cases C03,C07]

결과 (엑셀에서 바로 열리도록 UTF-8 BOM)
  label_messages.csv  상대방 메시지마다 한 줄: 신호·단계·확신·메모 칸이 비어 있음
  label_points.csv    사례마다 한 줄: 첫 금전 권유·첫 송금 직전 칸이 비어 있음
  --cases 를 주면 그 사례만 넣는다 (두 번째 라벨러용)

같은 파일·같은 시드로 make_blind.py를 돌린 가림판과 번호가 같다 (순서 규칙을 그대로 따름).
make_blind.py의 순서 규칙을 바꾸면 ordered()도 같이 바꿀 것.
"""
import argparse
import csv
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_blind import display_sender, room_names  # noqa: E402


def ordered(files, seed):
    """make_blind.py main()과 같은 순서 규칙."""
    files = sorted({os.path.realpath(f) for f in files}, key=os.path.basename)
    if len({os.path.basename(f) for f in files}) != len(files):
        sys.exit("[오류] 다른 폴더에 같은 이름의 파일이 있음")
    if seed is not None:
        random.Random(seed).shuffle(files)
    return files


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--out", required=True)
    ap.add_argument("--shuffle-seed", type=int, default=None)
    ap.add_argument("--cases", default="", help="쉼표로 구분한 가림판 번호 (예: C03,C07)")
    args = ap.parse_args()
    want = {c.strip().upper() for c in args.cases.split(",") if c.strip()}
    os.makedirs(args.out, exist_ok=True)

    msg_rows, point_rows, seen = [], [], set()
    for i, path in enumerate(ordered(args.files, args.shuffle_seed), 1):
        cid = f"C{i:02d}"
        seen.add(cid)
        if want and cid not in want:
            continue
        with open(path, encoding="utf-8") as f:
            lines = [json.loads(l) for l in f if l.strip()]
        if lines[0].get("type") != "meta":
            sys.exit(f"[오류] {path}: 첫 줄이 meta가 아님")
        msgs = lines[1:]
        rn = room_names(msgs)
        for m in msgs:
            if m["is_user"]:
                continue  # 신호는 상대방 메시지에만 붙인다 (가이드 2장)
            msg_rows.append({"case": cid, "seq": m["seq"], "room": rn[m["room"]],
                             "sender": display_sender(m, rn[m["room"]]), "text": m["text"],
                             "signals": "", "stage": "", "confidence": "", "note": ""})
        point_rows.append({"case": cid, "n_messages": len(msgs), "first_suggest": "",
                           "first_transfer_before": "", "transfer_seen": "", "reason": ""})

    missing = want - seen
    if missing:
        sys.exit(f"[오류] 없는 사례 번호: {sorted(missing)}")

    def write(name, rows, fields):
        with open(os.path.join(args.out, name), "w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(rows)

    write("label_messages.csv", msg_rows, list(msg_rows[0].keys()))
    write("label_points.csv", point_rows, list(point_rows[0].keys()))
    order = "파일 이름 순서" if args.shuffle_seed is None else f"시드 {args.shuffle_seed}로 섞음"
    print(f"사례 {len(point_rows)}건, 상대방 메시지 {len(msg_rows)}줄 ({order}) → {args.out}")


if __name__ == "__main__":
    main()
