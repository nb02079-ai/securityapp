# KorCCVi 개발 세트 기준선 (engine-v1.1, 2026-10-27)

- 입력: /tmp/claude-0/-home-claude/e7861dde-9d25-5500-a195-e2b32b0b68bb/scratchpad/korccvi_out/dev
- 사기 107건 (금전 지점 라벨 0건), 일반 107건
- "상대만": 앱과 같이 받은 메시지만 엔진에 넣음 (기본). "나 포함": 내 메시지도 넣음
- 일반 대화 중 "나"가 정해지지 않은 것(AI-Hub)은 화자마다 한 번씩 "나"로 놓고 돌려, 한 번이라도 경고하면 오탐으로 셈

## 1. 세 방식 비교

금전 지점 라벨이 없는 입력이라 경고까지 갔는지만 셉니다.

| 방식 | 보는 메시지 | 사기 경고 | 일반 대화 경고 (오탐) | 일반 대화 주의 |
|---|---|---|---|---|
| 단어 기준선 | 상대만 | 59/107 (55%) | 11/107 (10%) | 0/107 (0%) |
| 행위 단독 | 상대만 | 61/107 (57%) | 41/107 (38%) | 0/107 (0%) |
| 행위 + 흐름 | 상대만 | 6/107 (6%) | 1/107 (1%) | 2/107 (2%) |
| 단어 기준선 | 나 포함 | 59/107 (55%) | 11/107 (10%) | 0/107 (0%) |
| 행위 단독 | 나 포함 | 61/107 (57%) | 41/107 (38%) | 0/107 (0%) |
| 행위 + 흐름 | 나 포함 | 6/107 (6%) | 1/107 (1%) | 2/107 (2%) |

## 2. 사례별 결과

### 단어 기준선 · 상대만

| 사례 | 유형 | 첫 금전 권유 | 결심 전 마감 | 첫 송금 직전 | 첫 주의 | 첫 경고 | 경고 난 방 | 송금 전 | 앞선 상대 메시지 |
|---|---|---|---|---|---|---|---|---|---|
| korccvi_vishing_129 | 기타 | - | - | - | - | - | - | - | - |
| korccvi_vishing_132 | 대출 | - | - | - | - | - | - | - | - |
| korccvi_vishing_135 | 대출 | - | - | - | 1 | 1 | call | - | - |
| korccvi_vishing_136 | 대출 | - | - | - | 2 | 2 | call | - | - |
| korccvi_vishing_150 | 기타 | - | - | - | - | - | - | - | - |
| korccvi_vishing_156 | 기관 사칭 | - | - | - | 9 | 9 | call | - | - |
| korccvi_vishing_159 | 기관 사칭 | - | - | - | 3 | 3 | call | - | - |
| korccvi_vishing_160 | 기관 사칭 | - | - | - | 3 | 3 | call | - | - |
| korccvi_vishing_169 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_170 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_179 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_181 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_198 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_200 | 대출 | - | - | - | 1 | 1 | call | - | - |
| korccvi_vishing_202 | 대출 | - | - | - | - | - | - | - | - |
| korccvi_vishing_213 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_217 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_221 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_234 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_245 | 기관 사칭 | - | - | - | 1 | 1 | call | - | - |
| korccvi_vishing_254 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_258 | 기타 | - | - | - | - | - | - | - | - |
| korccvi_vishing_264 | 대출 | - | - | - | 12 | 12 | call | - | - |
| korccvi_vishing_267 | 대출 | - | - | - | - | - | - | - | - |
| korccvi_vishing_28 | 대출 | - | - | - | - | - | - | - | - |
| korccvi_vishing_285 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_29 | 대출 | - | - | - | 29 | 29 | call | - | - |
| korccvi_vishing_300 | 기관 사칭 | - | - | - | 48 | 48 | call | - | - |
| korccvi_vishing_301 | 기관 사칭 | - | - | - | 3 | 3 | call | - | - |
| korccvi_vishing_303 | 기관 사칭 | - | - | - | 59 | 59 | call | - | - |
| korccvi_vishing_315 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_32 | 기관 사칭 | - | - | - | 15 | 15 | call | - | - |
| korccvi_vishing_335 | 기타 | - | - | - | - | - | - | - | - |
| korccvi_vishing_336 | 기타 | - | - | - | 8 | 8 | call | - | - |
| korccvi_vishing_337 | 기관 사칭 | - | - | - | 13 | 13 | call | - | - |
| korccvi_vishing_339 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_351 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_356 | 대출 | - | - | - | 49 | 49 | call | - | - |
| korccvi_vishing_361 | 대출 | - | - | - | 5 | 5 | call | - | - |
| korccvi_vishing_369 | 기관 사칭 | - | - | - | 26 | 26 | call | - | - |
| korccvi_vishing_373 | 기관 사칭 | - | - | - | 7 | 7 | call | - | - |
| korccvi_vishing_382 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_392 | 대출 | - | - | - | - | - | - | - | - |
| korccvi_vishing_401 | 기관 사칭 | - | - | - | 21 | 21 | call | - | - |
| korccvi_vishing_403 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_405 | 대출 | - | - | - | - | - | - | - | - |
| korccvi_vishing_406 | 기관 사칭 | - | - | - | 220 | 220 | call | - | - |
| korccvi_vishing_407 | 기타 | - | - | - | 7 | 7 | call | - | - |
| korccvi_vishing_424 | 대출 | - | - | - | - | - | - | - | - |
| korccvi_vishing_43 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_430 | 대출 | - | - | - | 9 | 9 | call | - | - |
| korccvi_vishing_436 | 대출 | - | - | - | 1 | 1 | call | - | - |
| korccvi_vishing_437 | 기타 | - | - | - | 6 | 6 | call | - | - |
| korccvi_vishing_446 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_454 | 기관 사칭 | - | - | - | 7 | 7 | call | - | - |
| korccvi_vishing_457 | 대출 | - | - | - | - | - | - | - | - |
| korccvi_vishing_459 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_461 | 기타 | - | - | - | - | - | - | - | - |
| korccvi_vishing_466 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_470 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_471 | 기관 사칭 | - | - | - | 2 | 2 | call | - | - |
| korccvi_vishing_472 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_489 | 기타 | - | - | - | 3 | 3 | call | - | - |
| korccvi_vishing_491 | 기타 | - | - | - | 3 | 3 | call | - | - |
| korccvi_vishing_5 | 대출 | - | - | - | 3 | 3 | call | - | - |
| korccvi_vishing_510 | 기관 사칭 | - | - | - | 7 | 7 | call | - | - |
| korccvi_vishing_511 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_512 | 기관 사칭 | - | - | - | 8 | 8 | call | - | - |
| korccvi_vishing_516 | 기관 사칭 | - | - | - | 12 | 12 | call | - | - |
| korccvi_vishing_52 | 기타 | - | - | - | - | - | - | - | - |
| korccvi_vishing_520 | 기관 사칭 | - | - | - | 7 | 7 | call | - | - |
| korccvi_vishing_521 | 기관 사칭 | - | - | - | 4 | 4 | call | - | - |
| korccvi_vishing_523 | 기관 사칭 | - | - | - | 13 | 13 | call | - | - |
| korccvi_vishing_536 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_539 | 기관 사칭 | - | - | - | 16 | 16 | call | - | - |
| korccvi_vishing_54 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_552 | 기관 사칭 | - | - | - | 41 | 41 | call | - | - |
| korccvi_vishing_565 | 대출 | - | - | - | 11 | 11 | call | - | - |
| korccvi_vishing_569 | 기관 사칭 | - | - | - | 1 | 1 | call | - | - |
| korccvi_vishing_572 | 기관 사칭 | - | - | - | 5 | 5 | call | - | - |
| korccvi_vishing_577 | 대출 | - | - | - | 23 | 23 | call | - | - |
| korccvi_vishing_59 | 기타 | - | - | - | 4 | 4 | call | - | - |
| korccvi_vishing_595 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_6 | 대출 | - | - | - | 24 | 24 | call | - | - |
| korccvi_vishing_60 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_604 | 기타 | - | - | - | 26 | 26 | call | - | - |
| korccvi_vishing_610 | 대출 | - | - | - | - | - | - | - | - |
| korccvi_vishing_614 | 기관 사칭 | - | - | - | 8 | 8 | call | - | - |
| korccvi_vishing_62 | 기타 | - | - | - | 4 | 4 | call | - | - |
| korccvi_vishing_622 | 기관 사칭 | - | - | - | 3 | 3 | call | - | - |
| korccvi_vishing_625 | 기관 사칭 | - | - | - | 11 | 11 | call | - | - |
| korccvi_vishing_63 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_632 | 기관 사칭 | - | - | - | 5 | 5 | call | - | - |
| korccvi_vishing_64 | 기관 사칭 | - | - | - | 2 | 2 | call | - | - |
| korccvi_vishing_653 | 기관 사칭 | - | - | - | 66 | 66 | call | - | - |
| korccvi_vishing_654 | 대출 | - | - | - | - | - | - | - | - |
| korccvi_vishing_666 | 대출 | - | - | - | 6 | 6 | call | - | - |
| korccvi_vishing_674 | 기관 사칭 | - | - | - | 4 | 4 | call | - | - |
| korccvi_vishing_682 | 기타 | - | - | - | 8 | 8 | call | - | - |
| korccvi_vishing_690 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_694 | 기관 사칭 | - | - | - | 2 | 2 | call | - | - |
| korccvi_vishing_698 | 기관 사칭 | - | - | - | 30 | 30 | call | - | - |
| korccvi_vishing_75 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_80 | 기관 사칭 | - | - | - | 1 | 1 | call | - | - |
| korccvi_vishing_82 | 기타 | - | - | - | - | - | - | - | - |
| korccvi_vishing_90 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_96 | 기타 | - | - | - | 4 | 4 | call | - | - |

