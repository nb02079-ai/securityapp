#!/usr/bin/env python3
"""
재구성 사기 대화에서 작성자의 의도가 드러나는 정보를 지운 '가림판'을 만든다.
자유 메모(plan.md 5.2 1단계)와 라벨링을 사례 작성자가 아닌 사람·세션이 할 때 쓴다.

사용법
  python tools/scam/make_blind.py data/eval/scam/*.jsonl --out <저장소 밖 폴더> [--shuffle-seed N]

  --shuffle-seed 없이 실행하면 파일 이름 순서대로 C01, C02 … 를 붙인다 (자유 메모 때 쓴 방식).
  --shuffle-seed N 을 주면 같은 N에서 항상 같은 순서로 섞는다. 라벨링부터는 섞은 판을 쓴다
  (파일 목록을 아는 사람이 번호표 없이 사례를 알아맞히지 못하게).

지우는 것
  - 출처 표시(provenance), 근거 메모(source_note), 날짜 근거(day_source)
  - meta 전체 (사례 이름, 유형, 출처, 근거 강도, 금액 메모 등)
남기는 것
  - 메시지 순서, 날짜(dN), 방, 보낸 사람 표시 이름, 본인 메시지 여부, 메시지 내용
  - 단, 보낸 사람 이름에 '사칭' 같은 작성자의 판단이 들어 있으면 '상대'로 바꾼다
  - 실제 알림을 보는 사람도 볼 수 있는 정보만 남긴다

결과
  blind_cases.md   새 세션에 넣을 가림판 (사례 이름은 C01~C10 같은 중립 번호)
  blind_key.csv    중립 번호 ↔ 원래 사례 이름 (새 세션에 넣지 말 것)
"""
import argparse
import csv
import json
import os
import random
import re
import sys


def room_names(msgs):
    """방 이름도 작성자가 붙인 설명이라 '단체방', '1:1 대화 A'처럼 중립적으로 바꾼다."""
    names, n_dm, n_group = {}, 0, 0
    for m in msgs:
        r = m["room"]
        if r in names:
            continue
        senders = {x["sender"] for x in msgs if x["room"] == r and not x["is_user"]}
        if r.startswith("sms"):
            names[r] = "문자"
        elif r in ("call", "video"):
            # 새 평가 세트(holdout_v2): 전화·영상통화 녹취. 앱 알림에는 없으므로 평가기는 넣지 않지만 라벨러는 흐름을 봐야 함
            names[r] = "전화 통화" if r == "call" else "영상통화"
        elif r.startswith("group") or len(senders) >= 2:
            n_group += 1
            names[r] = "단체방" if n_group == 1 else f"단체방 {n_group}"
        else:
            names[r] = f"1:1 대화 {chr(ord('A') + n_dm)}"
            n_dm += 1
    return names


# 작성자의 판단이 들어간 보낸 사람 이름 (실제 알림에는 이런 이름이 보이지 않음)
JUDGMENT_WORDS = ("사칭", "사기", "스캐머", "바람잡이", "조직")


def display_sender(m, room_label):
    """상대가 스스로 내세운 이름(비서, 상담원 등)은 두고, 판단이 담긴 이름만 중립적으로 바꾼다."""
    if m["is_user"]:
        return "나"
    name = m["sender"]
    # holdout_v2: "증권사 비서(사칭)", "지인(계정 도용)"처럼 괄호 속 판단만 지우고, 바람잡이·화력팀은 알림에 보일 법한 이름으로
    name = re.sub(r"\((사칭|공범|계정 도용|번호 도용)\)", "", name).strip()
    name = re.sub(r"^바람잡이", "회원", name)
    name = re.sub(r"^화력팀", "시청자", name)
    if any(w in name for w in JUDGMENT_WORDS):
        return "발신 번호" if room_label == "문자" else "상대"
    return name


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--out", required=True)
    ap.add_argument("--shuffle-seed", type=int, default=None,
                    help="주면 사례 순서를 이 시드로 섞어 번호를 붙임")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    md = ["# 대화 기록 (가림판)\n",
          "각 사례는 한 사람(\"나\")이 받은 메시지와 보낸 메시지를 시간 순서로 모은 것입니다.",
          "- `dN`은 첫 대화로부터 며칠째인지입니다.",
          "- `[사진]`, `[파일]`은 사진·파일이 왔다는 표시만 보이는 메시지입니다.",
          "- `(링크)`, `(계좌번호)` 등은 원래 내용이 있던 자리를 가린 것입니다.\n"]
    key = []
    # 같은 파일을 두 번 넣어도 한 번만 (번호가 겹치거나 사례가 중복되지 않게)
    files = sorted({os.path.realpath(f) for f in args.files}, key=os.path.basename)
    if len({os.path.basename(f) for f in files}) != len(files):
        sys.exit("[오류] 다른 폴더에 같은 이름의 파일이 있음")
    if args.shuffle_seed is not None:
        random.Random(args.shuffle_seed).shuffle(files)
    for i, path in enumerate(files, 1):
        with open(path, encoding="utf-8") as f:
            lines = [json.loads(l) for l in f if l.strip()]
        meta, msgs = lines[0], lines[1:]
        if meta.get("type") != "meta":
            sys.exit(f"[오류] {path}: 첫 줄이 meta가 아님")
        cid = f"C{i:02d}"
        key.append({"blind_id": cid, "case_id": meta["case_id"], "file": os.path.basename(path)})
        rn = room_names(msgs)
        md.append(f"\n## 사례 {cid}\n")
        md.append("| # | 날짜 | 방 | 보낸 사람 | 메시지 |")
        md.append("|---|---|---|---|---|")
        for m in msgs:
            sender = display_sender(m, rn[m["room"]])
            text = m["text"].replace("|", "\\|")
            md.append(f"| {m['seq']} | d{m['day']} | {rn[m['room']]} | {sender} | {text} |")

    with open(os.path.join(args.out, "blind_cases.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")
    with open(os.path.join(args.out, "blind_key.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["blind_id", "case_id", "file"])
        w.writeheader()
        w.writerows(key)
    print(f"가림판 {len(key)}건 → {os.path.join(args.out, 'blind_cases.md')}")
    order = "파일 이름 순서" if args.shuffle_seed is None else f"시드 {args.shuffle_seed}로 섞음"
    print(f"번호 순서: {order}")
    print(f"번호표 → {os.path.join(args.out, 'blind_key.csv')} (새 세션에 넣지 말 것)")


if __name__ == "__main__":
    main()
