#!/usr/bin/env python3
"""
엔진 표현 목록(Lexicon.kt)이 평가 세트 문장에서 옮겨 온 것이 아닌지 검사한다 (docs/stage2_engine_design.md 1장).

사용법
  python tools/scam/check_lexicon_leak.py [--min 5]

방법
  Lexicon.kt의 문자열에서 정규식 기호를 기준으로 낱말 조각을 뽑고, 공백·기호를 뺀 평가 문장(data/eval/scam/*.jsonl)
  안에 그 조각이 그대로 들어 있는지 본다. --min 글자 이상인 조각만 본다 (짧은 낱말은 어디에나 있어서).
  겹친다고 곧 문제는 아니다 ("계좌번호"처럼 기준표에도 있는 낱말). 결과를 보고 사람이 판단해 기록한다.
  종료 코드는 항상 0 — 자동으로 막지 않고 목록을 남기는 도구.
"""
import argparse
import glob
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
LEX = os.path.join(ROOT, "engine", "src", "main", "kotlin", "securityapp", "engine", "acts", "Lexicon.kt")
EVAL = os.path.join(ROOT, "data", "eval", "scam", "*.jsonl")
GUIDE = os.path.join(ROOT, "docs", "labeling", "03_label_guide.md")


def compact(s):
    return re.sub(r"[\s.,·ㆍ\-_~*^'\"`|/\\:;!?()\[\]{}<>+=#@&]", "", s).lower()


def fragments(src):
    out = set()
    for lit in re.findall(r'"((?:[^"\\]|\\.)*)"', src):
        if "\\" in lit and not re.search(r"[가-힣]", lit):
            continue
        # 정규식 기호로 쪼개 낱말 조각만
        for piece in re.split(r"[()|?*+\[\]{}.^$\\]|\{\d+,?\d*\}", lit):
            piece = re.sub(r"[0-9]+", "", piece) if piece.isdigit() else piece
            if re.search(r"[가-힣a-z]", piece):
                out.add(piece)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min", type=int, default=5)
    args = ap.parse_args()
    with open(LEX, encoding="utf-8") as f:
        frags = {x for x in fragments(f.read()) if len(x) >= args.min}
    texts = []
    for path in sorted(glob.glob(EVAL)):
        with open(path, encoding="utf-8") as f:
            for line in f:
                o = json.loads(line)
                if o.get("type") != "meta":
                    texts.append((os.path.basename(path), o["seq"], compact(o["text"])))
    guide = compact(open(GUIDE, encoding="utf-8").read()) if os.path.exists(GUIDE) else ""
    hits = []
    for fr in sorted(frags):
        where = [f"{p.split('_')[0]}#{s}" for p, s, t in texts if fr in t]
        if where:
            hits.append((fr, fr in guide, where))
    print(f"표현 조각 {len(frags)}개 (길이 {args.min}자 이상) 중 평가 문장에 들어 있는 것 {len(hits)}개")
    for fr, in_guide, where in hits:
        tag = "기준표에도 있음" if in_guide else "기준표에 없음 — 확인 필요"
        print(f"  {fr}  [{tag}]  {', '.join(where[:6])}{' …' if len(where) > 6 else ''}")


if __name__ == "__main__":
    main()
