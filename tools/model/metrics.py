#!/usr/bin/env python3
"""
탐지율·오탐률 (plan.md 7.2 v3.0). score.py 결과(또는 재생 평가기의 cases.csv·normals.csv)를 읽어 계산.

  문턱 고르기 (개발 세트):  py tools/model/metrics.py --scores dev_scores.csv --pick-fp 0.03 --out dev_report.md
  고정 문턱으로 평가:       py tools/model/metrics.py --scores test_scores.csv --threshold 0.87 \
                               --decisive data/eval/korccvi_labels/final_decisive.csv --out test_report.md
  규칙 엔진·단어 기준선:     py tools/model/metrics.py --kotlin <평가기 --out 폴더> --decisive ... --out ...

정의
  - 일반 대화: 어느 관점에서든 한 번이라도 점수 ≥ 문턱이면 오탐 (결정 23)
  - 사기 대화: 첫 경고 = 점수 ≥ 문턱인 첫 상대 메시지. 첫 결정적 지시 번호가 있으면 그 번호 이하에서 경고해야 탐지,
    none이거나 라벨이 없으면 통화 중 한 번이라도 경고하면 탐지
  - --pick-fp: 일반 대화 오탐이 목표 이하가 되는 가장 낮은 문턱 (탐지율이 가장 높아지는 쪽)
"""
import argparse
import csv
import json
import math
import statistics
from collections import defaultdict


