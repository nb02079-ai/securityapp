#!/usr/bin/env python3
"""
AI-Hub「민원(콜센터) 질의-응답 데이터」금융/보험 → 재생 평가 형식(jsonl) 변환 + 나누기 (결정 28, docs/v3_plan.md 1단계).

사용법
  py tools/aihub/import_callcenter.py --input <금융보험 라벨링데이터 폴더(zip 또는 json)> [--input ...] \
      --out <저장소 밖 폴더> [--split-out data/eval/callcenter_split_ids.csv | --check data/eval/callcenter_split_ids.csv]

입력: 라벨링데이터의 .zip(안의 .json을 바로 읽음) 또는 풀어 둔 .json. 파일마다 문장 하나가 객체 하나인 목록.
      경로에 "Training"이 있으면 학습용, "Validation"이 있으면 평가용으로 봄 (AI-Hub의 나누기를 그대로 따름).

결과
  <out>/{train,dev,test}/callcenter_<대화셋일련번호>.jsonl   원문 (저장소에 넣지 않음, 재배포 금지)
  split CSV: dialog_id, category, split, n_messages          (ID와 숫자만 → 저장소)

규칙
  - 대화 = 같은 "대화셋일련번호". 메시지 = 문장 하나, "문장번호" 순서. 글은 네 칸(고객질문·상담사질문·고객답변·상담사답변) 중
    비어 있지 않은 것. 빈 문장은 뺌. 메시지 2개 미만인 대화는 뺌.
  - "나"는 정하지 않음 → 평가기가 고객·상담사를 한 번씩 "나"로 놓고 돌림 (결정 23). 보낸 사람 = 화자(고객/상담사).
  - 나누기: AI-Hub Validation → test(봉인). Training → 대화 ID를 시드 고정으로 섞어 85% train / 15% dev.
  - 같은 대화셋일련번호가 두 번 나오면(다른 파일·다른 나누기) 멈춤.
  - 주의: 이 데이터는 사람이 친 글이고 KorCCVi는 음성 전사라 말투가 다름. 모델이 말투로 가르지 않게
    정규화는 모델 쪽에서 하고, 오탐은 출처별로 따로 보고 (docs/korccvi.md, plan.md 5.2.1).
"""
import argparse
import csv
import hashlib
import io
import json
import os
import random
import sys
import zipfile
from collections import defaultdict

TEXT_FIELDS = ("고객질문(요청)", "상담사질문(요청)", "고객답변", "상담사답변")
FIELDS = ["dialog_id", "category", "split", "n_messages"]


def read_json_bytes(b, name):
    for enc in ("utf-8-sig", "cp949"):
        try:
            return json.loads(b.decode(enc))
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
    sys.exit(f"[오류] JSON을 읽을 수 없음: {name}")


def iter_files(paths):
    for p in paths:
        files = [p] if os.path.isfile(p) else sorted(
            os.path.join(r, f) for r, _, fs in os.walk(p) for f in fs)
        for f in files:
            low = f.lower()
            if low.endswith(".zip"):
                with zipfile.ZipFile(f) as z:
                    for info in sorted(z.infolist(), key=lambda i: i.filename):
                        if info.filename.lower().endswith(".json"):
                            yield f + "!" + info.filename, read_json_bytes(z.read(info), info.filename)
            elif low.endswith(".json"):
                with open(f, "rb") as fh:
                    yield f, read_json_bytes(fh.read(), f)


def source_split(path):
    if "Validation" in path or "validation" in path:
        return "test"
    if "Training" in path or "training" in path:
        return "train"
    sys.exit(f"[오류] 경로로 Training/Validation을 알 수 없음: {path}")


def load(paths):
    dialogs = {}
    for path, rows in iter_files(paths):
        if not isinstance(rows, list):
            sys.exit(f"[오류] 목록 형식이 아님: {path}")
        src = source_split(path)
        local = defaultdict(list)
        for r in rows:
            local[str(r["대화셋일련번호"]).strip()].append(r)
        for did, rs in local.items():
            if did in dialogs:
                sys.exit(f"[오류] 대화셋일련번호 중복: {did} ({path})")
            rs.sort(key=lambda r: int(r["문장번호"]))
            msgs = []
            for r in rs:
                t = next((r[k].strip() for k in TEXT_FIELDS if str(r.get(k, "")).strip()), "")
                if t:
                    msgs.append((r["화자"].strip(), t))
            if len(msgs) >= 2:
                dialogs[did] = {"id": did, "category": rs[0]["카테고리"].strip(), "src": src, "msgs": msgs}
    return dialogs


def assign(dialogs, seed):
    train_ids = sorted(d for d, v in dialogs.items() if v["src"] == "train")
    rng = random.Random(seed)
    rng.shuffle(train_ids)
    n_dev = round(len(train_ids) * 0.15)
    dev = set(train_ids[:n_dev])
    for d, v in dialogs.items():
        v["split"] = "test" if v["src"] == "test" else ("dev" if d in dev else "train")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", action="append", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--split-out")
    ap.add_argument("--check")
    ap.add_argument("--seed", type=int, default=20261027)
    args = ap.parse_args()
    repo = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    try:
        inside = os.path.commonpath([repo, os.path.abspath(args.out)]) == repo
    except ValueError:
        inside = False
    if inside:
        sys.exit("[멈춤] --out이 저장소 안입니다. 원문은 재배포 금지라 저장소 밖에 둡니다.")

    dialogs = load(args.input)
    if not dialogs:
        sys.exit("[오류] 읽은 대화가 없음")
    assign(dialogs, args.seed)
    for v in dialogs.values():
        d = os.path.join(args.out, v["split"])
        os.makedirs(d, exist_ok=True)
        cid = f"callcenter_{v['id']}"
        meta = {"type": "meta", "case_id": cid, "label": "normal", "topic": f"금융 콜센터 · {v['category']}",
                "source": "AI-Hub 민원(콜센터) 질의-응답 금융/보험 — 재배포 금지", "speaker_type": "1:1",
                "conversion": "tools/aihub/import_callcenter.py (결정 28)"}
        with open(os.path.join(d, cid + ".jsonl"), "w", encoding="utf-8") as f:
            f.write(json.dumps(meta, ensure_ascii=False) + "\n")
            for i, (sp, t) in enumerate(v["msgs"], 1):
                f.write(json.dumps({"type": "message", "seq": i, "room": "call", "sender": sp, "text": t},
                                   ensure_ascii=False) + "\n")
    rows = sorted(({"dialog_id": v["id"], "category": v["category"], "split": v["split"],
                    "n_messages": str(len(v["msgs"]))} for v in dialogs.values()), key=lambda r: r["dialog_id"])
    if args.split_out:
        with open(args.split_out, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
            w.writeheader()
            w.writerows(rows)
        with open(args.split_out, "rb") as f:
            print("split CSV SHA-256:", hashlib.sha256(f.read()).hexdigest())
    if args.check:
        with open(args.check, encoding="utf-8", newline="") as f:
            if [dict(r) for r in csv.DictReader(f)] != rows:
                sys.exit("[오류] 나누기 결과가 기존 CSV와 다릅니다")
        print("기존 split CSV와 같음")
    cnt = defaultdict(int)
    for r in rows:
        cnt[(r["category"], r["split"])] += 1
    print(f"대화 {len(rows)}개")
    for k in sorted(cnt):
        print(" ", k, cnt[k])
    print("원문 →", os.path.abspath(args.out))


if __name__ == "__main__":
    main()