### 행위 단독 · 상대만

| 사례 | 유형 | 첫 금전 권유 | 결심 전 마감 | 첫 송금 직전 | 첫 주의 | 첫 경고 | 경고 난 방 | 송금 전 | 앞선 상대 메시지 |
|---|---|---|---|---|---|---|---|---|---|
| korccvi_vishing_129 | 기타 | - | - | - | - | - | - | - | - |
| korccvi_vishing_132 | 대출 | - | - | - | 7 | 7 | call | - | - |
| korccvi_vishing_135 | 대출 | - | - | - | 4 | 4 | call | - | - |
| korccvi_vishing_136 | 대출 | - | - | - | 2 | 2 | call | - | - |
| korccvi_vishing_150 | 기타 | - | - | - | - | - | - | - | - |
| korccvi_vishing_156 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_159 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_160 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_169 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_170 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_179 | 기관 사칭 | - | - | - | 1 | 1 | call | - | - |
| korccvi_vishing_181 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_198 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_200 | 대출 | - | - | - | 4 | 4 | call | - | - |
| korccvi_vishing_202 | 대출 | - | - | - | 6 | 6 | call | - | - |
| korccvi_vishing_213 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_217 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_221 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_234 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_245 | 기관 사칭 | - | - | - | 8 | 8 | call | - | - |
| korccvi_vishing_254 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_258 | 기타 | - | - | - | - | - | - | - | - |
| korccvi_vishing_264 | 대출 | - | - | - | - | - | - | - | - |
| korccvi_vishing_267 | 대출 | - | - | - | - | - | - | - | - |
| korccvi_vishing_28 | 대출 | - | - | - | 13 | 13 | call | - | - |
| korccvi_vishing_285 | 기관 사칭 | - | - | - | 4 | 4 | call | - | - |
| korccvi_vishing_29 | 대출 | - | - | - | 1 | 1 | call | - | - |
| korccvi_vishing_300 | 기관 사칭 | - | - | - | 15 | 15 | call | - | - |
| korccvi_vishing_301 | 기관 사칭 | - | - | - | 7 | 7 | call | - | - |
| korccvi_vishing_303 | 기관 사칭 | - | - | - | 59 | 59 | call | - | - |
| korccvi_vishing_315 | 기관 사칭 | - | - | - | 2 | 2 | call | - | - |
| korccvi_vishing_32 | 기관 사칭 | - | - | - | 10 | 10 | call | - | - |
| korccvi_vishing_335 | 기타 | - | - | - | 14 | 14 | call | - | - |
| korccvi_vishing_336 | 기타 | - | - | - | 8 | 8 | call | - | - |
| korccvi_vishing_337 | 기관 사칭 | - | - | - | 13 | 13 | call | - | - |
| korccvi_vishing_339 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_351 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_356 | 대출 | - | - | - | 6 | 6 | call | - | - |
| korccvi_vishing_361 | 대출 | - | - | - | 18 | 18 | call | - | - |
| korccvi_vishing_369 | 기관 사칭 | - | - | - | 11 | 11 | call | - | - |
| korccvi_vishing_373 | 기관 사칭 | - | - | - | 1 | 1 | call | - | - |
| korccvi_vishing_382 | 기관 사칭 | - | - | - | 8 | 8 | call | - | - |
| korccvi_vishing_392 | 대출 | - | - | - | 52 | 52 | call | - | - |
| korccvi_vishing_401 | 기관 사칭 | - | - | - | 14 | 14 | call | - | - |
| korccvi_vishing_403 | 기관 사칭 | - | - | - | 3 | 3 | call | - | - |
| korccvi_vishing_405 | 대출 | - | - | - | - | - | - | - | - |
| korccvi_vishing_406 | 기관 사칭 | - | - | - | 221 | 221 | call | - | - |
| korccvi_vishing_407 | 기타 | - | - | - | 7 | 7 | call | - | - |
| korccvi_vishing_424 | 대출 | - | - | - | - | - | - | - | - |
| korccvi_vishing_43 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_430 | 대출 | - | - | - | 24 | 24 | call | - | - |
| korccvi_vishing_436 | 대출 | - | - | - | - | - | - | - | - |
| korccvi_vishing_437 | 기타 | - | - | - | 3 | 3 | call | - | - |
| korccvi_vishing_446 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_454 | 기관 사칭 | - | - | - | 7 | 7 | call | - | - |
| korccvi_vishing_457 | 대출 | - | - | - | - | - | - | - | - |
| korccvi_vishing_459 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_461 | 기타 | - | - | - | - | - | - | - | - |
| korccvi_vishing_466 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_470 | 기관 사칭 | - | - | - | 2 | 2 | call | - | - |
| korccvi_vishing_471 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_472 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_489 | 기타 | - | - | - | 3 | 3 | call | - | - |
| korccvi_vishing_491 | 기타 | - | - | - | 4 | 4 | call | - | - |
| korccvi_vishing_5 | 대출 | - | - | - | 3 | 3 | call | - | - |
| korccvi_vishing_510 | 기관 사칭 | - | - | - | 7 | 7 | call | - | - |
| korccvi_vishing_511 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_512 | 기관 사칭 | - | - | - | 8 | 8 | call | - | - |
| korccvi_vishing_516 | 기관 사칭 | - | - | - | 13 | 13 | call | - | - |
| korccvi_vishing_52 | 기타 | - | - | - | 2 | 2 | call | - | - |
| korccvi_vishing_520 | 기관 사칭 | - | - | - | 48 | 48 | call | - | - |
| korccvi_vishing_521 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_523 | 기관 사칭 | - | - | - | 25 | 25 | call | - | - |
| korccvi_vishing_536 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_539 | 기관 사칭 | - | - | - | 4 | 4 | call | - | - |
| korccvi_vishing_54 | 기관 사칭 | - | - | - | 5 | 5 | call | - | - |
| korccvi_vishing_552 | 기관 사칭 | - | - | - | 33 | 33 | call | - | - |
| korccvi_vishing_565 | 대출 | - | - | - | 47 | 47 | call | - | - |
| korccvi_vishing_569 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_572 | 기관 사칭 | - | - | - | 2 | 2 | call | - | - |
| korccvi_vishing_577 | 대출 | - | - | - | 4 | 4 | call | - | - |
| korccvi_vishing_59 | 기타 | - | - | - | 4 | 4 | call | - | - |
| korccvi_vishing_595 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_6 | 대출 | - | - | - | 30 | 30 | call | - | - |
| korccvi_vishing_60 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_604 | 기타 | - | - | - | 27 | 27 | call | - | - |
| korccvi_vishing_610 | 대출 | - | - | - | 7 | 7 | call | - | - |
| korccvi_vishing_614 | 기관 사칭 | - | - | - | 4 | 4 | call | - | - |
| korccvi_vishing_62 | 기타 | - | - | - | 4 | 4 | call | - | - |
| korccvi_vishing_622 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_625 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_63 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_632 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_64 | 기관 사칭 | - | - | - | 2 | 2 | call | - | - |
| korccvi_vishing_653 | 기관 사칭 | - | - | - | 51 | 51 | call | - | - |
| korccvi_vishing_654 | 대출 | - | - | - | 8 | 8 | call | - | - |
| korccvi_vishing_666 | 대출 | - | - | - | - | - | - | - | - |
| korccvi_vishing_674 | 기관 사칭 | - | - | - | 6 | 6 | call | - | - |
| korccvi_vishing_682 | 기타 | - | - | - | 5 | 5 | call | - | - |
| korccvi_vishing_690 | 기관 사칭 | - | - | - | 6 | 6 | call | - | - |
| korccvi_vishing_694 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_698 | 기관 사칭 | - | - | - | 3 | 3 | call | - | - |
| korccvi_vishing_75 | 기관 사칭 | - | - | - | 4 | 4 | call | - | - |
| korccvi_vishing_80 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_82 | 기타 | - | - | - | - | - | - | - | - |
| korccvi_vishing_90 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_96 | 기타 | - | - | - | - | - | - | - | - |

