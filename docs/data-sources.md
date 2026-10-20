# 데이터 출처

데이터 후보 전체 조사 결과와 라이선스는 [plan.md](plan.md) 5.1절에 있습니다. 이 문서는 **실제로 쓰는 데이터**와 **저장소에 무엇을 넣는지**를 정리합니다.

## 1. 저장소에 넣는 것과 넣지 않는 것

| 자료 | 저장소 | 이유 |
|---|---|---|
| AI-Hub 대화 원문, 후보·검토·재생 파일 | **넣지 않음** | 제3자 제공·재배포 금지 |
| 평가 세트 일반 대화 ID 목록 (`data/eval/normal_selected_ids.csv`) | 넣음 | 원문 없이 ID·묶음·주제만 |
| 추출 스크립트 (`tools/aihub/`) | 넣음 | 데이터 없이 재현 절차만 담음 |
| 사기 사례 출처 목록 (아래 3절) | 넣음 | 링크와 요약만, 원문 인용 없음 |
| 사기 대화 재구성본 | 작업 1단계 후 결정 | 출처 인용 분량을 확인한 뒤 결정 |
| KorCCVi 등 외부 데이터 원문 | 넣지 않음 | 라이선스별 재배포 조건이 달라 일괄 제외 |

## 2. AI-Hub 데이터 (2026-10-20 신청·승인 완료)

| 데이터셋 | 사용 상태 | 쓰임 |
|---|---|---|
| [주제별 텍스트 일상 대화 데이터](https://aihub.or.kr/aihubdata/data/view.do?dataSetSn=543) | **사용 중** | Validation → 평가 세트 일반 대화 43건, Training → 개발용 |
| [한국어 SNS](https://www.aihub.or.kr/aihubdata/data/view.do?dataSetSn=114) | 승인, 미사용 | 대량 오탐 점검 후보 (대화 200만 건) |
| [SNS 데이터 고도화](https://aihub.or.kr/aihubdata/data/view.do?dataSetSn=71343) | 승인, 미사용 | 사회/경제 주제 정상 대화 후보 |
| [생성형AI 한국어 SNS 멀티턴 대화 데이터](https://aihub.or.kr/aihubdata/data/view.do?dataSetSn=71694) | 승인, 미사용 | 3인 대화 참고 (자체 제작 대화라 평가에는 쓰지 않음) |

## 3. 사기 사례 출처 (재구성 후보 10건)

공개 출처 중 사기 대화 전체를 실은 곳은 없었습니다. 아래 출처는 단계별 수법 서술과 짧은 인용을 제공합니다.

| # | 유형 | 출처 | 날짜 |
|---|---|---|---|
| 1 | 리딩방 (밴드, 비밀 프로젝트, 출금 시 보증금 요구) | [신동아 밀착취재](https://v.daum.net/v/20251220090142597?f=p) | 2025-12-20 |
| 2 | 리딩방 (공모주, 손실 보상으로 신뢰) | [대구MBC](https://dgmbc.com/NewsArticle/617287) | 2024-06-12 |
| 3 | 투자 (피해 회복 빙자) | [뉴스핌 — 경찰청 국가수사본부 발표](https://www.newspim.com/news/view/20240913000238) | 2024-09-13 |
| 4 | 로맨스 (해외 조향사 사칭, 통관비) | 같은 기사 | 2024-09-13 |
| 5~7 | 로맨스·투자 피해자 3명 (페이스북·틴더·인스타그램 접근) | [일요신문](https://www.ilyo.co.kr/?ac=article_view&entry_id=466617) | 2023년 사례 |
| 8 | 로맨스 (퇴역 군인 사칭, 금 배송비) | [리걸타임즈 — 부산지법 2023고단3850](https://www.legaltimes.co.kr/news/articleView.html?idxno=78553) | 2024 판결 |
| 9 | 로맨스 (외국인 사칭, 금 배송비) | [엘파인드 — 서울중앙지법 2023고단2694](https://lfind.kr/cases/%EC%84%9C%EC%9A%B8%EC%A4%91%EC%95%99%EC%A7%80%EB%B0%A9%EB%B2%95%EC%9B%90/2023%EA%B3%A0%EB%8B%A82694) | 2023-10-25 판결 |
| 10 | 투자 (나스닥 선물·코인, 원금 보장 약속) | [파이낸셜뉴스 — 서울북부지법](https://fnnews.com/news/202610151326198661) | 2026년 9월 판결 |

구조 참고: [경찰청 리딩방 사기 유형 카드뉴스](https://www.korea.kr/multi/visualNewsView.do?newsId=148929073), [KB Think 로맨스스캠 (금감원 실제 캡처 포함)](https://kbthink.com/fraud/romance-scam.html), [뉴욕주 검찰 피그 부처링 안내 (한국어)](https://ag.ny.gov/sites/default/files/publications/pigbutchering-korean.pdf)

### 재구성 원칙
- 메시지마다 출처 표시: **인용**(출처 원문) / **서술 기반**(출처가 서술한 행동을 메시지로) / **연결**(단계를 잇기 위해 작성)
- 위험 신호는 연결 메시지에 쓰지 않음
- 재구성은 엔진 규칙을 만들기 전에 끝내고 잠금
- 라벨은 완성본만 보고 붙이고, 최소 5건은 두 번째 라벨러가 독립 라벨링

## 4. 참고한 연구

| 연구 | 가져온 것 |
|---|---|
| [ConScamBench (arXiv 2607.11707)](https://arxiv.org/pdf/2607.11707) | 실제 공개 사례 중심 구성, 사기 실행 전 구간 평가, 이중 라벨링, 실제·합성 분리 보고 |
| [What Yelp Fake Review Filter Might Be Doing? (ICWSM 2013)](https://ojs.aaai.org/index.php/ICWSM/article/view/14389) | 만든 데이터에서 단어 특징이 과대평가될 위험 → 흐름·행동 신호 중심 |
| [eRisk 조기 위험 탐지·ERDE (arXiv 1911.06147)](https://arxiv.org/pdf/1911.06147) | 메시지를 하나씩 흘려 넣는 평가, 늦은 경고 감점 |
| [합성 대화형 스미싱 데이터셋 (arXiv 2604.11752)](https://www.alphaxiv.org/abs/2604.11752.md) | 라벨은 완성본만 보고 |
| [스캠 베이팅 대화 연구 (arXiv 2509.08493)](https://arxiv.org/html/2509.08493v1) | 단계 길이 참고값 (계좌 공개까지 중앙값 8턴) |
