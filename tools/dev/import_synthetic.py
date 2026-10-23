#!/usr/bin/env python3
"""
다른 모델이 쓴 개발용 합성 대화 CSV(docs/dev/01_synthetic_prompt.md 형식)를 개발 세트 .jsonl로 바꾼다.

사용법
  python tools/dev/import_synthetic.py <CSV> --model <모델 이름> [--out data/dev/synthetic]

결과
  data/dev/synthetic/<모델>/<case>_<kind>.jsonl
  첫 줄 meta(case_id, kind, type, model, source), 이후 한 줄이 메시지 하나
  (평가 세트 data/eval/scam/*.jsonl과 같은 칸: seq, room, sender, is_user, day, text)

점검: 칸 이름, kind(scam/normal), is_user(true/false)와 sender "나"가 맞는지, 사례 안 seq가 1부터 이어지는지.
문제가 있으면 아무것도 쓰지 않고 멈춘다.
"""
import argparse
import csv
import json
import os
import re
import sys

FIELDS = ["case", "kind", "type", "seq", "day", "room", "sender", "is_user", "text"]


def read(path):
    for enc in ("utf-8-sig", "cp949"):
        try:
            with open(path, encoding=enc, newline="") as f:
                return list(csv.DictReader(f))
        except UnicodeDecodeError:
            continue
    sys.exit(f"[오류] 인코딩을 읽을 수 없음: {path}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("--model", required=True)
    ap.add_argument("--out", default=os.path.join("data", "dev", "synthetic"))
    args = ap.parse_args()
    model = re.sub(r"[^a-z0-9_-]", "", args.model.lower())
    if not model:
        sys.exit("[오류] --model 이름이 비어 있음")

    rows = read(args.csv)
    if not rows or [k.strip() for k in rows[0].keys()] != FIELDS:
        sys.exit(f"[오류] 칸 이름이 다름: {list(rows[0].keys()) if rows else '빈 파일'}")
    problems, cases = [], {}
    for r in rows:
        r = {k.strip(): (v or "").strip() for k, v in r.items()}
        if r["kind"] not in ("scam", "normal"):
            problems.append(f"{r['case']}#{r['seq']}: kind '{r['kind']}'")
        if r["is_user"] not in ("true", "false"):
            problems.append(f"{r['case']}#{r['seq']}: is_user '{r['is_user']}'")
        elif (r["is_user"] == "true") != (r["sender"] == "나"):
            problems.append(f"{r['case']}#{r['seq']}: sender '{r['sender']}'와 is_user '{r['is_user']}'가 맞지 않음")
        cases.setdefault(r["case"], []).append(r)
    for c, ms in cases.items():
        seqs = [int(m["seq"]) for m in ms]
        if seqs != list(range(1, len(seqs) + 1)):
            problems.append(f"{c}: seq가 1부터 이어지지 않음")
        if len({m["kind"] for m in ms}) != 1 or len({m["type"] for m in ms}) != 1:
            problems.append(f"{c}: 한 사례 안에 kind·type이 여러 개")
    if problems:
        print("[실패] 문제:")
        for p in problems:
            print("  -", p)
        sys.exit(1)

    out_dir = os.path.join(args.out, model)
    os.makedirs(out_dir, exist_ok=True)
    for c, ms in cases.items():
        kind = ms[0]["kind"]
        path = os.path.join(out_dir, f"{c}_{kind}.jsonl")
        with open(path, "w", encoding="utf-8") as f:
            meta = {"type": "meta", "case_id": f"{model}_{c}", "kind": kind, "scam_type": ms[0]["type"],
                    "model": args.model, "source": "합성 (docs/dev/01_synthetic_prompt.md)"}
            f.write(json.dumps(meta, ensure_ascii=False) + "\n")
            for m in ms:
                f.write(json.dumps({"type": "message", "seq": int(m["seq"]), "room": m["room"], "sender": m["sender"],
                                    "is_user": m["is_user"] == "true", "day": int(m["day"] or 0), "text": m["text"]},
                                   ensure_ascii=False) + "\n")
    n_scam = sum(1 for ms in cases.values() if ms[0]["kind"] == "scam")
    print(f"{args.model}: 사례 {len(cases)}건 (사기 {n_scam}, 정상 {len(cases) - n_scam}), 메시지 {len(rows)}개 → {out_dir}")


if __name__ == "__main__":
    main()
