#!/usr/bin/env python3
"""
KorCCVi v2 전사문 → 재생 평가 형식(jsonl) 변환 + 묶음 단위 나누기 (결정 28, docs/v3_plan.md 1단계).

사용법
  py tools/korccvi/import_calls.py --korccvi <Korean_Voice_Phishing_Detection 폴더> \
      --out <저장소 밖 폴더> [--split-out data/eval/korccvi_split_ids.csv] [--seed 20261027]

입력: 저장소 Multimodal/data/transcripts/{vishing,non_vishing}/*.json (CLOVA 전사, 화자 구분)
      Multimodal/data/fss_source_file_mapping.csv (사기 통화 → 금감원 원본 파일)

결과
  <out>/{train,dev,test}/korccvi_<call_id>.jsonl   대화 원문 (저장소에 넣지 않음, 재배포 금지)
  --split-out CSV                                   call_id, label, group, split, kind, n_speakers, scammer, n_segments
                                                    (ID와 숫자만 → 저장소에 넣음. --split-out 없이 돌리면 기존 CSV와 같은지만 확인)

규칙
  - 메시지 = 전사 구간(segment) 하나. 빈 구간은 뺌. seq는 1부터.
  - 사기 통화: 화자가 둘 이상이면 사기범 = 상담·수사 말투 낱말(ROLE_WORDS) 수가 가장 많은 화자, 같으면 글자 수가
    많은 화자 → "상대"(is_user=false), 나머지 화자 → "나". 글자 수만 쓰면 474건 중 25건에서 낱말 기준과 갈렸고,
    직접 본 4건(21·427·18·413)은 모두 낱말 기준이 맞았음 (피해자가 따지느라 더 길게 말한 통화).
    화자가 하나뿐이면(화자 구분 실패) 모두 "상대". scammer 칸에 "single"로 기록.
  - 일반 통화: is_user를 비워 둠 → 평가기가 화자마다 한 번씩 "나"로 놓고 돌림 (결정 23).
  - 묶음: 같은 금감원 원본 파일에서 나온 통화, 그리고 글자 5-gram **포함도**(작은 쪽 5-gram 중 큰 쪽에도 있는 비율)
    ≥ 0.45인 통화를 하나로 묶음 (union-find). 금감원 공개본에는 긴 녹음의 일부를 잘라 따로 올린 것이 많아
    (예: 225자 통화가 8,867자 통화 안에 그대로 있음) 자카드 유사도로는 못 잡음. 0.45~0.65 구간에는 같은 사기범
    ("○○지검 김○○ 수사관")의 다른 통화가 많아 함께 묶음. 일반 통화도 같은 규칙.
  - 나누기: 라벨·유형(kind)별로 묶음을 시드 고정으로 섞어 묶음 단위 70/15/15 (통화 수 기준으로 채움).
  - 유형(kind, 사기만): 기관 사칭 / 대출 / 기타 — 키워드로 정한 나누기용 근사치 (정답 라벨 아님).
"""
import argparse
import csv
import hashlib
import json
import os
import random
import re
import sys
from collections import defaultdict

SPLITS = (("train", 0.70), ("dev", 0.15), ("test", 0.15))
SIM = 0.45  # 작은 쪽 5-gram 중 큰 쪽에도 있는 비율 (포함도)
KIND_RULES = (("기관 사칭", r"검찰|검사|수사관|경찰|금융감독원|금감원|사건번호|명의도용|대포통장|피의자|피해자로"),
              ("대출", r"대출|저금리|대환|한도|상환|신용등급"))
ROLE_WORDS = (r"고객님|수사관|검찰|지검|본인 명의|확인차|연락드|말씀드리|하셔야|해 주셔야|해주셔야|저희|담당|대출|금리|"
              r"이체|송금|계좌|협조|사건")
FIELDS = ["call_id", "label", "group", "split", "kind", "n_speakers", "scammer", "n_segments"]