def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def read_scores(paths):
    convs = {}
    for p in paths:
        with open(p, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                c = convs.setdefault(r["conv"], {"label": r["label"], "source": r["source"], "persp": defaultdict(list)})
                if r["seq"]:
                    c["persp"][r["persp"]].append((int(r["seq"]), float(r["score"])))
                else:
                    c["persp"].setdefault(r["persp"], [])
    for c in convs.values():
        for v in c["persp"].values():
            v.sort()
    return convs


def read_decisive(path):
    if not path:
        return {}
    with open(path, encoding="utf-8") as f:
        return {r["call_id"]: (None if r["decisive_seq"] == "none" else int(r["decisive_seq"])) for r in csv.DictReader(f)}


def pick_threshold(convs, target):
    maxima = sorted((max((s for v in c["persp"].values() for _, s in v), default=0.0)
                     for c in convs.values() if c["label"] == "normal"), reverse=True)
    if not maxima:
        raise SystemExit("[오류] 일반 대화가 없어 문턱을 고를 수 없음")
    allowed = math.floor(target * len(maxima) + 1e-9)
    if allowed >= len(maxima):
        return 0.0
    return maxima[allowed] + 1e-9  # 그 대화의 최고점보다 살짝 위 → 그 대화부터는 경고 안 남 (1을 넘으면 경고 없음)


def evaluate(convs, th, decisive):
    res = {"normal": [], "scam": []}
    for cid, c in sorted(convs.items()):
        if c["label"] == "normal":
            warned = any(s >= th for v in c["persp"].values() for _, s in v)
            res["normal"].append({"conv": cid, "source": c["source"], "warned": warned})
        else:
            v = next(iter(c["persp"].values()), [])
            first = next(((i, q) for i, (q, s) in enumerate(v, 1) if s >= th), None)
            dl = decisive.get(cid)
            ok = first is not None and (dl is None or first[1] <= dl)
            res["scam"].append({"conv": cid, "source": c["source"], "first_seq": first[1] if first else None,
                                "first_k": first[0] if first else None, "n": len(v), "deadline": dl,
                                "labeled": cid in decisive, "detected": ok})
    return res


def from_kotlin(folder, method, mode, decisive):
    res = {"normal": [], "scam": []}
    with open(f"{folder}/normals.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["method"] == method and r["mode"] == mode:
                res["normal"].append({"conv": r["id"], "source": r["id"].split("_")[0],
                                      "warned": int(r["warned_perspectives"]) > 0})
    with open(f"{folder}/cases.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["method"] == method and r["mode"] == mode:
                fs = None if r["first_warning"] == "-" else int(r["first_warning"])
                dl = decisive.get(r["case_id"])
                res["scam"].append({"conv": r["case_id"], "source": r["case_id"].split("_")[0], "first_seq": fs,
                                    "first_k": None, "n": int(r["counterpart_messages"]), "deadline": dl,
                                    "labeled": r["case_id"] in decisive,
                                    "detected": fs is not None and (dl is None or fs <= dl)})
    return res


def pct(k, n):
    lo, hi = wilson(k, n)
    return f"{k}/{n} ({100 * k / n:.1f}%, 95% CI {100 * lo:.1f}–{100 * hi:.1f})" if n else "-"


def report(res, title, th):
    sc, no = res["scam"], res["normal"]
    det = sum(r["detected"] for r in sc)
    fp = sum(r["warned"] for r in no)
    lines = [f"# {title}", "", f"- 문턱: {th if th is not None else '(규칙 엔진)'}", "",
             "| 지표 | 값 | 목표 |", "|---|---|---|",
             f"| **탐지율** (사기 대화) | {pct(det, len(sc))} | 90% 이상 |",
             f"| **오탐률** (일반 대화) | {pct(fp, len(no))} | 3% 이하 |"]
    lab = [r for r in sc if r["deadline"] is not None]
    if lab:
        lines.append(f"| 지시가 있는 사기 대화에서 지시 전 경고 | {pct(sum(r['detected'] for r in lab), len(lab))} | (보조) |")
    nolab = [r for r in sc if r["labeled"] and r["deadline"] is None]
    if nolab:
        lines.append(f"| 지시 없는(none) 사기 대화에서 경고 | {pct(sum(r['detected'] for r in nolab), len(nolab))} | (보조) |")
    ks = [r["first_k"] for r in sc if r["detected"] and r["first_k"]]
    if ks:
        rel = [r["first_k"] / r["n"] for r in sc if r["detected"] and r["first_k"] and r["n"]]
        lines.append(f"| 첫 경고 위치 (상대 메시지 몇 번째, 중앙값) | {statistics.median(ks)} (대화 길이의 {100 * statistics.median(rel):.0f}% 지점) | (보조) |")
    lines += ["", "## 출처별 오탐", "", "| 출처 | 오탐 |", "|---|---|"]
    by = defaultdict(list)
    for r in no:
        by[r["source"]].append(r["warned"])
    for s in sorted(by):
        lines.append(f"| {s} | {pct(sum(by[s]), len(by[s]))} |")
    lines += ["", "## 출처별 탐지", "", "| 출처 | 탐지 |", "|---|---|"]
    by = defaultdict(list)
    for r in sc:
        by[r["source"]].append(r["detected"])
    for s in sorted(by):
        lines.append(f"| {s} | {pct(sum(by[s]), len(by[s]))} |")
    return "\n".join(lines) + "\n", {"threshold": th, "detected": det, "scams": len(sc), "fp": fp, "normals": len(no)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scores", action="append")
    ap.add_argument("--kotlin")
    ap.add_argument("--method", default="행위 + 흐름")
    ap.add_argument("--mode", default="상대만")
    ap.add_argument("--threshold", type=float)
    ap.add_argument("--pick-fp", type=float)
    ap.add_argument("--decisive")
    ap.add_argument("--title", default="탐지율·오탐률")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    dec = read_decisive(a.decisive)
    if a.kotlin:
        res, th = from_kotlin(a.kotlin, a.method, a.mode, dec), None
    else:
        if not a.scores:
            raise SystemExit("[오류] --scores 또는 --kotlin")
        convs = read_scores(a.scores)
        if (a.threshold is None) == (a.pick_fp is None):
            raise SystemExit("[오류] --threshold 와 --pick-fp 중 하나만")
        th = a.threshold if a.threshold is not None else pick_threshold(convs, a.pick_fp)
        res = evaluate(convs, th, dec)
    if dec:
        missing = [k for k in dec if k not in {r["conv"] for r in res["scam"]}]
        if missing:
            raise SystemExit(f"[오류] 라벨은 있는데 점수가 없는 사기 대화 {len(missing)}개 (예: {missing[:3]})")
    text, summ = report(res, a.title, th)
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(text)
    with open(a.out.rsplit(".", 1)[0] + ".json", "w", encoding="utf-8") as f:
        json.dump({"summary": summ, "rows": res}, f, ensure_ascii=False)
    print(text)


if __name__ == "__main__":
    main()