### 행위 + 흐름 · 상대만

| 사례 | 유형 | 첫 금전 권유 | 결심 전 마감 | 첫 송금 직전 | 첫 주의 | 첫 경고 | 경고 난 방 | 송금 전 | 앞선 상대 메시지 |
|---|---|---|---|---|---|---|---|---|---|
| korccvi_vishing_129 | 기타 | - | - | - | - | - | - | - | - |
| korccvi_vishing_132 | 대출 | - | - | - | - | - | - | - | - |
| korccvi_vishing_135 | 대출 | - | - | - | 5 | 5 | call | - | - |
| korccvi_vishing_136 | 대출 | - | - | - | - | - | - | - | - |
| korccvi_vishing_150 | 기타 | - | - | - | - | - | - | - | - |
| korccvi_vishing_156 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_159 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_160 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_169 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_170 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_179 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_181 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_198 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_200 | 대출 | - | - | - | 5 | 5 | call | - | - |
| korccvi_vishing_202 | 대출 | - | - | - | - | - | - | - | - |
| korccvi_vishing_213 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_217 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_221 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_234 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_245 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_254 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_258 | 기타 | - | - | - | - | - | - | - | - |
| korccvi_vishing_264 | 대출 | - | - | - | - | - | - | - | - |
| korccvi_vishing_267 | 대출 | - | - | - | - | - | - | - | - |
| korccvi_vishing_28 | 대출 | - | - | - | 24 | 24 | call | - | - |
| korccvi_vishing_285 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_29 | 대출 | - | - | - | - | - | - | - | - |
| korccvi_vishing_300 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_301 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_303 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_315 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_32 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_335 | 기타 | - | - | - | - | - | - | - | - |
| korccvi_vishing_336 | 기타 | - | - | - | - | - | - | - | - |
| korccvi_vishing_337 | 기관 사칭 | - | - | - | 56 | - | - | - | - |
| korccvi_vishing_339 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_351 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_356 | 대출 | - | - | - | - | - | - | - | - |
| korccvi_vishing_361 | 대출 | - | - | - | - | - | - | - | - |
| korccvi_vishing_369 | 기관 사칭 | - | - | - | 329 | - | - | - | - |
| korccvi_vishing_373 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_382 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_392 | 대출 | - | - | - | - | - | - | - | - |
| korccvi_vishing_401 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_403 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_405 | 대출 | - | - | - | - | - | - | - | - |
| korccvi_vishing_406 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_407 | 기타 | - | - | - | - | - | - | - | - |
| korccvi_vishing_424 | 대출 | - | - | - | - | - | - | - | - |
| korccvi_vishing_43 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_430 | 대출 | - | - | - | 24 | 117 | call | - | - |
| korccvi_vishing_436 | 대출 | - | - | - | - | - | - | - | - |
| korccvi_vishing_437 | 기타 | - | - | - | - | - | - | - | - |
| korccvi_vishing_446 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_454 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_457 | 대출 | - | - | - | - | - | - | - | - |
| korccvi_vishing_459 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_461 | 기타 | - | - | - | - | - | - | - | - |
| korccvi_vishing_466 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_470 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_471 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_472 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_489 | 기타 | - | - | - | - | - | - | - | - |
| korccvi_vishing_491 | 기타 | - | - | - | - | - | - | - | - |
| korccvi_vishing_5 | 대출 | - | - | - | 7 | - | - | - | - |
| korccvi_vishing_510 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_511 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_512 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_516 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_52 | 기타 | - | - | - | - | - | - | - | - |
| korccvi_vishing_520 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_521 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_523 | 기관 사칭 | - | - | - | 62 | 62 | call | - | - |
| korccvi_vishing_536 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_539 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_54 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_552 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_565 | 대출 | - | - | - | - | - | - | - | - |
| korccvi_vishing_569 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_572 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_577 | 대출 | - | - | - | - | - | - | - | - |
| korccvi_vishing_59 | 기타 | - | - | - | - | - | - | - | - |
| korccvi_vishing_595 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_6 | 대출 | - | - | - | 30 | 33 | call | - | - |
| korccvi_vishing_60 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_604 | 기타 | - | - | - | - | - | - | - | - |
| korccvi_vishing_610 | 대출 | - | - | - | - | - | - | - | - |
| korccvi_vishing_614 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_62 | 기타 | - | - | - | - | - | - | - | - |
| korccvi_vishing_622 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_625 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_63 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_632 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_64 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_653 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_654 | 대출 | - | - | - | - | - | - | - | - |
| korccvi_vishing_666 | 대출 | - | - | - | - | - | - | - | - |
| korccvi_vishing_674 | 기관 사칭 | - | - | - | 6 | - | - | - | - |
| korccvi_vishing_682 | 기타 | - | - | - | 5 | - | - | - | - |
| korccvi_vishing_690 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_694 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_698 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_75 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_80 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_82 | 기타 | - | - | - | - | - | - | - | - |
| korccvi_vishing_90 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_96 | 기타 | - | - | - | - | - | - | - | - |

