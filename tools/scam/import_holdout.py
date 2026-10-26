#!/usr/bin/env python3
"""
봉인된 새 평가 세트(docs/holdout_v2.md)의 원본 md → 평가기 형식(.jsonl)으로 바꾼다.

  python tools/scam/import_holdout.py [--src data/eval/holdout_v2/source_sealed.md] [--out data/eval/holdout_v2]

원본은 고치지 않는다. 먼저 SHA-256이 봉인 기록과 같은지 확인하고, 다르면 멈춘다.

변환 규칙 (결정 26, 평가 전에 정함)
  1. 원본 CSV 줄 끝의 출처 표시(\\[1\\] 등)는 칸 밖에 붙어 있어 지운다. 메시지 내용은 바꾸지 않는다.
  2. 1:1 방(dm, kakao_dm)은 상대마다 따로 방으로 나눈다 (dm_<상대>). 실제로는 사람마다 대화방이 따로이기 때문.
     "나"의 메시지는 같은 방 종류에서 가장 가까운 앞 상대(없으면 뒤 상대)의 방으로 넣는다.
  3. 전화·영상통화(call, video)는 앱이 받는 알림이 아니므로 channel=voice로 표시한다. 평가기는 이 메시지를 엔진에 넣지 않는다.
  4. 유튜브 실시간 채팅(live_chat)은 여러 사람이 있는 방이라 group_live로 둔다.
  5. 원래 메시지 번호(seq)는 그대로 둔다. 라벨과 금전 지점은 이 번호를 쓴다.
"""
import argparse, csv, hashlib, io, json, os, re, sys

SEALED_SHA256 = "419dee388f879e1f9cb9505fdbd7c304f6f915f5e5bebc520583ee5335022232"
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))

TYPES = {
    "C01": "유명인 사칭 투자 (리딩방 → 가짜 코인 거래소)",
    "C02": "투자 리딩방 (증권사 비서 사칭, 밴드방, AI 추천주)",
    "C03": "로맨스 (딥페이크, 투자 강의 → 위탁거래)",
    "C04": "로맨스 (코인 연애 적금, 구매대행 부업)",
    "C05": "유명인 사칭 로맨스 (배우 사칭, 발급비·억류·만남 비용)",
    "C06": "부업·팀미션 (영상 조회 → 코인 버튼 미션, 위약금)",
    "C07": "부업·팀미션 (리뷰 알바, 단계별 고가 구매)",
    "C08": "가족 사칭 (액정 파손, 원격제어 앱)",
    "C09": "지인 사칭 (좀비폰, 급전 차용)",
    "C10": "잘못 보낸 문자 → 공유숙박 투자 (폰지)",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=os.path.join(ROOT, "data", "eval", "holdout_v2", "source_sealed.md"))
    ap.add_argument("--out", default=os.path.join(ROOT, "data", "eval", "holdout_v2"))
    a = ap.parse_args()

    raw = open(a.src, "rb").read()
    h = hashlib.sha256(raw).hexdigest()
    if h != SEALED_SHA256:
        sys.exit(f"[멈춤] SHA-256이 봉인 기록과 다릅니다: {h}")
    text = raw.decode("utf-8")

    block = re.search(r"```csv\n(.*?)\n```", text, re.S)
    if not block:
        sys.exit("[멈춤] CSV 블록을 찾지 못했습니다")
    lines = [re.sub(r'(\\\[\d+\\\])+$', "", l.rstrip()) for l in block.group(1).split("\n")]
    rows = list(csv.DictReader(io.StringIO("\n".join(lines))))
    bad = [r for r in rows if None in r or len(r) != 9]
    if bad:
        sys.exit(f"[멈춤] 칸 수가 맞지 않는 줄: {bad[:2]}")

    # 사례 목록 표에서 출처
    src = {}
    for m in re.finditer(r"^\| (C\d\d) \| ([^|]+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \|$", text, re.M):
        src[m.group(1)] = {"type_raw": m.group(2).strip(), "title": m.group(3).strip(),
                           "url": m.group(4).strip(), "published": re.sub(r"\\\[\d+\\\]", "", m.group(5)).strip()}

    by_case = {}
    for r in rows:
        by_case.setdefault(r["case"], []).append(r)

    os.makedirs(a.out, exist_ok=True)
    total = voice = 0
    for cid, ms in by_case.items():
        ms.sort(key=lambda r: int(r["seq"]))
        # 2. 1:1 방을 상대마다 나눔
        def kind(room):
            return "dm" if room in ("dm", "kakao_dm") else room
        rooms = []
        for i, r in enumerate(ms):
            k = kind(r["room"])
            if k != "dm":
                rooms.append({"live_chat": "group_live"}.get(r["room"], r["room"]))
                continue
            if r["is_user"] != "true":
                rooms.append(f"dm_{r['sender']}")
                continue
            prev = next((ms[j]["sender"] for j in range(i - 1, -1, -1)
                         if kind(ms[j]["room"]) == "dm" and ms[j]["is_user"] != "true"), None)
            nxt = next((ms[j]["sender"] for j in range(i + 1, len(ms))
                        if kind(ms[j]["room"]) == "dm" and ms[j]["is_user"] != "true"), None)
            rooms.append(f"dm_{prev or nxt or '상대'}")
        s = src.get(cid, {})
        meta = {"type": "meta", "case_id": f"holdout_{cid}", "label": "scam", "scam_type": TYPES.get(cid, s.get("type_raw", "")),
                "source": {"title": s.get("title", ""), "url": s.get("url", ""), "published": s.get("published", "")},
                "made_by": "다른 세션 (Claude, 프로젝트 밖, 기억 끔) — docs/holdout_v2.md",
                "sealed_sha256": SEALED_SHA256,
                "conversion": "tools/scam/import_holdout.py (결정 26)"}
        path = os.path.join(a.out, f"holdout_{cid}.jsonl")
        with open(path, "w", encoding="utf-8") as f:
            f.write(json.dumps(meta, ensure_ascii=False) + "\n")
            for r, room in zip(ms, rooms):
                m = {"type": "message", "seq": int(r["seq"]), "room": room, "room_original": r["room"],
                     "sender": r["sender"], "is_user": r["is_user"] == "true", "day": int(r["day"]),
                     "text": r["text"], "provenance": r["provenance"], "source_note": r["source_note"]}
                if r["room"] in ("call", "video"):
                    m["channel"] = "voice"
                    voice += 1
                f.write(json.dumps(m, ensure_ascii=False) + "\n")
                total += 1
        print(f"{os.path.basename(path)}: 메시지 {len(ms)}개, 방 {sorted(set(rooms))}")
    print(f"사례 {len(by_case)}건, 메시지 {total}개 (전화·영상 {voice}개는 channel=voice)")


if __name__ == "__main__":
    main()
