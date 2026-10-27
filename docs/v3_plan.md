# v3.0 작업 계획 (결정 27·28, plan.md 7.2·7.4)

목표: 실제 사기 통화(KorCCVi)와 금융 콜센터로 소형 분류 모델을 만들고, **11-03까지 고정 → 평가 1회**를 마칩니다.
- 판정 기준: 탐지율(첫 결정적 지시 메시지까지 경고) 90% 이상, 오탐률 3% 이하
- 기한 방식: 마감에 못 미쳐도 그 시점의 최선을 고정하고 결과를 그대로 적습니다.

## 1단계 데이터 정리 (마감 10-28)
- [x] KorCCVi 변환, 묶기, 나누기, 봉인 — [korccvi.md](korccvi.md), `data/eval/korccvi_split_ids.csv`
- [x] 개발 세트 기준선(규칙 v1.1): 사기 경고 6/107, 일반 경고 1/107
- [x] 금융 콜센터 구조 확인 (여러 턴 대화, 중앙값 20문장) — [callcenter.md](callcenter.md)
- [x] 콜센터 변환 도구 `tools/aihub/import_callcenter.py` (Validation → 평가 봉인, Training → 학습·개발)
- [x] 금융 콜센터 변환·나누기·봉인: 학습 13,834 / 개발 2,441 / 평가 2,039 (해시 `e8975226…76a6`)
- [ ] 집 PC에서 KorCCVi 재현: `--check`로 나누기 결과가 같은지 확인

## 2단계 평가 라벨 (마감 10-30)
- [x] **완료 (10-27)**: 세 모델 일치 68, 둘 일치 30, 사용자 판정 5 → none 77 / 번호 26 ([08](labeling/08_label_decisive.md))
- 평가용 사기 통화 103건마다 **첫 결정적 지시** 지점 하나를 정합니다.
  - 결정적 지시: 피해로 이어지는 첫 지시. 이체·송금, 현금 인출·전달, 앱 설치·원격 제어, 계좌·카드·인증번호 같은 금융 정보 제공 등이 해당합니다.
  - 지시가 없는 통화(잘린 녹음 등)는 `none`으로 둡니다. `none`인 통화는 탐지율 분모에서 빼지 않고, "통화가 끝나기 전까지 경고"로 셉니다. 이 기준은 라벨을 받기 전에 정해 둡니다.
- 라벨러: ChatGPT·Gemini·Grok. 프로젝트 밖, 기억 끔. 이 세션(Claude)은 평가 통화를 보지 않으므로 빠집니다.
- 지점이 둘 이상 같으면 그 값으로 정합니다. 셋이 모두 다르면 사용자가 판정합니다.

## 3단계 모델 개발 (마감 11-02)
- 모델: 소형 한국어 인코더 1개(KoELECTRA-small 수준), Python으로 미세조정합니다.
- 입력: 지금까지의 상대 메시지 누적본(최근 N자). 메시지가 하나 올 때마다 위험 점수를 냅니다.
- 학습 데이터:
  - 사기 쪽: KorCCVi 학습 세트 사기 통화
  - 일반 쪽: KorCCVi 학습 세트 일반 통화, 콜센터 학습분
- 문턱: 개발 세트 일반 대화의 오탐이 3% 이하가 되도록 정합니다.
- 보조 점검: 메신저 데이터(합성 개발 61, AI-Hub 메신저 일반)
- 지름길 점검: 출처별 오탐(KorCCVi 일반 / 콜센터)과, 상대 말만 넣었을 때와 전체를 넣었을 때를 비교합니다.

## 4단계 고정·평가 (마감 11-03)
- 모델 파일과 문턱을 태그 `model-v1`로 고정합니다.
- 평가 세트를 1회 실행합니다. 결과에 함께 적을 것:
  - 탐지율과 오탐률(95% 신뢰구간)
  - 같은 조건의 단어 기준선과 규칙 v1.1
  - 첫 경고 위치(중앙값)
  - 메신저 데이터에서의 같은 두 숫자(보조)
- 결과 문서에는 목표 대비 달성/미달, 원인, 다음에 해 볼 것을 적습니다.

## 5단계 앱 (그 뒤)
- ONNX 또는 LiteRT로 바꾸고 int8로 줄입니다. 기기 안 처리 시간을 잽니다.
- 카카오톡 알림 연결, 인터넷 권한 없음, 공유 버튼(plan.md 4장).

## 3단계 실행 순서 (집 PC, cmd)

코드는 `tools/model/`에 있습니다.
- `common.py`: 정규화와 관점 처리
- `build_examples.py`: 학습 예시 만들기
- `train.py`: 미세조정
- `score.py`: 위험 점수 매기기
- `metrics.py`: 탐지율·오탐률 계산

평가(test) 폴더는 `build_examples.py`가 받지 않습니다. `score.py`도 `--eval-set` 없이는 멈춥니다.

```
:: 0) 준비 (한 번만)
py -m pip install torch --index-url https://download.pytorch.org/whl/cu121
py -m pip install -r tools\model\requirements.txt
set D=%USERPROFILE%\Desktop
set K=%D%\korccvi_calls
set C=%D%\callcenter_calls
set M=%D%\model_v1

:: 1) 데이터 다시 만들기 (집 PC) — 나누기가 같은지 확인
py tools\korccvi\import_calls.py --korccvi %D%\KorCCVi --out %K% --check data\eval\korccvi_split_ids.csv
py tools\aihub\import_callcenter.py --input %D%\data --out %C% --check data\eval\callcenter_split_ids.csv

:: 2) 예시 만들기 (학습·개발만)
py tools\model\build_examples.py --input %K%\train --input %C%\train --max-convs-per-source callcenter=3000 --out %M%\train.jsonl
py tools\model\build_examples.py --input %K%\dev --input %C%\dev --max-convs-per-source callcenter=500 --out %M%\dev.jsonl

:: 3) 점검용 짧은 학습 → 본 학습
py tools\model\train.py --train %M%\train.jsonl --dev %M%\dev.jsonl --out %M%\smoke --smoke
py tools\model\train.py --train %M%\train.jsonl --dev %M%\dev.jsonl --out %M%

:: 4) 개발 세트 점수 → 오탐 3% 문턱 고르기
py tools\model\score.py --model %M%\best --input %K%\dev --input %C%\dev --out %M%\dev_scores.csv
py tools\model\metrics.py --scores %M%\dev_scores.csv --pick-fp 0.03 --title "model-v1 개발 세트" --out %M%\dev_report.md
```

- 확인용 기준(단어 기준선): KorCCVi 개발 세트에서 Python 단어 점수기(`score.py --scorer words`)와 재생 평가기 결과가 같았습니다. 사기 59/107, 일반 11/107입니다.