### 단어 기준선 · 나 포함

| 사례 | 유형 | 첫 금전 권유 | 결심 전 마감 | 첫 송금 직전 | 첫 주의 | 첫 경고 | 경고 난 방 | 송금 전 | 앞선 상대 메시지 |
|---|---|---|---|---|---|---|---|---|---|
| korccvi_vishing_129 | 기타 | - | - | - | - | - | - | - | - |
| korccvi_vishing_132 | 대출 | - | - | - | - | - | - | - | - |
| korccvi_vishing_135 | 대출 | - | - | - | 1 | 1 | call | - | - |
| korccvi_vishing_136 | 대출 | - | - | - | 2 | 2 | call | - | - |
| korccvi_vishing_150 | 기타 | - | - | - | - | - | - | - | - |
| korccvi_vishing_156 | 기관 사칭 | - | - | - | 9 | 9 | call | - | - |
| korccvi_vishing_159 | 기관 사칭 | - | - | - | 3 | 3 | call | - | - |
| korccvi_vishing_160 | 기관 사칭 | - | - | - | 3 | 3 | call | - | - |
| korccvi_vishing_169 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_170 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_179 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_181 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_198 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_200 | 대출 | - | - | - | 1 | 1 | call | - | - |
| korccvi_vishing_202 | 대출 | - | - | - | - | - | - | - | - |
| korccvi_vishing_213 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_217 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_221 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_234 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_245 | 기관 사칭 | - | - | - | 1 | 1 | call | - | - |
| korccvi_vishing_254 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_258 | 기타 | - | - | - | - | - | - | - | - |
| korccvi_vishing_264 | 대출 | - | - | - | 12 | 12 | call | - | - |
| korccvi_vishing_267 | 대출 | - | - | - | - | - | - | - | - |
| korccvi_vishing_28 | 대출 | - | - | - | - | - | - | - | - |
| korccvi_vishing_285 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_29 | 대출 | - | - | - | 29 | 29 | call | - | - |
| korccvi_vishing_300 | 기관 사칭 | - | - | - | 48 | 48 | call | - | - |
| korccvi_vishing_301 | 기관 사칭 | - | - | - | 3 | 3 | call | - | - |
| korccvi_vishing_303 | 기관 사칭 | - | - | - | 59 | 59 | call | - | - |
| korccvi_vishing_315 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_32 | 기관 사칭 | - | - | - | 15 | 15 | call | - | - |
| korccvi_vishing_335 | 기타 | - | - | - | - | - | - | - | - |
| korccvi_vishing_336 | 기타 | - | - | - | 8 | 8 | call | - | - |
| korccvi_vishing_337 | 기관 사칭 | - | - | - | 13 | 13 | call | - | - |
| korccvi_vishing_339 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_351 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_356 | 대출 | - | - | - | 49 | 49 | call | - | - |
| korccvi_vishing_361 | 대출 | - | - | - | 5 | 5 | call | - | - |
| korccvi_vishing_369 | 기관 사칭 | - | - | - | 26 | 26 | call | - | - |
| korccvi_vishing_373 | 기관 사칭 | - | - | - | 7 | 7 | call | - | - |
| korccvi_vishing_382 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_392 | 대출 | - | - | - | - | - | - | - | - |
| korccvi_vishing_401 | 기관 사칭 | - | - | - | 21 | 21 | call | - | - |
| korccvi_vishing_403 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_405 | 대출 | - | - | - | - | - | - | - | - |
| korccvi_vishing_406 | 기관 사칭 | - | - | - | 220 | 220 | call | - | - |
| korccvi_vishing_407 | 기타 | - | - | - | 7 | 7 | call | - | - |
| korccvi_vishing_424 | 대출 | - | - | - | - | - | - | - | - |
| korccvi_vishing_43 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_430 | 대출 | - | - | - | 9 | 9 | call | - | - |
| korccvi_vishing_436 | 대출 | - | - | - | 1 | 1 | call | - | - |
| korccvi_vishing_437 | 기타 | - | - | - | 6 | 6 | call | - | - |
| korccvi_vishing_446 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_454 | 기관 사칭 | - | - | - | 7 | 7 | call | - | - |
| korccvi_vishing_457 | 대출 | - | - | - | - | - | - | - | - |
| korccvi_vishing_459 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_461 | 기타 | - | - | - | - | - | - | - | - |
| korccvi_vishing_466 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_470 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_471 | 기관 사칭 | - | - | - | 2 | 2 | call | - | - |
| korccvi_vishing_472 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_489 | 기타 | - | - | - | 3 | 3 | call | - | - |
| korccvi_vishing_491 | 기타 | - | - | - | 3 | 3 | call | - | - |
| korccvi_vishing_5 | 대출 | - | - | - | 3 | 3 | call | - | - |
| korccvi_vishing_510 | 기관 사칭 | - | - | - | 7 | 7 | call | - | - |
| korccvi_vishing_511 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_512 | 기관 사칭 | - | - | - | 8 | 8 | call | - | - |
| korccvi_vishing_516 | 기관 사칭 | - | - | - | 12 | 12 | call | - | - |
| korccvi_vishing_52 | 기타 | - | - | - | - | - | - | - | - |
| korccvi_vishing_520 | 기관 사칭 | - | - | - | 7 | 7 | call | - | - |
| korccvi_vishing_521 | 기관 사칭 | - | - | - | 4 | 4 | call | - | - |
| korccvi_vishing_523 | 기관 사칭 | - | - | - | 13 | 13 | call | - | - |
| korccvi_vishing_536 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_539 | 기관 사칭 | - | - | - | 16 | 16 | call | - | - |
| korccvi_vishing_54 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_552 | 기관 사칭 | - | - | - | 41 | 41 | call | - | - |
| korccvi_vishing_565 | 대출 | - | - | - | 11 | 11 | call | - | - |
| korccvi_vishing_569 | 기관 사칭 | - | - | - | 1 | 1 | call | - | - |
| korccvi_vishing_572 | 기관 사칭 | - | - | - | 5 | 5 | call | - | - |
| korccvi_vishing_577 | 대출 | - | - | - | 23 | 23 | call | - | - |
| korccvi_vishing_59 | 기타 | - | - | - | 4 | 4 | call | - | - |
| korccvi_vishing_595 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_6 | 대출 | - | - | - | 24 | 24 | call | - | - |
| korccvi_vishing_60 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_604 | 기타 | - | - | - | 26 | 26 | call | - | - |
| korccvi_vishing_610 | 대출 | - | - | - | - | - | - | - | - |
| korccvi_vishing_614 | 기관 사칭 | - | - | - | 8 | 8 | call | - | - |
| korccvi_vishing_62 | 기타 | - | - | - | 4 | 4 | call | - | - |
| korccvi_vishing_622 | 기관 사칭 | - | - | - | 3 | 3 | call | - | - |
| korccvi_vishing_625 | 기관 사칭 | - | - | - | 11 | 11 | call | - | - |
| korccvi_vishing_63 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_632 | 기관 사칭 | - | - | - | 5 | 5 | call | - | - |
| korccvi_vishing_64 | 기관 사칭 | - | - | - | 2 | 2 | call | - | - |
| korccvi_vishing_653 | 기관 사칭 | - | - | - | 66 | 66 | call | - | - |
| korccvi_vishing_654 | 대출 | - | - | - | - | - | - | - | - |
| korccvi_vishing_666 | 대출 | - | - | - | 6 | 6 | call | - | - |
| korccvi_vishing_674 | 기관 사칭 | - | - | - | 4 | 4 | call | - | - |
| korccvi_vishing_682 | 기타 | - | - | - | 8 | 8 | call | - | - |
| korccvi_vishing_690 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_694 | 기관 사칭 | - | - | - | 2 | 2 | call | - | - |
| korccvi_vishing_698 | 기관 사칭 | - | - | - | 30 | 30 | call | - | - |
| korccvi_vishing_75 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_80 | 기관 사칭 | - | - | - | 1 | 1 | call | - | - |
| korccvi_vishing_82 | 기타 | - | - | - | - | - | - | - | - |
| korccvi_vishing_90 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_96 | 기타 | - | - | - | 4 | 4 | call | - | - |

