#!/usr/bin/env python3
"""
모델 고정 기록 (평가 세트를 열기 전에 실행, plan.md 7.2 / 결정 32).
모델 파일은 저장소 밖에 두고, 파일마다 SHA-256과 문턱·학습 설정을 저장소에 남긴다.

  py tools/model/freeze.py --model <모델 폴더>\best --threshold 0.843446001 --train-log <모델 폴더>\train_log.json \
      --name model-v2 --out docs/results/model-v2/freeze.json
  평가 때 확인: py tools/model/freeze.py --verify docs/results/model-v2/freeze.json --model <모델 폴더>\best
"""
import argparse
import hashlib
import json
import os
import sys


def digest(folder):
    out = {}
    for f in sorted(os.listdir(folder)):
        p = os.path.join(folder, f)
        if os.path.isfile(p):
            h = hashlib.sha256()
            with open(p, "rb") as fh:
                for chunk in iter(lambda: fh.read(1 << 20), b""):
                    h.update(chunk)
            out[f] = h.hexdigest()
    if not out:
        sys.exit(f"[오류] 모델 파일이 없습니다: {folder}")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--threshold", type=float)
    ap.add_argument("--train-log")
    ap.add_argument("--name")
    ap.add_argument("--out")
    ap.add_argument("--verify")
    a = ap.parse_args()
    files = digest(a.model)
    if a.verify:
        with open(a.verify, encoding="utf-8") as f:
            rec = json.load(f)
        if rec["files"] != files:
            bad = sorted(set(rec["files"].items()) ^ set(files.items()))
            sys.exit(f"[오류] 고정한 모델과 다릅니다: {bad[:4]}")
        print(f"고정한 모델과 같음 ({rec['name']}, 문턱 {rec['threshold']})")
        return
    if a.threshold is None or not a.name or not a.out:
        sys.exit("[오류] --threshold, --name, --out 이 필요합니다")
    rec = {"name": a.name, "threshold": a.threshold, "files": files,
           "threshold_rule": "개발 세트에서 KorCCVi 일반 통화·금융 콜센터가 각각 오탐 3% 이하가 되는 가장 낮은 값 (결정 29)"}
    if a.train_log:
        with open(a.train_log, encoding="utf-8") as f:
            log = json.load(f)
        args = dict(log.get("args", {}))
        for k in ("train", "dev", "out"):
            args.pop(k, None)  # 개인 PC 경로는 남기지 않음
        rec["train"] = {"args": args, "log": log.get("log"), "best_dev_auc": log.get("best_dev_auc")}
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(rec, f, ensure_ascii=False, indent=1)
    print(f"고정 기록 → {a.out}")
    for k, v in files.items():
        print(f"  {k}: {v[:16]}…")


if __name__ == "__main__":
    main()