def load_calls(root):
    base = os.path.join(root, "Multimodal", "data", "transcripts")
    calls = []
    for sub, label in (("vishing", "scam"), ("non_vishing", "normal")):
        d = os.path.join(base, sub)
        if not os.path.isdir(d):
            sys.exit(f"[오류] 폴더 없음: {d}")
        for f in sorted(os.listdir(d)):
            if not f.endswith(".json"):
                continue
            with open(os.path.join(d, f), encoding="utf-8") as fh:
                j = json.load(fh)
            segs = []
            for s in j.get("segments", []):
                t = (s.get("textEdited") or s.get("text") or "").strip()
                if t:
                    segs.append((str(s["speaker"]["label"]), t))
            if segs:
                calls.append({"id": f[:-5], "label": label, "segs": segs})
    return calls


def source_map(root):
    p = os.path.join(root, "Multimodal", "data", "fss_source_file_mapping.csv")
    with open(p, encoding="utf-8-sig", newline="") as f:
        return {r["manifest_file"].rsplit(".", 1)[0]: r["fss_source_file"] for r in csv.DictReader(f)}


def shingles(text, n=5):
    t = re.sub(r"\s+", "", text)
    return {t[i:i + n] for i in range(max(1, len(t) - n + 1))}


class UF:
    def __init__(self, items):
        self.p = {x: x for x in items}

    def find(self, x):
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a, b):
        a, b = self.find(a), self.find(b)
        if a != b:
            self.p[max(a, b)] = min(a, b)


def kind_of(text):
    for k, pat in KIND_RULES:
        if re.search(pat, text):
            return k
    return "기타"


def build(args):
    calls = load_calls(args.korccvi)
    src = source_map(args.korccvi)
    by_id = {c["id"]: c for c in calls}
    for c in calls:
        chars, words = defaultdict(int), defaultdict(int)
        for sp, t in c["segs"]:
            chars[sp] += len(t)
            words[sp] += len(re.findall(ROLE_WORDS, t))
        c["n_speakers"] = len(chars)
        if c["label"] == "scam":
            c["scammer"] = max(sorted(chars), key=lambda s: (words[s], chars[s])) if len(chars) > 1 else "single"
            c["kind"] = kind_of(" ".join(t for _, t in c["segs"]))
        else:
            c["scammer"], c["kind"] = "", ""
        c["sh"] = shingles(" ".join(t for _, t in c["segs"]))

    uf = UF(list(by_id))
    first_by_src = {}
    for c in calls:
        s = src.get(c["id"]) if c["label"] == "scam" else None
        if s:
            if s in first_by_src:
                uf.union(c["id"], first_by_src[s])
            else:
                first_by_src[s] = c["id"]
    n_sim = 0
    for lab in ("scam", "normal"):
        cs = [c for c in calls if c["label"] == lab]
        for i in range(len(cs)):
            a = cs[i]["sh"]
            for k in range(i + 1, len(cs)):
                b = cs[k]["sh"]
                small, big = (a, b) if len(a) < len(b) else (b, a)
                if len(small & big) >= SIM * len(small):
                    uf.union(cs[i]["id"], cs[k]["id"])
                    n_sim += 1
    groups = defaultdict(list)
    for c in calls:
        groups[uf.find(c["id"])].append(c)

    rng = random.Random(args.seed)
    strata = defaultdict(list)
    for gid, members in sorted(groups.items()):
        lab = members[0]["label"]
        if any(m["label"] != lab for m in members):
            sys.exit(f"[오류] 묶음 {gid}에 사기·일반이 섞임")
        kind = members[0]["kind"] if lab == "scam" else ""
        strata[(lab, kind)].append((gid, members))
    for key in sorted(strata):
        gs = strata[key]
        rng.shuffle(gs)
        total = sum(len(m) for _, m in gs)
        done, si = 0, 0
        bounds = []
        acc = 0.0
        for _, frac in SPLITS:
            acc += frac
            bounds.append(acc * total)
        for gid, members in gs:
            while si < len(SPLITS) - 1 and done >= bounds[si]:
                si += 1
            for m in members:
                m["split"], m["group"] = SPLITS[si][0], gid
            done += len(members)
    return calls, groups, n_sim