### 행위 단독 · 나 포함

| 사례 | 유형 | 첫 금전 권유 | 결심 전 마감 | 첫 송금 직전 | 첫 주의 | 첫 경고 | 경고 난 방 | 송금 전 | 앞선 상대 메시지 |
|---|---|---|---|---|---|---|---|---|---|
| korccvi_vishing_129 | 기타 | - | - | - | - | - | - | - | - |
| korccvi_vishing_132 | 대출 | - | - | - | 7 | 7 | call | - | - |
| korccvi_vishing_135 | 대출 | - | - | - | 4 | 4 | call | - | - |
| korccvi_vishing_136 | 대출 | - | - | - | 2 | 2 | call | - | - |
| korccvi_vishing_150 | 기타 | - | - | - | - | - | - | - | - |
| korccvi_vishing_156 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_159 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_160 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_169 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_170 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_179 | 기관 사칭 | - | - | - | 1 | 1 | call | - | - |
| korccvi_vishing_181 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_198 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_200 | 대출 | - | - | - | 4 | 4 | call | - | - |
| korccvi_vishing_202 | 대출 | - | - | - | 6 | 6 | call | - | - |
| korccvi_vishing_213 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_217 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_221 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_234 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_245 | 기관 사칭 | - | - | - | 8 | 8 | call | - | - |
| korccvi_vishing_254 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_258 | 기타 | - | - | - | - | - | - | - | - |
| korccvi_vishing_264 | 대출 | - | - | - | - | - | - | - | - |
| korccvi_vishing_267 | 대출 | - | - | - | - | - | - | - | - |
| korccvi_vishing_28 | 대출 | - | - | - | 13 | 13 | call | - | - |
| korccvi_vishing_285 | 기관 사칭 | - | - | - | 4 | 4 | call | - | - |
| korccvi_vishing_29 | 대출 | - | - | - | 1 | 1 | call | - | - |
| korccvi_vishing_300 | 기관 사칭 | - | - | - | 15 | 15 | call | - | - |
| korccvi_vishing_301 | 기관 사칭 | - | - | - | 7 | 7 | call | - | - |
| korccvi_vishing_303 | 기관 사칭 | - | - | - | 59 | 59 | call | - | - |
| korccvi_vishing_315 | 기관 사칭 | - | - | - | 2 | 2 | call | - | - |
| korccvi_vishing_32 | 기관 사칭 | - | - | - | 10 | 10 | call | - | - |
| korccvi_vishing_335 | 기타 | - | - | - | 14 | 14 | call | - | - |
| korccvi_vishing_336 | 기타 | - | - | - | 8 | 8 | call | - | - |
| korccvi_vishing_337 | 기관 사칭 | - | - | - | 13 | 13 | call | - | - |
| korccvi_vishing_339 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_351 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_356 | 대출 | - | - | - | 6 | 6 | call | - | - |
| korccvi_vishing_361 | 대출 | - | - | - | 18 | 18 | call | - | - |
| korccvi_vishing_369 | 기관 사칭 | - | - | - | 11 | 11 | call | - | - |
| korccvi_vishing_373 | 기관 사칭 | - | - | - | 1 | 1 | call | - | - |
| korccvi_vishing_382 | 기관 사칭 | - | - | - | 8 | 8 | call | - | - |
| korccvi_vishing_392 | 대출 | - | - | - | 52 | 52 | call | - | - |
| korccvi_vishing_401 | 기관 사칭 | - | - | - | 14 | 14 | call | - | - |
| korccvi_vishing_403 | 기관 사칭 | - | - | - | 3 | 3 | call | - | - |
| korccvi_vishing_405 | 대출 | - | - | - | - | - | - | - | - |
| korccvi_vishing_406 | 기관 사칭 | - | - | - | 221 | 221 | call | - | - |
| korccvi_vishing_407 | 기타 | - | - | - | 7 | 7 | call | - | - |
| korccvi_vishing_424 | 대출 | - | - | - | - | - | - | - | - |
| korccvi_vishing_43 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_430 | 대출 | - | - | - | 24 | 24 | call | - | - |
| korccvi_vishing_436 | 대출 | - | - | - | - | - | - | - | - |
| korccvi_vishing_437 | 기타 | - | - | - | 3 | 3 | call | - | - |
| korccvi_vishing_446 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_454 | 기관 사칭 | - | - | - | 7 | 7 | call | - | - |
| korccvi_vishing_457 | 대출 | - | - | - | - | - | - | - | - |
| korccvi_vishing_459 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_461 | 기타 | - | - | - | - | - | - | - | - |
| korccvi_vishing_466 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_470 | 기관 사칭 | - | - | - | 2 | 2 | call | - | - |
| korccvi_vishing_471 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_472 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_489 | 기타 | - | - | - | 3 | 3 | call | - | - |
| korccvi_vishing_491 | 기타 | - | - | - | 4 | 4 | call | - | - |
| korccvi_vishing_5 | 대출 | - | - | - | 3 | 3 | call | - | - |
| korccvi_vishing_510 | 기관 사칭 | - | - | - | 7 | 7 | call | - | - |
| korccvi_vishing_511 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_512 | 기관 사칭 | - | - | - | 8 | 8 | call | - | - |
| korccvi_vishing_516 | 기관 사칭 | - | - | - | 13 | 13 | call | - | - |
| korccvi_vishing_52 | 기타 | - | - | - | 2 | 2 | call | - | - |
| korccvi_vishing_520 | 기관 사칭 | - | - | - | 48 | 48 | call | - | - |
| korccvi_vishing_521 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_523 | 기관 사칭 | - | - | - | 25 | 25 | call | - | - |
| korccvi_vishing_536 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_539 | 기관 사칭 | - | - | - | 4 | 4 | call | - | - |
| korccvi_vishing_54 | 기관 사칭 | - | - | - | 5 | 5 | call | - | - |
| korccvi_vishing_552 | 기관 사칭 | - | - | - | 33 | 33 | call | - | - |
| korccvi_vishing_565 | 대출 | - | - | - | 47 | 47 | call | - | - |
| korccvi_vishing_569 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_572 | 기관 사칭 | - | - | - | 2 | 2 | call | - | - |
| korccvi_vishing_577 | 대출 | - | - | - | 4 | 4 | call | - | - |
| korccvi_vishing_59 | 기타 | - | - | - | 4 | 4 | call | - | - |
| korccvi_vishing_595 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_6 | 대출 | - | - | - | 30 | 30 | call | - | - |
| korccvi_vishing_60 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_604 | 기타 | - | - | - | 27 | 27 | call | - | - |
| korccvi_vishing_610 | 대출 | - | - | - | 7 | 7 | call | - | - |
| korccvi_vishing_614 | 기관 사칭 | - | - | - | 4 | 4 | call | - | - |
| korccvi_vishing_62 | 기타 | - | - | - | 4 | 4 | call | - | - |
| korccvi_vishing_622 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_625 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_63 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_632 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_64 | 기관 사칭 | - | - | - | 2 | 2 | call | - | - |
| korccvi_vishing_653 | 기관 사칭 | - | - | - | 51 | 51 | call | - | - |
| korccvi_vishing_654 | 대출 | - | - | - | 8 | 8 | call | - | - |
| korccvi_vishing_666 | 대출 | - | - | - | - | - | - | - | - |
| korccvi_vishing_674 | 기관 사칭 | - | - | - | 6 | 6 | call | - | - |
| korccvi_vishing_682 | 기타 | - | - | - | 5 | 5 | call | - | - |
| korccvi_vishing_690 | 기관 사칭 | - | - | - | 6 | 6 | call | - | - |
| korccvi_vishing_694 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_698 | 기관 사칭 | - | - | - | 3 | 3 | call | - | - |
| korccvi_vishing_75 | 기관 사칭 | - | - | - | 4 | 4 | call | - | - |
| korccvi_vishing_80 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_82 | 기타 | - | - | - | - | - | - | - | - |
| korccvi_vishing_90 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_96 | 기타 | - | - | - | - | - | - | - | - |

