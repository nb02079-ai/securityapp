package securityapp.engine.acts

import org.junit.jupiter.api.Test
import securityapp.engine.Message
import securityapp.engine.Signal
import kotlin.test.assertFalse
import kotlin.test.assertTrue

/**
 * 행위 감지 v1.1에서 넣은 표현 테스트 (docs/dev/08_act_rules_v1_1.md).
 * 문장은 모두 지어낸 것이며 평가 세트·봉인 세트 문장이 아니다. 개발 세트 문장도 그대로 옮기지 않았다.
 */
class ActRulesV11Test {
    private val detector = ActDetector()

    private fun signalsOf(text: String, ctx: RoomContext = RoomContext()): Set<Signal> {
        val m = Message("1:1", "상대", text, isGroup = false)
        val r = detector.detect(m, ctx)
        detector.record(m, r, ctx)
        return r.signals
    }

    private fun has(text: String, s: Signal, ctx: RoomContext = RoomContext()) =
        signalsOf(text, ctx).let { assertTrue(s in it, "\"$text\"에서 ${s.code}를 기대했지만 $it") }

    private fun not(text: String, s: Signal, ctx: RoomContext = RoomContext()) =
        signalsOf(text, ctx).let { assertFalse(s in it, "\"$text\"에서 ${s.code}가 나오면 안 되는데 $it") }

    @Test fun `D1 메신저 설치와 전용방 초대`() {
        has("상담은 텔레그램 설치하시고 거기서 이어 갈게요", Signal.D1)
        has("이번 주부터 회원방으로 초대해 드릴게요", Signal.D1)
        not("내일 동창 모임 장소 정해서 알려줄게", Signal.D1)
    }

    @Test fun `D2 넣어 주셔야, 더 넣으시면, 사 두시면`() {
        has("이번 회차는 증거금을 넣어 주셔야 배정이 확정돼요", Signal.D2)
        has("지금 더 넣으시면 배정 물량이 커집니다", Signal.D2)
        has("이 코인 지금 사 두시면 다음 달에 크게 남아요", Signal.D2)
        has("청약 신청하시면 바로 반영됩니다", Signal.D2)
        has("최소 참여 금액은 백만 원부터예요", Signal.D2)
    }

    @Test fun `D2 투자 이야기가 나온 방에서 금액과 시작·준비`() {
        val ctx = RoomContext()
        signalsOf("요즘 코인으로 수익 내는 분들 많아요", ctx)
        has("처음엔 이백만 원으로 시작해 보세요", Signal.D2, ctx)
        // 투자 이야기가 없던 방에서는 금액 + 준비만으로 D2가 아님
        not("회비는 삼만 원 준비해 주세요", Signal.D2)
        // 상대가 이미 보냈다는 알림은 요구가 아님
        val ctx2 = RoomContext()
        signalsOf("투자 수익 정산 안내드려요", ctx2)
        not("오만 원 입금 완료했습니다", Signal.D2, ctx2)
    }

    @Test fun `D2 낱말만 나오면 아님`() {
        not("실제 투자금은 각자 알아서 관리하자", Signal.D2)
        not("매수 추천보다는 근거 비교를 해 봐요", Signal.D2)
    }

    @Test fun `D3 상대가 정한 명목의 비용`() {
        has("물건이 세관에 있어서 통관 비용 이십만 원이 필요해요", Signal.D3)
        has("교육비 오십만 원은 첫 월급에서 공제해 드리니 먼저 납부해 주세요", Signal.D3)
        has("선물을 보내려면 비용을 지불해 주셔야 해요", Signal.D3)
        has("초과분은 오늘 안에 입금해 주셔야 정리됩니다", Signal.D3)
    }

    @Test fun `D5 출금이 잠겼다, 조건을 채워야 출금`() {
        has("출금이 잠겨 있어서 해제하려면 같은 금액이 한 번 더 필요해요", Signal.D5)
        has("출금은 거래량 기준을 충족하셔야 승인됩니다", Signal.D5)
        has("세금을 먼저 넣어 주셔야 출금 승인이 나요", Signal.D5)
    }

    @Test fun `D7 앱 설치와 신분증·복구 문구`() {
        has("이 앱 하나만 깔아 주시면 확인 끝나요", Signal.D7)
        has("신분증 앞면 촬영본 보내 주세요", Signal.D7)
        has("지갑 복구문구 입력하시면 자동으로 연결돼요", Signal.D7)
    }

    @Test fun `P1 퍼센트 수익, 우리말 배수, 안전 장담`() {
        has("이번 프로젝트는 300% 수익 목표입니다", Signal.P1)
        has("지금 들어가면 열 배 넘게 됩니다", Signal.P1)
        has("이 투자는 법인이 운영해서 안전해요", Signal.P1)
        has("손실 볼 가능성 거의 없어요", Signal.P1)
        has("당신이 손해 보는 건 내가 절대 두고 보지 않아요", Signal.P1)
    }

    @Test fun `P1 부정한 보장은 아님, 다른 장담이 같이 있으면 P1`() {
        not("원금과 수익을 보장하지 않습니다", Signal.P1)
        not("모의 투자 수익률 계산법 공유할게요", Signal.P1)
        has("원금 보장은 없지만 손실 본 분은 거의 없어요", Signal.P1)
    }

    @Test fun `P2 기관 이름과 직함, 정부 의뢰, 군 신분, 공문`() {
        has("OO은행 자산관리팀 박 과장입니다", Signal.P2)
        has("정부 의뢰로 피해금 환급을 돕고 있습니다", Signal.P2)
        has("저는 해외에 파병된 군의관입니다", Signal.P2)
        has("제 명함이랑 공문 보내 드릴게요", Signal.P2)
        not("△△증권 고객센터 상담원입니다 무엇을 도와드릴까요", Signal.P2)
        not("화물운송 허가증 사본도 보내 드릴게요", Signal.P2)
    }

    @Test fun `P4 공식 창구로는 확인이 안 된다`() {
        has("대표번호로 문의하시면 조회가 안 됩니다", Signal.P4)
    }

    @Test fun `G3 금액을 키우라, G4 다시 생각해 보라`() {
        has("시드를 키우시면 상단 수익률로 배정됩니다", Signal.G3)
        has("이런 기회 흔치 않아요 다시 생각해 보세요", Signal.G4)
        not("서류는 다시 한번 검토 부탁드립니다", Signal.G4)
    }

    @Test fun `R1 넣었더니 받았다는 후기 (단체방 다른 회원)`() {
        val ctx = RoomContext()
        detector.record(Message("방", "운영자", "공지", isGroup = true), detector.detect(Message("방", "운영자", "공지", isGroup = true), ctx), ctx)
        val m = Message("방", "회원", "어제 오십 참여해서 육십오 받았어요", isGroup = true)
        assertTrue(Signal.R1 in detector.detect(m, ctx).signals)
    }
}
