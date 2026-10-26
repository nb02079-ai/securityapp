# 새 평가 세트(holdout_v2) 라벨링

- 날짜: 2026-10-27
- 대상: `data/eval/holdout_v2/holdout_C01~C10.jsonl` (사례 10건, 메시지 168개, 그중 상대 메시지 107개)
- 기준표: [03_label_guide.md](03_label_guide.md) v2.2 (바꾸지 않음)
- 진행 방식: 기존 평가 세트 2차 라벨링([04](04_labeling_prompt.md), [06](06_label_round2.md))과 같습니다. 모델 3개가 전부 붙이고, 갈린 곳만 사용자가 판정합니다.

## 라벨러

| 라벨러 | 이유 |
|---|---|
| ChatGPT, Gemini, Grok (각각 기억을 끈 새 대화) | 이 세트는 Claude(다른 세션)가 재구성했습니다. "라벨은 작성자가 아닌 쪽이"(plan.md 5.2) 원칙에 따라 **Claude는 라벨러에서 뺍니다** (결정 26). |
| 사용자 | 모델끼리 갈린 칸과 금전 지점만 판정 |

## 준비 (이 세션에서 만들어 전달함, 저장소 밖)

```
python tools/scam/make_blind.py       data/eval/holdout_v2/*.jsonl --out "<저장소 밖>/label_in"  --shuffle-seed 20261027
python tools/scam/make_label_sheet.py data/eval/holdout_v2/*.jsonl --out "<저장소 밖>/label_all" --shuffle-seed 20261027
```

- 라벨러에게 주는 것: `blind_cases.md`, `03_label_guide.md`, `label_messages.csv`(107줄), `label_points.csv`(10줄)
- 라벨러에게 주지 않는 것: `blind_key.csv`(번호표), 원래 사례 파일, 이 저장소
- 가림판의 "전화 통화"·"영상통화" 방은 녹취입니다. 앱에는 오지 않아 평가기가 엔진에 넣지 않지만, 라벨러는 흐름을 봐야 하므로 보여 주고 라벨도 붙입니다.

## 지시문 (모델마다 같은 것)

```
첨부한 대화 기록 파일(blind_cases.md)에는 10개의 대화 기록(C01~C10)이 있습니다. 모두 실제 금융 사기 사례를 바탕으로 재구성한 것이고, "나"가 피해자입니다.
첨부한 03_label_guide.md(라벨 기준표)에 따라 라벨을 붙여 주세요.

[규칙]
- 기준표의 정의와 "붙이지 않는 경우"를 그대로 따르세요. 기준표에 없는 신호 코드를 만들지 마세요.
- 웹 검색을 하거나 원래 기사·사건을 추측해서 찾지 마세요. 표에 보이는 것만 보세요.
- 상대방 메시지 하나도 빠뜨리지 마세요. 신호가 없는 메시지는 signals 칸을 비우되 stage와 confidence는 채우세요.
- "전화 통화"·"영상통화" 방의 메시지도 같은 기준으로 붙이세요.
- 확신이 없으면 confidence를 "낮음"으로 하고 note에 고민한 다른 신호를 적으세요.
- 금전 지점 세 개(기준표 4장)를 모두 채우세요. "보냈어요"가 돈인지, "해 볼게요"가 의사 표현인지 송금인지 반드시 구분하세요.

[출력]
첨부한 label_messages.csv와 label_points.csv의 빈 칸을 채워 같은 이름의 CSV 파일 두 개로 돌려주세요.
- 줄을 추가하거나 지우지 말고, case·seq·room·sender·text 칸은 바꾸지 마세요.
- 모든 사례를 끝낸 뒤, 기준표로 판단하기 어려웠던 점을 5줄 이내로 따로 적어 주세요.
```

## 받은 뒤
1. 형식 확인: messages 107줄, points 10줄, 신호 코드가 기준표에 있는지
2. `tools/scam/agreement.py`로 일치율(κ)과 갈린 곳 목록
3. 갈린 칸과 금전 지점만 사용자가 판정 (`make_adjudication_xlsx.py`)
4. `finalize_labels.py`로 최종 라벨 → `data/eval/holdout_v2/labels/`
5. 평가기를 `--eval-set`으로 **한 번** 실행 (engine-v1.1, 비교용으로 engine-v1도 같은 날 함께)