### 행위 + 흐름 · 나 포함

| 사례 | 유형 | 첫 금전 권유 | 결심 전 마감 | 첫 송금 직전 | 첫 주의 | 첫 경고 | 경고 난 방 | 송금 전 | 앞선 상대 메시지 |
|---|---|---|---|---|---|---|---|---|---|
| korccvi_vishing_129 | 기타 | - | - | - | - | - | - | - | - |
| korccvi_vishing_132 | 대출 | - | - | - | - | - | - | - | - |
| korccvi_vishing_135 | 대출 | - | - | - | 5 | 5 | call | - | - |
| korccvi_vishing_136 | 대출 | - | - | - | - | - | - | - | - |
| korccvi_vishing_150 | 기타 | - | - | - | - | - | - | - | - |
| korccvi_vishing_156 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_159 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_160 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_169 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_170 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_179 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_181 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_198 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_200 | 대출 | - | - | - | 5 | 5 | call | - | - |
| korccvi_vishing_202 | 대출 | - | - | - | - | - | - | - | - |
| korccvi_vishing_213 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_217 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_221 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_234 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_245 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_254 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_258 | 기타 | - | - | - | - | - | - | - | - |
| korccvi_vishing_264 | 대출 | - | - | - | - | - | - | - | - |
| korccvi_vishing_267 | 대출 | - | - | - | - | - | - | - | - |
| korccvi_vishing_28 | 대출 | - | - | - | 24 | 24 | call | - | - |
| korccvi_vishing_285 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_29 | 대출 | - | - | - | - | - | - | - | - |
| korccvi_vishing_300 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_301 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_303 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_315 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_32 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_335 | 기타 | - | - | - | - | - | - | - | - |
| korccvi_vishing_336 | 기타 | - | - | - | - | - | - | - | - |
| korccvi_vishing_337 | 기관 사칭 | - | - | - | 56 | - | - | - | - |
| korccvi_vishing_339 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_351 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_356 | 대출 | - | - | - | - | - | - | - | - |
| korccvi_vishing_361 | 대출 | - | - | - | - | - | - | - | - |
| korccvi_vishing_369 | 기관 사칭 | - | - | - | 329 | - | - | - | - |
| korccvi_vishing_373 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_382 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_392 | 대출 | - | - | - | - | - | - | - | - |
| korccvi_vishing_401 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_403 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_405 | 대출 | - | - | - | - | - | - | - | - |
| korccvi_vishing_406 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_407 | 기타 | - | - | - | - | - | - | - | - |
| korccvi_vishing_424 | 대출 | - | - | - | - | - | - | - | - |
| korccvi_vishing_43 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_430 | 대출 | - | - | - | 24 | 117 | call | - | - |
| korccvi_vishing_436 | 대출 | - | - | - | - | - | - | - | - |
| korccvi_vishing_437 | 기타 | - | - | - | - | - | - | - | - |
| korccvi_vishing_446 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_454 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_457 | 대출 | - | - | - | - | - | - | - | - |
| korccvi_vishing_459 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_461 | 기타 | - | - | - | - | - | - | - | - |
| korccvi_vishing_466 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_470 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_471 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_472 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_489 | 기타 | - | - | - | - | - | - | - | - |
| korccvi_vishing_491 | 기타 | - | - | - | - | - | - | - | - |
| korccvi_vishing_5 | 대출 | - | - | - | 7 | - | - | - | - |
| korccvi_vishing_510 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_511 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_512 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_516 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_52 | 기타 | - | - | - | - | - | - | - | - |
| korccvi_vishing_520 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_521 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_523 | 기관 사칭 | - | - | - | 62 | 62 | call | - | - |
| korccvi_vishing_536 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_539 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_54 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_552 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_565 | 대출 | - | - | - | - | - | - | - | - |
| korccvi_vishing_569 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_572 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_577 | 대출 | - | - | - | - | - | - | - | - |
| korccvi_vishing_59 | 기타 | - | - | - | - | - | - | - | - |
| korccvi_vishing_595 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_6 | 대출 | - | - | - | 30 | 33 | call | - | - |
| korccvi_vishing_60 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_604 | 기타 | - | - | - | - | - | - | - | - |
| korccvi_vishing_610 | 대출 | - | - | - | - | - | - | - | - |
| korccvi_vishing_614 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_62 | 기타 | - | - | - | - | - | - | - | - |
| korccvi_vishing_622 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_625 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_63 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_632 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_64 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_653 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_654 | 대출 | - | - | - | - | - | - | - | - |
| korccvi_vishing_666 | 대출 | - | - | - | - | - | - | - | - |
| korccvi_vishing_674 | 기관 사칭 | - | - | - | 6 | - | - | - | - |
| korccvi_vishing_682 | 기타 | - | - | - | 5 | - | - | - | - |
| korccvi_vishing_690 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_694 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_698 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_75 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_80 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_82 | 기타 | - | - | - | - | - | - | - | - |
| korccvi_vishing_90 | 기관 사칭 | - | - | - | - | - | - | - | - |
| korccvi_vishing_96 | 기타 | - | - | - | - | - | - | - | - |