def write_calls(calls, out):
    for c in calls:
        d = os.path.join(out, c["split"])
        os.makedirs(d, exist_ok=True)
        cid = f"korccvi_{c['id']}"
        meta = {"type": "meta", "case_id": cid, "label": c["label"], "scam_type": c["kind"] or "일반 통화",
                "source": "KorCCVi v2 (금감원 공개 사기 통화 / AI-Hub 저품질 전화망) — 재배포 금지",
                "speaker_type": "다자간" if c["n_speakers"] > 2 else "1:1",
                "conversion": "tools/korccvi/import_calls.py (결정 28)"}
        with open(os.path.join(d, cid + ".jsonl"), "w", encoding="utf-8") as f:
            f.write(json.dumps(meta, ensure_ascii=False) + "\n")
            for i, (sp, t) in enumerate(c["segs"], 1):
                row = {"type": "message", "seq": i, "room": "call", "sender": f"화자{sp}", "text": t}
                if c["label"] == "scam":
                    row["is_user"] = not (c["scammer"] == "single" or sp == c["scammer"])
                    row["sender"] = "나" if row["is_user"] else "상대"
                f.write(json.dumps(row, ensure_ascii=False) + "\n")


def split_rows(calls):
    return sorted(({"call_id": c["id"], "label": c["label"], "group": c["group"], "split": c["split"], "kind": c["kind"],
                    "n_speakers": c["n_speakers"], "scammer": c["scammer"], "n_segments": len(c["segs"])} for c in calls),
                  key=lambda r: (r["label"], r["call_id"]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--korccvi", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--split-out")
    ap.add_argument("--check", help="기존 split CSV와 같은지 확인 (집 PC에서 재현할 때)")
    ap.add_argument("--seed", type=int, default=20261027)
    args = ap.parse_args()
    repo = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    out = os.path.abspath(args.out)
    try:
        inside = os.path.commonpath([repo, out]) == repo
    except ValueError:  # 윈도에서 드라이브가 다름 → 저장소 밖
        inside = False
    if inside:
        sys.exit("[멈춤] --out이 저장소 안입니다. 원문은 재배포 금지라 저장소 밖에 둡니다.")
    calls, groups, n_sim = build(args)
    write_calls(calls, args.out)
    rows = split_rows(calls)
    if args.split_out:
        with open(args.split_out, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
            w.writeheader()
            w.writerows(rows)
        with open(args.split_out, "rb") as f:
            print("split CSV SHA-256:", hashlib.sha256(f.read()).hexdigest())
    if args.check:
        with open(args.check, encoding="utf-8", newline="") as f:
            old = [dict(r) for r in csv.DictReader(f)]
        new = [{k: str(v) for k, v in r.items()} for r in rows]
        if old != new:
            sys.exit("[오류] 나누기 결과가 기존 CSV와 다릅니다 (입력 파일이나 스크립트가 다름)")
        print("기존 split CSV와 같음")
    cnt = defaultdict(int)
    for r in rows:
        cnt[(r["label"], r["split"])] += 1
    multi = sum(1 for g in groups.values() if len(g) > 1)
    print(f"통화 {len(rows)}개, 묶음 {len(groups)}개 (2개 이상 묶인 것 {multi}개, 유사도로 이은 쌍 {n_sim}개)")
    for lab in ("scam", "normal"):
        print(lab, {s: cnt[(lab, s)] for s, _ in SPLITS})
    print("원문 →", os.path.abspath(args.out))


if __name__ == "__main__":
    main()
