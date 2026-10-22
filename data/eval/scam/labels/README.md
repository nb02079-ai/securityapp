# 사기 평가 세트 최종 라벨 (정답지)

재구성 사기 10건(`../scamNN_*.jsonl`)의 상대방 메시지 122개에 대한 최종 라벨입니다. 작업 2단계 엔진 평가의 정답으로 씁니다.

| 파일 | 내용 |
|---|---|
| `final_messages.csv` | 메시지마다 신호(`;`로 구분, 기준표 v2.1 코드)·단계, 그 값을 정한 방법(다수결 / 판정) |
| `final_points.csv` | 사례마다 첫 금전 권유·첫 송금 의사 직전·첫 송금 직전 메시지 번호, 송금 여부 |

- 기준: [라벨 기준표 v2.1](../../../../docs/labeling/03_label_guide.md)
- 만든 방법: 서로 다른 회사 모델 3개(Grok·Claude·ChatGPT)가 기준표 v2로 붙인 라벨의 다수결 + 사용자가 기준표 v2.1 문장을 보고 판정한 41칸 ([06_label_round2.md](../../../../docs/labeling/06_label_round2.md) 4장)
- 라벨러 간 일치: 모델 3개 신호 Fleiss κ 0.82, 단계 κ 0.78, 첫 송금 직전 10건 모두 일치
- 다시 만들기: `python tools/scam/finalize_labels.py data/eval/scam/*.jsonl --shuffle-seed 20261021 --labels docs/labeling/label_results/v2 --adjudication docs/labeling/label_results/v2/adjudication_final.xlsx --out data/eval/scam/labels`
- `seq`는 원래 사례 파일의 메시지 번호입니다 (가림판 번호 C01~C10이 아니라 `case_id`로 적음).
- 평가 때 "결심 전 경고율"의 마감점은 `first_intent_before`와 `first_transfer_before` 중 앞선 쪽입니다 (plan.md 6.1).
