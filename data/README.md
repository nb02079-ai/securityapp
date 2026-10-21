# 데이터

이 폴더에는 **외부 데이터 원문을 넣지 않습니다.** `.gitignore`가 `data/README.md`, `data/eval/*_ids.csv`, 직접 쓴 사기 재구성본 `data/eval/scam/`만 커밋되도록 막고 있습니다.

## 1. 일반 대화 (AI-Hub 「주제별 텍스트 일상 대화 데이터」)

1. [AI-Hub](https://aihub.or.kr/aihubdata/data/view.do?dataSetSn=543)에서 데이터를 신청해 내려받습니다 (내국인만 신청 가능).
2. 압축을 풀지 않아도 됩니다. 폴더 구조는 다음과 같습니다.
   ```
   020.주제별 텍스트 일상 대화 데이터/
   └── 01.데이터/
       ├── 1.Training/
       │   ├── 라벨링데이터/              (TL_01. KAKAO(2).zip …)
       │   ├── 라벨링데이터_250929_add/   (TL_01. KAKAO(1).zip — 2025-09 추가분)
       │   └── 원천데이터/                (사용 안 함)
       └── 2.Validation/
           ├── 라벨링데이터/
           └── 원천데이터/                (사용 안 함)
   ```
3. 저장소 **밖** 폴더에서 아래를 실행합니다 (`tools/aihub/extract_candidates.py`는 출력 폴더가 git 저장소 안이면 멈춥니다).

```
python tools/aihub/extract_candidates.py scan   --data-root "<…>/01.데이터"
python tools/aihub/extract_candidates.py sample --out "<…>/candidates_out"          # 시드 20261020
# review_validation.csv 의 selected 칸에 Y 표시 (또는 아래 ID 목록과 맞춤)
python tools/aihub/extract_candidates.py export --out "<…>/candidates_out"
```

### 평가 세트 일반 대화 43건

[`eval/normal_selected_ids.csv`](eval/normal_selected_ids.csv)에 고른 대화의 ID와 묶음만 있습니다. 대화 내용은 없습니다.

| 묶음 | 건수 | 뜻 |
|---|---|---|
| 금전_투자_외부_지원금 | 22 | 주식·코인·대출·계좌·링크·재난지원금 이야기가 섞인 정상 대화 |
| 연애_만남 | 11 | 연애/결혼 주제 + 만남 이야기 (로맨스 사기와 비교용) |
| 다자간 | 5 | 3인 이상 대화 (단체방 비교용) |
| 주제만 | 5 | 키워드 없이 주제만 맞는 쉬운 정상 대화 |

고른 방법: Validation 후보 2,526건 → 묶음별 시드 고정 무작위 추출 109건 → 직접 읽고 43건 선택.

### 데이터에서 확인한 사항
- 메시지마다 보낸 시각이 없어 시간 기반 신호는 이 데이터로 평가할 수 없습니다.
- 일부 대화 끝에 앞 메시지를 `1 : 내용` 형태로 한 번 더 붙인 오류 줄이 있어 scan 단계에서 제외합니다 (Training 152줄, Validation 36줄).
- 대화 중 주제가 바뀌는 경우는 거의 없습니다 (Training 3건, Validation 0건).

## 2. 사기 대화 (공개 사례 기반 재구성)

공개 출처에 사기 대화 전체를 실은 곳이 없어, 출처의 단계 흐름과 짧은 인용을 뼈대로 재구성합니다. 출처와 방식은 [docs/data-sources.md](../docs/data-sources.md)에 있습니다. 재구성본 10건은 [`eval/scam/`](eval/scam/)에 있습니다 (메시지 187개, 그중 상대방 122개). **커밋 `9e40dca`(2026-10-21)에서 잠갔고, 엔진 규칙은 그 뒤에 만듭니다.**

- `scamNN_*.jsonl`: 첫 줄은 사례 정보(meta), 이후 한 줄이 메시지 하나 (`seq`, `room`, `sender`, `is_user`, `day`, `text`, `provenance`, `source_note` 등)
- `scamNN_*.md`: 사람이 읽기 위한 표 (`.jsonl`에서 자동 생성)
- `provenance`: `quote`(출처 원문) / `described`(출처가 서술한 행동을 메시지로) / `connector`(단계를 잇기 위해 작성, 위험 신호 없음)

```
# 형식·출처 표시·연결 메시지 위험 단어·계좌번호 같은 숫자열 점검 + .md 다시 생성
python tools/scam/check_case.py data/eval/scam/*.jsonl

# 라벨러용 가림판 (출처·메모·사례 이름 제거). 출력은 저장소 밖 폴더로
python tools/scam/make_blind.py data/eval/scam/*.jsonl --out "<…>/blind_out"                    # 자유 메모 때 쓴 판
python tools/scam/make_blind.py data/eval/scam/*.jsonl --out "<…>/blind_out" --shuffle-seed N   # 라벨링부터, 번호를 섞은 판
```
`blind_key.csv`(가림판 번호 ↔ 사례 이름)는 라벨러 세션에 넣지 않습니다. 자유 메모와 라벨링 절차는 [docs/labeling/](../docs/labeling/)에 있습니다.