## 3. 일반 대화에서 경고·주의가 난 대화 (ID만)

- 단어 기준선 · 상대만: korccvi_d01j020s011169(경고, 일반 통화), korccvi_d01j020s011686(경고, 일반 통화), korccvi_d01j04s006963(경고, 일반 통화), korccvi_d01j04s007528(경고, 일반 통화), korccvi_d02j05s003462(경고, 일반 통화), korccvi_d02j05s004778(경고, 일반 통화), korccvi_d02j07s001117(경고, 일반 통화), korccvi_d02j08s008435(경고, 일반 통화), korccvi_d02j11s008061(경고, 일반 통화), korccvi_d04j18s018176(경고, 일반 통화), korccvi_d04j18s019373(경고, 일반 통화)

- 행위 단독 · 상대만: korccvi_d01j01s000050(경고, 일반 통화), korccvi_d01j01s000574(경고, 일반 통화), korccvi_d01j01s000950(경고, 일반 통화), korccvi_d01j020s003078(경고, 일반 통화), korccvi_d01j020s004491(경고, 일반 통화), korccvi_d01j020s011169(경고, 일반 통화), korccvi_d01j020s015368(경고, 일반 통화), korccvi_d01j020s023216(경고, 일반 통화), korccvi_d01j021s002421(경고, 일반 통화), korccvi_d01j021s003634(경고, 일반 통화), korccvi_d01j021s004803(경고, 일반 통화), korccvi_d01j021s006050(경고, 일반 통화), korccvi_d01j03s001111(경고, 일반 통화), korccvi_d01j04s001634(경고, 일반 통화), korccvi_d01j04s006963(경고, 일반 통화), korccvi_d01j04s007528(경고, 일반 통화), korccvi_d02j05s000682(경고, 일반 통화), korccvi_d02j05s003462(경고, 일반 통화), korccvi_d02j05s004778(경고, 일반 통화), korccvi_d02j07s001117(경고, 일반 통화), korccvi_d02j07s004577(경고, 일반 통화), korccvi_d02j07s007061(경고, 일반 통화), korccvi_d02j08s004829(경고, 일반 통화), korccvi_d02j08s008435(경고, 일반 통화), korccvi_d02j08s008990(경고, 일반 통화), korccvi_d02j09s001642(경고, 일반 통화), korccvi_d02j11s006704(경고, 일반 통화), korccvi_d02j11s008061(경고, 일반 통화), korccvi_d02j12s000680(경고, 일반 통화), korccvi_d02j12s004598(경고, 일반 통화), korccvi_d03j15s001825(경고, 일반 통화), korccvi_d03j15s002507(경고, 일반 통화), korccvi_d04j18s000300(경고, 일반 통화), korccvi_d04j18s004834(경고, 일반 통화), korccvi_d04j18s005715(경고, 일반 통화), korccvi_d04j18s011470(경고, 일반 통화), korccvi_d04j18s012521(경고, 일반 통화), korccvi_d04j18s018176(경고, 일반 통화), korccvi_d04j18s019030(경고, 일반 통화), korccvi_d04j18s019373(경고, 일반 통화), korccvi_d04j18s019613(경고, 일반 통화)

