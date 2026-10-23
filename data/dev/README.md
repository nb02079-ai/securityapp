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

## AI-Hub Training 일반 대화 (예정)
원문은 저장소에 넣지 않고 ID 목록(`*_ids.csv`)만 둡니다.
