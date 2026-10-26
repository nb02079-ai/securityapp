# 개발 세트 (규칙을 만들고 고칠 때만 쓰는 데이터)

평가에는 쓰지 않습니다 ([docs/stage2_engine_design.md](../../docs/stage2_engine_design.md) 1·2장).

## 합성 대화 (`synthetic/`, 원본 CSV는 `raw/`)

| 모델 | 원본 | 사례 | 메시지 | 맡은 유형 |
|---|---|---|---|---|
| Claude (프로젝트 밖 새 대화) | `raw/dev_claude.csv` | 사기 7 + 정상 4 | 247 | 공모주 내부 청약, 유명인 사칭 코인, 재택 부업 선입금 등 |
| ChatGPT (임시 채팅) | `raw/dev_chatgpt.csv` | 사기 7 + 정상 4 | 150 | 코인 리딩방, 해외 물품 배송비 대납, 가족 사칭 등 |
| Gemini (Grok 대신) | `raw/dev_gemini.csv` | 사기 7 + 정상 4 | 183 | 주식 리딩방 유료 전환, 군인·의사 사칭 로맨스, 공공기관 사칭 환급 등 |

- 2026-10-23 생성. 지시문: [docs/dev/01_synthetic_prompt.md](../../docs/dev/01_synthetic_prompt.md). 모델에게 평가 사례·가림판·라벨 기준표를 주지 않았습니다.
- Grok은 답변이 나오지 않아 같은 지시문으로 Gemini에 맡겼습니다.
- 평가 사례 문장과 10자 이상 겹치는 곳: 없음 (받은 뒤 검사)
- 라벨은 붙이지 않습니다. 엔진이 어느 메시지에서 어떤 신호·경고를 냈는지만 봅니다.
- 변환: `python tools/dev/import_synthetic.py data/dev/raw/dev_<모델>.csv --model <모델>`

## 합성 대화 2차 (`synthetic2/`, 작업 4-1)
- 지시문: [docs/dev/05_synthetic_round2_prompt.md](../../docs/dev/05_synthetic_round2_prompt.md). 말투·금액 표기·돌려 말하기를 다양하게 요청함
- ChatGPT 12건(메시지 148개), Claude 12건(249개), Gemini 12건(188개, 예시 문구를 뺀 2차-B 지시문으로 다시 받음), Grok 12건(201개, 2차-B 지시문, 다른 유형). 처음 받은 Gemini 결과는 기준 미달이라 `raw/dev2_gemini_rejected.csv`로 보관
- 지시문의 예시 문구를 그대로 쓴 메시지는 규칙을 고치는 근거로 쓰지 않음 (05 문서 "받은 결과 점검")

## 공개 사례 재구성 (`reconstructed/`, 작업 4-2)
- 8건 (K01~K08), 규칙 작성 세션이 평가 세트와 같은 방식(메시지별 provenance)으로 재구성. 출처와 피한 것은 [docs/dev/07_reconstructed_dev.md](../../docs/dev/07_reconstructed_dev.md)
- 다시 만들기: `python tools/dev/reconstructed_dev.py`

## AI-Hub Training 일반 대화 (200건)
원문은 저장소에 넣지 않고 ID 목록 [`aihub_training_ids.csv`](aihub_training_ids.csv)만 둡니다.

- 뽑은 방법: Training 후보 18,766건에서 묶음마다 시드 20261020으로 무작위 추출, 직접 고르지 않고 모두 사용 (`--select-all`)
- 묶음: 금전·투자·외부·지원금 100, 연애·만남 50, 다자간 25, 주제만 25 (평가 세트 43건과 비슷한 비율)
- 평가 세트(Validation)와 겹치지 않음
- 재현:
  ```
  py tools/aihub/extract_candidates.py scan   --data-root "<…>/01.데이터"
  py tools/aihub/extract_candidates.py sample --out "<…>/candidates_out" --split training --n-money 100 --n-romance 50 --n-group 25 --n-topic 25 --select-all
  py tools/aihub/extract_candidates.py export --out "<…>/candidates_out" --split training
  ```
