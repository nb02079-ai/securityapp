#!/usr/bin/env python3
"""
소형 한국어 인코더 미세조정 (docs/v3_plan.md 3단계). 이진 분류: 지금까지의 상대 메시지가 사기 대화의 것인가.

  py tools/model/train.py --train train.jsonl --dev dev.jsonl --out <모델 폴더> \
      [--model monologg/koelectra-small-v3-discriminator] [--epochs 3] [--batch 32] [--lr 5e-5] [--max-len 256] [--smoke]

- 글이 길면 앞쪽을 자름 (truncation_side=left, 최근 말을 남김)
- 손실: 사기/일반 예시 수 차이를 가중치로 맞춤
- 에포크마다 개발 예시 AUC를 적고, AUC가 가장 높은 에포크를 <out>/best 에 저장
- --smoke: 예시 2,000개·에포크 1로 빠르게 돌려 설치·코드 점검만
"""
import argparse
import json
import math
import os
import random
import time


def read(path, limit=None, seed=0):
    with open(path, encoding="utf-8") as f:
        rows = [json.loads(l) for l in f if l.strip()]
    if limit and len(rows) > limit:
        rows = random.Random(seed).sample(rows, limit)
    return rows


def auc(scores, labels):
    pairs = sorted(zip(scores, labels))
    pos = sum(labels)
    neg = len(labels) - pos
    if not pos or not neg:
        return float("nan")
    rank_sum, i = 0.0, 0
    while i < len(pairs):
        j = i
        while j < len(pairs) and pairs[j][0] == pairs[i][0]:
            j += 1
        avg = (i + j + 1) / 2  # 같은 점수는 평균 순위
        rank_sum += avg * sum(l for _, l in pairs[i:j])
        i = j
    return (rank_sum - pos * (pos + 1) / 2) / (pos * neg)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--train", required=True)
    ap.add_argument("--dev", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--model", default="monologg/koelectra-small-v3-discriminator")
    ap.add_argument("--epochs", type=int, default=3)
    ap.add_argument("--batch", type=int, default=32)
    ap.add_argument("--lr", type=float, default=5e-5)
    ap.add_argument("--max-len", type=int, default=256)
    ap.add_argument("--seed", type=int, default=20261028)
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()

    import torch
    from torch.utils.data import DataLoader
    from transformers import AutoModelForSequenceClassification, AutoTokenizer, get_linear_schedule_with_warmup

    random.seed(a.seed)
    torch.manual_seed(a.seed)
    dev_name = "cuda" if torch.cuda.is_available() else "cpu"
    print("장치:", dev_name, torch.cuda.get_device_name(0) if dev_name == "cuda" else "")
    lim = 2000 if a.smoke else None
    train = read(a.train, lim, a.seed)
    dev = read(a.dev, 500 if a.smoke else None, a.seed)
    epochs = 1 if a.smoke else a.epochs
    pos = sum(r["label"] for r in train)
    neg = len(train) - pos
    if not pos or not neg:
        raise SystemExit("[오류] 학습 예시에 사기·일반이 모두 있어야 합니다")
    print(f"학습 예시 {len(train)} (사기 {pos}, 일반 {neg}), 개발 예시 {len(dev)}")

    tok = AutoTokenizer.from_pretrained(a.model)
    tok.truncation_side = "left"
    model = AutoModelForSequenceClassification.from_pretrained(a.model, num_labels=2).to(dev_name)

    def collate(batch):
        enc = tok([r["text"] for r in batch], truncation=True, max_length=a.max_len, padding=True, return_tensors="pt")
        enc["labels"] = torch.tensor([r["label"] for r in batch])
        return enc

    tl = DataLoader(train, batch_size=a.batch, shuffle=True, collate_fn=collate)
    dl = DataLoader(dev, batch_size=a.batch * 2, shuffle=False, collate_fn=collate)
    opt = torch.optim.AdamW(model.parameters(), lr=a.lr, weight_decay=0.01)
    steps = epochs * len(tl)
    sch = get_linear_schedule_with_warmup(opt, int(0.06 * steps), steps)
    weight = torch.tensor([len(train) / (2 * neg), len(train) / (2 * pos)], dtype=torch.float, device=dev_name)
    lossf = torch.nn.CrossEntropyLoss(weight=weight)
    use_amp = dev_name == "cuda"
    scaler = torch.amp.GradScaler("cuda", enabled=use_amp)

    os.makedirs(a.out, exist_ok=True)
    best, log = -1.0, []
    for ep in range(1, epochs + 1):
        model.train()
        t0, total = time.time(), 0.0
        for i, b in enumerate(tl, 1):
            labels = b.pop("labels").to(dev_name)
            b = {k: v.to(dev_name) for k, v in b.items()}
            with torch.autocast(device_type="cuda", dtype=torch.float16, enabled=use_amp):
                logits = model(**b).logits
            loss = lossf(logits.float(), labels)
            opt.zero_grad()
            scaler.scale(loss).backward()
            scaler.unscale_(opt)
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            scaler.step(opt)
            scaler.update()
            sch.step()
            total += loss.item()
            if i % 200 == 0 or i == len(tl):
                print(f"  에포크 {ep} {i}/{len(tl)} 손실 {total / i:.4f} ({time.time() - t0:.0f}초)", flush=True)
        model.eval()
        scores, ys = [], []
        with torch.no_grad():
            for b in dl:
                ys += b.pop("labels").tolist()
                b = {k: v.to(dev_name) for k, v in b.items()}
                with torch.autocast(device_type="cuda", dtype=torch.float16, enabled=use_amp):
                    p = torch.softmax(model(**b).logits.float(), -1)[:, 1]
                scores += p.tolist()
        a_ = auc(scores, ys)
        log.append({"epoch": ep, "train_loss": total / len(tl), "dev_auc": a_})
        print(f"에포크 {ep}: 학습 손실 {total / len(tl):.4f}, 개발 예시 AUC {a_:.4f}")
        if not math.isnan(a_) and a_ > best:
            best = a_
            model.save_pretrained(os.path.join(a.out, "best"))
            tok.save_pretrained(os.path.join(a.out, "best"))
    with open(os.path.join(a.out, "train_log.json"), "w", encoding="utf-8") as f:
        json.dump({"args": vars(a), "log": log, "best_dev_auc": best}, f, ensure_ascii=False, indent=1)
    print(f"가장 좋은 개발 AUC {best:.4f} → {os.path.join(a.out, 'best')}")


if __name__ == "__main__":
    main()
