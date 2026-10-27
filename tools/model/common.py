"""분류 모델 공통: 대화 읽기, 관점(누가 "나"인가), 정규화, 접두 글 만들기 (docs/v3_plan.md 3단계)."""
import json
import os
import re

SEP = " | "
MASK = re.compile(r"(?:[OoXx○●*＊]{2,}|0{3,})")
PUNCT = re.compile(r"[^\w\s|#○]")
DIGITS = re.compile(r"\d+")
SPACE = re.compile(r"\s+")


def normalize(text):
    """전사문(KorCCVi)과 입력한 글(콜센터)의 말투 차이를 줄임: 가림 기호 통일, 숫자 → #, 문장부호 제거, 띄어쓰기 정리."""
    t = MASK.sub(" ○ ", text)
    t = DIGITS.sub("#", t)
    t = PUNCT.sub(" ", t)
    t = t.replace("_", " ")
    return SPACE.sub(" ", t).strip().lower()


def load_conv(path):
    with open(path, encoding="utf-8") as f:
        rows = [json.loads(l) for l in f if l.strip()]
    meta = rows[0] if rows[0].get("type") == "meta" else {}
    msgs = [r for r in rows if r.get("type") == "message" or "seq" in r]
    cid = meta.get("case_id") or os.path.splitext(os.path.basename(path))[0]
    label = meta.get("label") or meta.get("kind")
    if label not in ("scam", "normal"):
        raise ValueError(f"{cid}: label 없음")
    src = cid.split("_")[0] if "_" in cid else "other"
    return {"id": cid, "label": label, "source": src, "messages": msgs}


def load_dir(folder):
    out = []
    for root, _, files in os.walk(folder):
        for f in sorted(files):
            if f.endswith(".jsonl"):
                out.append(load_conv(os.path.join(root, f)))
    out.sort(key=lambda c: c["id"])
    return out


def perspectives(conv):
    """앱은 "상대" 메시지만 받음. "나"가 정해진 대화는 관점 하나, 안 정해진 대화(일반 통화·콜센터)는 화자마다 하나 (결정 23).
    반환: [(관점 이름, [상대 메시지 (seq, text), ...])]"""
    msgs = [m for m in conv["messages"] if m.get("channel") != "voice"]
    if any(m.get("is_user") is not None for m in msgs):
        return [("user", [(m["seq"], m["text"]) for m in msgs if m.get("is_user") is not True])]
    speakers = list(dict.fromkeys(m["sender"] for m in msgs))
    if len(speakers) < 2:  # 화자 하나뿐 → 상대 메시지 없음 (경고가 날 수 없음)
        return [(f"as:{s}", []) for s in speakers]
    return [(f"as:{s}", [(m["seq"], m["text"]) for m in msgs if m["sender"] != s]) for s in speakers]


def prefix_text(counterpart, k, max_chars=600):
    """상대 메시지 1..k를 정규화해 이어 붙이고 끝에서 max_chars만 남김 (최근 말이 가장 중요)."""
    t = SEP.join(normalize(x) for _, x in counterpart[:k] if x.strip())
    return t[-max_chars:]
