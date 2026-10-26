# -*- coding: utf-8 -*-
"""
개발용 공개 사례 재구성 (작업 4-2) — 규칙 작성 세션이 직접 씀.
평가 세트(data/eval/scam, 10건)와 봉인된 새 평가 세트(docs/holdout_v2.md, 10건)의 출처·사건은 피함.
출력: data/dev/reconstructed/K??_*.jsonl (평가 세트와 같은 형식, provenance 포함)
메시지 튜플: (room, sender, is_user, day, text, provenance, source_note)
  provenance: quote(기사 인용) / described(기사가 서술한 행동을 메시지로) / connector(흐름 연결, 위험 신호 없음)
points는 개발용 참고값(이 세션이 표시, 정답 라벨 아님).
"""
import json, os, sys

U = "나"
CASES = [
dict(case_id="K01_vote_wallet_app", scam_type="투자 리딩방 (투표 이벤트 → 가짜 지갑 앱 코인 청약)",
 source=dict(title="머니투데이 — 리딩방 후기에 나도 해봤더니 '대박'…앱부터 가짜였다", url="https://www.mt.co.kr/stock/2024/01/30/2024012910430560184", published="2024-01-30"),
 points=dict(first_suggest=7, first_transfer_before=12),
 msgs=[
 ("sms","모르는 번호",False,0,"안녕하세요. 저희 투자 전문가님이 글로벌 투자 대회에 나가 계신데요, 투표 한 번 해 주시면 커피 쿠폰이랑 투자 강의 수강권을 보내 드려요.","described","투자전문가가 글로벌 투자대회 참가 중, 투표하면 기프티콘·강의 수강권"),
 ("sms",U,True,0,"투표만 하면 되는 거예요?","connector",""),
 ("sms","모르는 번호",False,0,"네~ 투표하시고 이 방에 들어오시면 수강권 바로 드립니다 (링크)","described","카카오톡·텔레그램 리딩방 초대"),
 ("group","비서 지은",False,1,"좋은 아침입니다 여러분. 오늘 경제 기사 세 꼭지와 무료 관심 종목 올려 드립니다.","described","매일 안부 인사, 경제 기사, 무료 주식 정보"),
 ("group","회원 한결",False,9,"1분기 수익은 완벽했으며 대표님께 많은 감사를 드립니다","quote","바람잡이 수익 후기 (기사 인용)"),
 ("group","회원 서윤",False,9,"다음주 모든 주식을 팔고 두배 수익 프로젝트를 기다릴 것입니다","quote","바람잡이 후기 (기사 인용)"),
 ("group","비서 지은",False,20,"이번 분기 자금 늘리기 프로젝트 참가자 받습니다. 세 차례 진행되고 수익률 500%를 보장해 드립니다.","described","'4분기 자금 늘리기 프로젝트', 세 차례 수익률 500% 보장"),
 ("dm",U,True,20,"프로젝트 참여하려면 어떻게 해요?","connector",""),
 ("dm","비서 지은",False,20,"OO캐쉬 지갑 앱 먼저 깔아 주세요. 거기서 코인 청약 신청하시면 됩니다 (링크)","described","'한캐쉬' 디지털 지갑 앱에서 코인 청약 권유 (앱 이름 가림)"),
 ("dm","비서 지은",False,20,"청약은 테더로만 받아요. 거래소에서 사는 방법 차근차근 알려 드릴게요.","described","테더(USDT) 구매 유도"),
 ("dm",U,True,21,"처음이라 조금만 넣어 볼게요","connector",""),
 ("dm","비서 지은",False,21,"네 처음엔 작게 하시고, 수익 나면 출금도 직접 눌러 보세요. 바로 빠져요.","described","처음엔 소액 수익, 출금 자유"),
 ("dm",U,True,30,"진짜 출금되네요","connector",""),
 ("dm","비서 지은",False,40,"2회차는 배정 물량이 커서요, 청약금을 늘리시면 늘린 비율대로 더 받아 가세요.","described","투자금이 커지도록 유도"),
 ("dm",U,True,60,"출금 눌렀는데 며칠째 대기예요","connector",""),
 ("dm","비서 지은",False,60,"수익금이 커서 세금이랑 수수료를 먼저 넣어 주셔야 출금 승인이 납니다.","described","세금·수수료 명목 추가 입금 요구, 이후 출금 불가"),
 ]),
dict(case_id="K02_youtuber_band_fakeapp", scam_type="투자 리딩방 (유명 유튜버 사칭 밴드 → 금융기관 사칭 앱)",
 source=dict(title="블록미디어 — '100만 유튜버' 사진 도용하고 금융기관 사칭한 가짜 앱 가입 유도", url="https://www.blockmedia.co.kr/archives/932263", published="2025-06-22"),
 points=dict(first_suggest=5, first_transfer_before=8),
 msgs=[
 ("group","운영진",False,0,"구독자 여러분 환영합니다. 선생님 방송 보시고 오신 분들만 모신 방입니다. 공지 꼭 읽어 주세요.","described","유명 유튜버 사진이 걸린 밴드, 70명 넘게 초대"),
 ("group","회원 봄비",False,0,"방송 잘 보고 있어요! 여기서도 뵙네요","connector",""),
 ("group","운영진",False,2,"오늘 시황 정리 올립니다. 내일부터는 앱으로 실시간 매매 안내 드립니다.","connector",""),
 ("group",U,True,2,"앱은 어디서 받아요?","connector",""),
 ("group","운영진",False,3,"ㅇㅇ증권에서 주관하는 ㅇㅇㅇ프로젝트에 참여하면 500% 수익을 낼 수 있다","quote","운영진 발언 (기사 인용)"),
 ("dm","운영진",False,3,"회원님, OO증권 거래 앱 설치 링크 드립니다. 회원 등록 후 투자금 넣으시면 바로 시작돼요 (링크)","described","금융기관 이름이 적힌 가짜 증권거래 앱 가입 권유"),
 ("dm",U,True,3,"OO증권 앱이면 믿을 만하네요","connector",""),
 ("dm","운영진",False,4,"첫 입금은 1,000만 원부터 권해 드려요. 앱 화면 안내대로 이체하시면 됩니다.","described","첫 이체액 1,000만 원"),
 ("dm",U,True,5,"넣었어요. 벌써 수익이 엄청 났네요","connector","앱에 순식간에 수천만 원 수익 표시"),
 ("dm","운영진",False,6,"지금이 제일 좋을 때입니다. 더 넣으시면 프로젝트 배정이 커집니다.","described","열흘 남짓 1억 8,000만 원 이상 이체"),
 ("dm",U,True,14,"출금하려고 고객센터에 물어봤는데요","connector",""),
 ("dm","고객센터",False,14,"출금하시려면 수익금의 17%를 먼저 납부하셔야 합니다.","described","수익금 17% 선납 요구"),
 ("dm",U,True,15,"제 계정이 없어졌어요. 이게 뭐예요?","connector","앱에서 탈퇴 처리"),
 ]),
dict(case_id="K03_pe_fund_impersonation", scam_type="기관전용 사모펀드 운용사 사칭 (특별 청약 → 가짜 앱 → 출금 비용)",
 source=dict(title="뉴시스 — '기관전용 사모펀드라고?'…금감원, 소비자경보 발령", url="https://www.newsis.com/view/NISX20240522_0002743699", published="2024-05-22"),
 points=dict(first_suggest=5, first_transfer_before=8),
 msgs=[
 ("group","△△파트너스 이사",False,0,"안녕하십니까. △△파트너스 투자본부 이사입니다. 저희가 이번 밸류업 프로그램 책임 운용사로 선정되어 회원님들께 인사드립니다.","described","사모펀드 운용사 임직원 행세, 밸류업 프로그램 책임 운용사 선정 주장"),
 ("group","회원 수호",False,0,"와 기관 쪽 분이 직접 오시다니요","connector",""),
 ("group","△△파트너스 이사",False,1,"프라이빗 블라인드 전략과 AI 자동투자로 기관 수준의 수익을 개인분들께도 나눠 드리려 합니다.","described","프라이빗 블라인드 전략, AI 자동투자"),
 ("group",U,True,1,"개인도 들어갈 수 있는 거예요?","connector",""),
 ("group","△△파트너스 이사",False,2,"대표님이 상장사에 직접 요청해서, 저희 펀드 투자자분들만 낮은 가격에 청약하실 수 있게 됐습니다. 거래 앱 설치 부탁드립니다 (링크)","described","특별 청약 기회, 가짜 주식거래 앱 설치 유도"),
 ("dm","△△파트너스 매니저",False,2,"청약 증거금은 아래 수탁 계좌로 넣어 주시면 앱에 반영됩니다. (계좌번호) 예금주가 개인으로 보이는 건 수탁 절차 때문이에요.","described","타인 명의 대포통장 입금 요구"),
 ("dm",U,True,2,"알겠습니다. 보내 볼게요","connector",""),
 ("dm","△△파트너스 매니저",False,3,"축하드립니다. 증거금 대비 물량이 많이 배정됐어요. 배정분 납입금을 추가로 넣어 주셔야 확정됩니다.","described","증거금보다 많이 배정됐다며 추가 납입 요구"),
 ("dm",U,True,10,"이제 돈 좀 빼려고요","connector",""),
 ("dm","△△파트너스 매니저",False,10,"출금 전에 수수료와 비밀유지 보증금, 세금을 먼저 처리하셔야 합니다.","described","출금 시 수수료·비밀유지 보증금·세금 요구"),
 ("dm",U,True,11,"그건 못 내겠어요","connector",""),
 ("group","시스템",False,11,"△△파트너스 이사님이 회원님을 내보냈습니다.","described","거절하면 대화방에서 내보냄"),
 ]),
dict(case_id="K04_language_exchange_romance", scam_type="로맨스 (언어 교환 사이트 → 메신저 → 은행 발행 코인 사칭)",
 source=dict(title="블록미디어 — '언어 교환 사이트에서 만나서 괜찮은 사람인 줄 알았습니다'", url="https://www.blockmedia.co.kr/archives/163243", published="2020-11-17"),
 points=dict(first_suggest=7, first_transfer_before=10),
 msgs=[
 ("dm","니니",False,0,"안녕하세요! 언어 교환 사이트에서 봤어요. 저는 한국어 배우고 싶고 당신은 중국어 배우고 싶다고 했죠?","described","언어 교환 사이트에서 알게 된 뒤 메신저(라인)로 대화"),
 ("dm",U,True,0,"네 반가워요. 중국어 진짜 어렵더라고요","connector",""),
 ("dm","니니",False,3,"저는 자동차 대리점을 하고 있어요. 이건 우리 가게예요 [사진]","described","대형 자동차 대리점 운영 주장, 사진"),
 ("dm","니니",False,8,"어릴 때 집이 많이 어려웠어요. 그래서 지금은 열심히 살아요. 당신한테는 이런 얘기를 하게 되네요.","described","힘든 성장 과정 털어놓으며 신뢰"),
 ("dm",U,True,8,"그런 얘기 해 줘서 고마워요","connector",""),
 ("dm","니니",False,15,"사실 아는 사람끼리만 조용히 하는 투자가 있어요. 예일대 박사이고 월가에서 일했던 교수님이 알려 주신 거예요.","described","'아는 사람끼리만 은밀히 참여하는 투자', 명문대 교수 정보"),
 ("dm","니니",False,15,"큰 은행에서 만든 코인이라 안전해요. 지금 사 두면 나중에 많이 올라요.","described","은행이 발행한 코인이라고 소개 (코인 이름 가림)"),
 ("dm",U,True,15,"저는 코인을 한 번도 안 해 봤어요","connector",""),
 ("dm","니니",False,16,"괜찮아요 내가 알려 줄게요. 먼저 거래소에서 테더를 사고, 이 사이트에서 그 코인으로 바꾸면 돼요 (링크)","described","구매 방법 안내: 테더 구매 → 사이트에서 코인 매수"),
 ("dm",U,True,17,"말한 대로 샀어요. 올랐네요?","connector","초기 수익"),
 ("dm","니니",False,20,"봐요, 내 말 맞죠. 비트코인도 더 사서 넣으면 열 배 넘게 될 거예요.","described","추가 자금 투입 유도 (15~20배 수익 주장)"),
 ("dm",U,True,40,"출금하려니까 거래가 일시 정지됐다고만 나와요","connector","출금 막힘"),
 ]),
dict(case_id="K05_refund_project_exchange", scam_type="피해 환불 빙자 → 해외 거래소 사칭 리딩방 (대출 유도)",
 source=dict(title="머니투데이 — 4600만원 뺏긴 엄마, 벌벌 떨면서 '대출 도와줘'…코인사기 표적 됐다", url="https://www.mt.co.kr/society/2024/07/22/2024072213142172273", published="2024-07-22"),
 points=dict(first_suggest=6, first_transfer_before=7),
 msgs=[
 ("dm","환불 프로젝트 담당",False,0,"안녕하세요 고객님. 정부 의뢰로 예전 투자 사기 피해금을 돌려드리는 환불 프로젝트 담당자입니다.","described","2년 전 사기 피해금을 되찾아 주겠다며 접근, 정부 의뢰 주장"),
 ("dm",U,True,0,"정말요? 그때 60만 원 잃었는데요","connector",""),
 ("dm","환불 프로젝트 담당",False,0,"계좌 하나 새로 여시면 바로 넣어 드릴게요.","described","계좌를 열자 60만 원 입금"),
 ("dm",U,True,1,"들어왔어요! 신기하네요","connector",""),
 ("dm","환불 프로젝트 담당",False,1,"추가로 B 거래소 한국지점 리딩방에 모셔 드릴게요. 텔레그램 깔아 주세요.","described","해외 거래소 리딩방, 텔레그램 설치 요구, 가짜 한국지점"),
 ("dm","환불 프로젝트 담당",False,2,"회사 지원금이 붙는 계좌라서요, 계좌 개설 확인용으로 1,200만 원 먼저 넣어 주셔야 합니다.","described","계좌 개설 확인 명목 1,200만 원"),
 ("dm","환불 프로젝트 담당",False,2,"거래용으로는 2,500만 원 정도 준비해 주세요. 이 사이트에서 하시면 됩니다 (링크)","described","거래용 2,500만 원, 실제 거래소 주소에 'kr' 붙인 가짜 사이트"),
 ("dm",U,True,5,"손실이 나서 1,300만 원으로 줄었어요","connector",""),
 ("dm","환불 프로젝트 담당",False,5,"지원금 받으시려면 1,100만 원을 더 넣으셔야 해요.","described","지원금 조건 추가 1,100만 원"),
 ("dm","환불 프로젝트 담당",False,5,"이번에 시드(투자금)만 더 마련되면 제 프로젝트보다 고객님 수익에 더 힘쓰겠다","quote","달래기 (기사 인용)"),
 ("dm","환불 프로젝트 담당",False,6,"원금까지만이라도 되찾자","quote","설득 (기사 인용)"),
 ("dm",U,True,7,"카드론 900만 원 빌려서 보냈어요","connector","카드론 900만 원 입금"),
 ("dm","환불 프로젝트 담당",False,7,"서류 다시 올렸으니 1,100만 원으로 맞춰 주셔야 합니다.","described","대출 뒤 재요구"),
 ("dm","환불 프로젝트 담당",False,8,"회삿돈까지 잃었으니 압류에 들어가겠다","quote","협박 (기사 인용)"),
 ("dm","환불 프로젝트 담당",False,9,"의심되시면 사업자등록증 보세요 [사진] 사무실로 오셔도 됩니다.","described","위조 사업자등록증, 사무실 방문 권유"),
 ]),
dict(case_id="K06_lotto_refund_coin", scam_type="가입비 환불 빙자 → 코인 지갑 → 매수자 연결 (금융사 직원 사칭)",
 source=dict(title="경향신문 — 로또 예측 사이트 가입비 환불 미끼 가상자산 투자사기", url="https://www.khan.co.kr/article/202508102056005/", published="2025-08-10"),
 points=dict(first_suggest=6, first_transfer_before=8),
 msgs=[
 ("dm","△△증권 김대리",False,0,"안녕하세요, △△증권 김대리입니다. 예전에 가입하셨던 로또 번호 예측 사이트 가입비 환불 건으로 연락 드립니다.","described","증권사 직원 사칭, 과거 로또 예측 사이트 가입비 환불 제안"),
 ("dm","△△증권 김대리",False,0,"제 명함이랑 정부기관 공문 보내 드립니다 [사진] [사진]","described","명함과 정부기관 명의 '가입비 환불' 공문"),
 ("dm",U,True,0,"아 그 사이트 기억나요. 어떻게 받으면 돼요?","connector",""),
 ("dm","△△증권 김대리",False,1,"환불은 코인으로 지급돼요. 이 지갑 사이트에서 회원 등록부터 해 주세요 (링크)","described","코인 환불, 가상자산 지갑 사이트 가입 권유"),
 ("dm",U,True,1,"가입했더니 코인이 들어와 있네요","connector","지갑 화면에 코인 입금 표시"),
 ("dm","△△증권 김대리",False,2,"아 죄송해요, 시스템 오류로 코인이 많이 지급됐어요. 초과분 대금을 입금해 주셔야 정리가 됩니다.","described","코인이 많이 지급됐다며 대금 입금 요구"),
 ("dm","△△증권 김대리",False,3,"대신 좋은 기회예요. 제가 매수자를 찾아 드릴 테니 지금 더 사 두시면 짧은 기간에 크게 남기실 수 있어요.","described","매수자를 찾아주겠다며 추가 매수 부추김"),
 ("dm",U,True,3,"얼마나 더 사야 해요?","connector",""),
 ("dm","△△증권 김대리",False,3,"모자라시면 대출도 제가 안내해 드릴게요.","described","대출 권유 (금감원 일반 수법)"),
 ("dm",U,True,10,"김대리님 왜 연락이 안 되세요?","connector","잠적, 총 1억 2,400만 원 송금"),
 ]),
dict(case_id="K07_military_parcel_romance", scam_type="로맨스 (미군·의사 사칭 → 선물 배송비)",
 source=dict(title="문화일보 — '미국인'에 '군인·의사' 사칭해 사랑 속삭이자 수억원씩 보냈다 (로맨스 스캠 판결문 73건 분석)", url="https://v.daum.net/v/20231203233907107", published="2023-12-03"),
 points=dict(first_suggest=10, first_transfer_before=12),
 msgs=[
 ("dm","Michael",False,0,"Hello. 저는 시리아에 파병된 미군 의무 장교입니다. 번역기로 말해서 미안해요.","described","군인(32%)·의사(15%) 사칭, 미국 국적(43%), 파병 군인 사칭 예시"),
 ("dm",U,True,0,"안녕하세요. 어떻게 저를 아세요?","connector",""),
 ("dm","Michael",False,0,"당신 사진에서 따뜻한 마음을 봤어요. 친구가 되고 싶어요.","connector",""),
 ("dm","Michael",False,4,"오늘은 부대가 조용해요. 종일 당신 메시지만 기다렸어요.","connector",""),
 ("dm",U,True,4,"저도 기다리게 되네요","connector",""),
 ("dm","Michael",False,12,"내 임무가 곧 끝나요. 끝나면 한국에 가서 당신과 살고 싶어요.","connector",""),
 ("dm","Michael",False,15,"당신을 위해 선물이랑 내가 모은 돈을 상자에 넣어서 보냈어요 [사진]","described","돈과 선물을 보내겠다는 수법 (57%)"),
 ("dm",U,True,15,"정말요? 무슨 상자요?","connector",""),
 ("dm","외교 배송 담당",False,17,"고객님 앞으로 해외 화물이 도착해 보관 중입니다. 수령인 성함 맞으신지 회신 바랍니다.","described","짐 보관(15%)"),
 ("dm","Michael",False,17,"돈과 선물을 보내려고 하니 소요되는 비용을 지불해달라","quote","판결문 분석의 대표 요구 (기사 인용)"),
 ("dm","외교 배송 담당",False,17,"통관과 보관 비용 350만 원을 이 계좌로 보내 주시면 바로 배송됩니다 (계좌번호)","described","선물 배송 비용 요구 (금액은 재구성)"),
 ("dm",U,True,18,"알겠어요. 보낼게요","connector",""),
 ("dm","외교 배송 담당",False,19,"상자 안에 현금이 있어 신고 수수료가 추가로 나왔습니다.","described","추가 비용 (평균 피해 약 1억 원, 여러 차례 송금)"),
 ]),
dict(case_id="K08_asset_manager_hts", scam_type="자산운용사 사칭 투자 (SNS 광고 → 가짜 HTS, 하루 5~20%)",
 source=dict(title="파이낸셜뉴스(영문) — Cambodia-Based Leading Room Gang Arrested ('Daily 20% Profit')", url="https://en.fnnews.com/news/202509191349250565", published="2025-09-19"),
 points=dict(first_suggest=4, first_transfer_before=7),
 msgs=[
 ("dm","△△자산운용 상담팀",False,0,"광고 보고 문의 남겨 주셨죠? △△자산운용 투자상담팀입니다.","described","SNS 광고 → 연락하면 유명 자산운용사 사칭"),
 ("dm",U,True,0,"어떤 상품인지 궁금해서요","connector",""),
 ("dm","△△자산운용 상담팀",False,0,"저희 프로젝트는 실제 주가 지수와 연동된 전용 HTS로 운용됩니다 (링크)","described","실제 주가지표와 연동된 가짜 HTS"),
 ("dm","△△자산운용 상담팀",False,1,"a daily profit of 5~20% if you invest in the project","quote","수익 약속 (기사 인용, 영문 기사)"),
 ("dm","△△자산운용 상담팀",False,1,"프로젝트에 투자하시면 하루 5~20% 수익이 납니다. 원금도 저희가 책임집니다.","described","위 인용의 한국어 표현, 경찰 당부의 '원금 보장·고수익'"),
 ("dm",U,True,1,"하루에요? 처음엔 얼마부터 돼요?","connector",""),
 ("dm","영업팀 팀장",False,2,"처음엔 300만 원으로 시작해 보세요. 입금은 고객센터에서 알려 드리는 계좌로 하시면 됩니다.","described","영업팀·고객센터 역할 분담 (금액은 재구성)"),
 ("dm","고객센터",False,2,"이번 입금 계좌 안내드립니다 (계좌번호) 매번 계좌가 바뀌니 꼭 확인하고 보내 주세요.","described","타인 명의 계좌 사용"),
 ("dm",U,True,3,"넣었어요. HTS에 수익이 찍혀요","connector",""),
 ("dm","영업팀 팀장",False,5,"수익 구간이 열렸습니다. 금액을 키우시면 수익률 상단으로 배정됩니다.","described","피해액 수백만~4억 원 이상"),
 ("dm",U,True,9,"출금하고 싶은데 어떻게 해요?","connector",""),
 ("dm","고객센터",False,9,"출금 심사 중입니다. 심사 통과하려면 거래량 조건을 먼저 채우셔야 합니다.","described","출금 지연 (재구성, 기사에는 출금 방식 없음)"),
 ]),
]

def main(out):
    os.makedirs(out, exist_ok=True)
    for c in CASES:
        meta = {"type": "meta", "case_id": c["case_id"], "kind": "scam", "label": "scam", "scam_type": c["scam_type"],
                "model": "reconstructed", "source": c["source"], "dev_points": c["points"],
                "made_by": "규칙 작성 세션 (작업 4-2, 개발용)"}
        with open(os.path.join(out, c["case_id"] + ".jsonl"), "w", encoding="utf-8") as f:
            f.write(json.dumps(meta, ensure_ascii=False) + "\n")
            for i, (room, sender, is_user, day, text, prov, note) in enumerate(c["msgs"], 1):
                assert prov in ("quote", "described", "connector"), (c["case_id"], i)
                f.write(json.dumps({"type": "message", "seq": i, "room": room, "sender": sender, "is_user": is_user,
                                    "day": day, "text": text, "provenance": prov, "source_note": note}, ensure_ascii=False) + "\n")
        print(c["case_id"], len(c["msgs"]))

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join("data", "dev", "reconstructed"))
