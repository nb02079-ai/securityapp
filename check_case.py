#!/usr/bin/env python3
"""
재구성 사기 대화(.jsonl) 점검 + 읽기용 표(.md) 생성.

사용법
  python tools/scam/check_case.py data/eval/scam/scam01_leadingroom_band.jsonl [더 많은 파일...]

점검 항목 (plan.md 5.2 재구성 원칙)
  1. 형식: 첫 줄 meta, 이후 message. seq가 1부터 빠짐없이 이어지는지, 필수 필드가 있는지
  2. 출처 표시: provenance가 quote / described / connector 중 하나인지
  3. 연결 메시지에 위험 신호 단어가 없는지 (tools/aihub/extract_candidates.py의 KEYWORD_GROUPS 사용)
  4. 비식별: 계좌번호·전화번호처럼 보이는 숫자열이 없는지
문제가 있으면 종료 코드 1. 인용 문장이 출처 원문과 일치하는지는 출처가 기사라 자동 확인할 수 없으므로 사람이 확인한다.
"""
import importlib.util
import json
import os
import re
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
EC_PATH = os.path.join(HERE, "..", "aihub", "extract_candidates.py")

REQUIRED = ("seq", "room", "sender", "is_user", "day", "text", "provenance", "source_note")
PROV = {"quote": "인용", "described": "서술 기반", "connector": "연결"}
# 계좌·전화번호처럼 보이는 숫자열 (하이픈 포함 10자리 이상 숫자)
ID_LIKE = re.compile(r"(?:\d[\d-]{8,}\d)")


def load_keyword_groups():
    spec = importlib.util.spec_from_file_location("ec", EC_PATH)
    ec = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ec)
    return {g: re.compile(p) for g, p in ec.KEYWORD_GROUPS.items()}


def check(path, kw):
    problems = []
    with open(path, encoding="utf-8") as f:
        lines = [json.loads(l) for l in f if l.strip()]
    if not lines or lines[0].get("type") != "meta":
        return None, ["첫 줄이 meta가 아님"]
    meta, msgs = lines[0], lines[1:]

    for i, m in enumerate(msgs, 1):
        miss = [k for k in REQUIRED if k not in m]
        if miss:
            problems.append(f"seq {m.get('seq', '?')}: 필드 없음 {miss}")
            continue
        if m["seq"] != i:
            problems.append(f"seq 순서 어긋남: {i}번째 줄의 seq={m['seq']}")
        if m["provenance"] not in PROV:
            problems.append(f"seq {m['seq']}: provenance 값 이상 '{m['provenance']}'")
        if m["provenance"] == "connector":
            hit = [g for g, p in kw.items() if p.search(m["text"])]
            if hit:
                problems.append(f"seq {m['seq']}: 연결 메시지에 위험 신호 단어 {hit} — '{m['text']}'")
        if ID_LIKE.search(m["text"]):
            problems.append(f"seq {m['seq']}: 계좌·전화번호처럼 보이는 숫자열 — 비식별 확인")
    return (meta, msgs), problems


def well_formed(msgs):
    return [m for m in msgs if all(k in m for k in REQUIRED)]


def render(path, meta, msgs):
    msgs = well_formed(msgs)  # 필드가 빠진 줄은 문제 목록에만 남김
    rooms = meta.get("rooms", {})
    c = Counter(m["provenance"] for m in msgs)
    out = [f"# {meta['case_id']} — {meta.get('scam_type', '')}\n",
           f"- 출처: [{meta['source']['title']}]({meta['source']['url']}), {meta['source']['published']}"]
    for key, name in (("entry_point", "유입"), ("anonymized", "비식별"), ("evidence_strength", "근거 강도"),
                      ("amounts", "금액"), ("room_assumption", "방 가정"), ("ending", "끝")):
        if meta.get(key):
            out.append(f"- {name}: {meta[key]}")
    out.append(f"- 메시지 {len(msgs)}개 (인용 {c['quote']} · 서술 기반 {c['described']} · 연결 {c['connector']}), "
               f"그중 피해자 본인 {sum(m['is_user'] for m in msgs)}개")
    out.append("- 라벨: 아직 없음. 완성본을 처음부터 읽고 따로 붙입니다.\n")
    out.append("| # | 날짜 | 방 | 보낸 사람 | 메시지 | 출처 | 근거 |")
    out.append("|---|---|---|---|---|---|---|")
    for m in msgs:
        d = f"d{m['day']}" + ("" if m.get("day_source") == "기사" else "*")
        sender = "**나**" if m["is_user"] else m["sender"]
        room = rooms.get(m["room"], m["room"]).split(" (")[0]
        out.append(f"| {m['seq']} | {d} | {room} | {sender} | {m['text']} | {PROV.get(m.get('provenance'), '⚠' + str(m.get('provenance')))} | {m['source_note']} |")
    out.append("\n`*` 표시 날짜는 기사에 없어 순서만 맞춘 추정입니다.")
    md = os.path.splitext(path)[0] + ".md"
    with open(md, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    return md


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    kw = load_keyword_groups()
    bad = 0
    for path in sys.argv[1:]:
        parsed, problems = check(path, kw)
        name = os.path.basename(path)
        if parsed is None:
            print(f"[실패] {name}: {problems[0]}")
            bad += 1
            continue
        meta, msgs = parsed
        md = render(path, meta, msgs)
        c = Counter(m["provenance"] for m in well_formed(msgs))
        status = "통과" if not problems else f"문제 {len(problems)}개"
        print(f"[{status}] {name}: 메시지 {len(msgs)} (인용 {c['quote']} / 서술 {c['described']} / 연결 {c['connector']}) → {os.path.basename(md)}")
        for p in problems:
            print("   -", p)
        bad += bool(problems)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