- 행위 + 흐름 · 상대만: korccvi_d01j020s015368(주의, 일반 통화), korccvi_d02j12s000680(주의, 일반 통화), korccvi_d04j18s012521(경고, 일반 통화)

- 단어 기준선 · 나 포함: korccvi_d01j020s011169(경고, 일반 통화), korccvi_d01j020s011686(경고, 일반 통화), korccvi_d01j04s006963(경고, 일반 통화), korccvi_d01j04s007528(경고, 일반 통화), korccvi_d02j05s003462(경고, 일반 통화), korccvi_d02j05s004778(경고, 일반 통화), korccvi_d02j07s001117(경고, 일반 통화), korccvi_d02j08s008435(경고, 일반 통화), korccvi_d02j11s008061(경고, 일반 통화), korccvi_d04j18s018176(경고, 일반 통화), korccvi_d04j18s019373(경고, 일반 통화)

- 행위 단독 · 나 포함: korccvi_d01j01s000050(경고, 일반 통화), korccvi_d01j01s000574(경고, 일반 통화), korccvi_d01j01s000950(경고, 일반 통화), korccvi_d01j020s003078(경고, 일반 통화), korccvi_d01j020s004491(경고, 일반 통화), korccvi_d01j020s011169(경고, 일반 통화), korccvi_d01j020s015368(경고, 일반 통화), korccvi_d01j020s023216(경고, 일반 통화), korccvi_d01j021s002421(경고, 일반 통화), korccvi_d01j021s003634(경고, 일반 통화), korccvi_d01j021s004803(경고, 일반 통화), korccvi_d01j021s006050(경고, 일반 통화), korccvi_d01j03s001111(경고, 일반 통화), korccvi_d01j04s001634(경고, 일반 통화), korccvi_d01j04s006963(경고, 일반 통화), korccvi_d01j04s007528(경고, 일반 통화), korccvi_d02j05s000682(경고, 일반 통화), korccvi_d02j05s003462(경고, 일반 통화), korccvi_d02j05s004778(경고, 일반 통화), korccvi_d02j07s001117(경고, 일반 통화), korccvi_d02j07s004577(경고, 일반 통화), korccvi_d02j07s007061(경고, 일반 통화), korccvi_d02j08s004829(경고, 일반 통화), korccvi_d02j08s008435(경고, 일반 통화), korccvi_d02j08s008990(경고, 일반 통화), korccvi_d02j09s001642(경고, 일반 통화), korccvi_d02j11s006704(경고, 일반 통화), korccvi_d02j11s008061(경고, 일반 통화), korccvi_d02j12s000680(경고, 일반 통화), korccvi_d02j12s004598(경고, 일반 통화), korccvi_d03j15s001825(경고, 일반 통화), korccvi_d03j15s002507(경고, 일반 통화), korccvi_d04j18s000300(경고, 일반 통화), korccvi_d04j18s004834(경고, 일반 통화), korccvi_d04j18s005715(경고, 일반 통화), korccvi_d04j18s011470(경고, 일반 통화), korccvi_d04j18s012521(경고, 일반 통화), korccvi_d04j18s018176(경고, 일반 통화), korccvi_d04j18s019030(경고, 일반 통화), korccvi_d04j18s019373(경고, 일반 통화), korccvi_d04j18s019613(경고, 일반 통화)

- 행위 + 흐름 · 나 포함: korccvi_d01j020s015368(주의, 일반 통화), korccvi_d02j12s000680(주의, 일반 통화), korccvi_d04j18s012521(경고, 일반 통화)
