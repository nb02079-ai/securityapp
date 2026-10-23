package securityapp.engine.acts

import org.junit.jupiter.api.Test
import securityapp.engine.Message
import securityapp.engine.Signal
import kotlin.test.assertFalse
import kotlin.test.assertTrue

/**
 * 기준표 v2.1(docs/labeling/03_label_guide.md)의 "지어낸 예시"와 "붙이지 않는 경우"로 만든 테스트.
 * 평가 세트 문장은 쓰지 않는다.
 */
class ActDetectorTest {
    private val detector = ActDetector()

    /** 1:1 대화에서 메시지 하나만 보고 감지 */
    private fun signalsOf(text: String, ctx: RoomContext = RoomContext(), sender: String = "상대"): Set<Signal> {
        val m = Message("1:1", sender, text)
        val r = detector.detect(m, ctx)
        detector.record(m, r, ctx)
        return r.signals
    }

    private fun assertHas(text: String, vararg expected: Signal) {
        val got = signalsOf(text)
        for (s in expected) assertTrue(s in got, "\"$text\"에서 ${s.code}를 기대했지만 $got")
    }

    private fun assertNot(text: String, vararg unexpected: Signal) {
        val got = signalsOf(text)
        for (s in unexpected) assertFalse(s in got, "\"$text\"에서 ${s.code}가 나오면 안 되는데 $got")
    }

    // ── D 요구 ──
    @Test fun `D1 채널 이동`() {
        assertHas("여기선 얘기하기 어려우니 이 방으로 오세요 (링크)", Signal.D1)
        assertHas("이 사이트에 회원가입부터 해 주세요", Signal.D1)
    }

    @Test fun `D2 투자금 입금과 내 계좌 매수 안내`() {
        assertHas("이번 종목 100만 원만 넣어 보세요", Signal.D2)
        assertHas("이 종목 지금 사 두세요, 다음 주면 오릅니다", Signal.D2)
        assertHas("한번 소액으로 시작해 보세요", Signal.D2)
    }

    @Test fun `D2 아님 - 자랑만, 매도 안내만`() {
        assertNot("저 오늘 40% 벌었어요", Signal.D2)
        assertNot("지금 매도하세요", Signal.D2)
    }

    @Test fun `D3 대납·차용`() {
        assertHas("어머니 수술비가 급해서 그런데 조금만 빌려 줄 수 있어요? 다음 주에 갚을게요", Signal.D3)
        assertHas("배송비만 내 주면 돼요", Signal.D3)
    }

    @Test fun `D4 지정 계좌·경로`() {
        assertHas("은행 창구 말고 ATM에서 이 계좌로 보내 주세요", Signal.D4)
        assertHas("여기로 보내 주세요 123-456-789012", Signal.D4)
    }

    @Test fun `D5 출금 조건부 추가 입금 - D3가 아님`() {
        val got = signalsOf("출금하려면 보증금 20%를 먼저 입금하셔야 합니다")
        assertTrue(Signal.D5 in got, "$got")
        assertFalse(Signal.D3 in got, "출금용이면 D3가 아님: $got")
    }

    @Test fun `D6 비밀 유지`() {
        assertHas("가족분들한테는 수익 나고 말씀하세요", Signal.D6)
        assertHas("이건 꼭 비밀로 해 주세요", Signal.D6)
    }

    @Test fun `D7 개인정보 요구`() {
        assertHas("본인 확인을 위해 신분증 사진 부탁드려요", Signal.D7)
    }

    @Test fun `D7 아님 - 손실 금액, 상대가 정보를 주는 메시지`() {
        assertNot("손실 금액 남겨 주세요", Signal.D7)
        assertNot("오늘 시장은 반도체가 강했습니다", Signal.D7)
    }

    // ── P 설득 ──
    @Test fun `P1 수익 보장`() {
        assertHas("원금은 보장되고 한 달에 30%는 기본입니다", Signal.P1)
    }

    @Test fun `P1 아님 - 가능성, 남의 수익 이야기`() {
        assertNot("수익이 날 수도 있어요", Signal.P1)
        assertNot("친구가 꽤 벌었대요", Signal.P1)
    }

    @Test fun `P2 권위·신분`() {
        assertHas("저는 증권사 출신 애널리스트입니다 [사진]", Signal.P2)
        assertHas("해외 연구소에서 일하는 의사예요", Signal.P2)
        assertHas("제 사원증 찍어서 보낼게요", Signal.P2)
    }

    @Test fun `P2 아님 - 평범한 소개`() {
        assertNot("회사원이에요", Signal.P2)
    }

    @Test fun `P3 긴급성·한정성`() {
        assertHas("오늘 장 마감 전까지만 받습니다", Signal.P3)
        assertHas("선착순 열 분만 모십니다", Signal.P3)
    }

    @Test fun `P4 확인 회피`() {
        assertHas("카메라가 고장 나서 영상통화는 다음에 해요", Signal.P4)
    }

    // ── G 진행 ──
    @Test fun `G1 소액 선보상`() {
        assertHas("가입 축하금 2만 원 보내 드렸어요, 통장 보시면 있을 거예요", Signal.G1)
    }

    @Test fun `G1 아님 - 앞으로 주겠다는 약속`() {
        assertNot("다음 주에 수익금 보내 드릴게요", Signal.G1)
    }

    @Test fun `G2 화제 급전환 - 돈과 무관한 대화 뒤 처음 돈 이야기`() {
        val ctx = RoomContext()
        signalsOf("요즘 날씨가 쌀쌀하네요", ctx)
        signalsOf("저는 어제 김치찌개 끓여 먹었어요", ctx)
        assertTrue(Signal.G2 in signalsOf("참, 요즘 코인 해 보셨어요?", ctx))
        // 이미 돈 이야기가 시작된 뒤에는 다시 붙지 않음
        assertFalse(Signal.G2 in signalsOf("코인은 지금이 기회예요", ctx))
    }

    @Test fun `G2 아님 - 처음부터 투자 이야기`() {
        val ctx = RoomContext()
        assertFalse(Signal.G2 in signalsOf("안녕하세요 투자 상담 드립니다", ctx))
    }

    @Test fun `G3 요구 금액 증가 - 규칙과 앞 금액 비교`() {
        assertHas("이번엔 500만 원은 넣어야 등급이 올라가요", Signal.G3)
        val ctx = RoomContext()
        signalsOf("처음엔 50만 원만 넣어 보세요", ctx)
        assertTrue(Signal.G3 in signalsOf("이번에는 300만 원 넣어 보세요", ctx))
    }

    @Test fun `G3 아님 - 첫 금액 제시`() {
        assertNot("처음엔 50만 원만 넣어 보세요", Signal.G3)
    }

    @Test fun `G4 거절 뒤 붙잡기`() {
        assertHas("지금 그만두면 넣은 돈도 다 날아가요", Signal.G4)
        val ctx = RoomContext()
        val me = Message("1:1", "나", "저는 이제 그만하고 싶어요", isUser = true)
        detector.record(me, detector.detect(me, ctx), ctx)
        assertTrue(Signal.G4 in signalsOf("그래도 10만 원만 더 넣어 보세요", ctx))
    }

    @Test fun `G4 아님 - 거절 없이 다시 요구`() {
        val ctx = RoomContext()
        signalsOf("10만 원만 넣어 보세요", ctx)
        assertFalse(Signal.G4 in signalsOf("10만 원만 넣어 보세요", ctx))
    }

    // ── R 관계 ──
    @Test fun `R1 단체방 다른 회원의 맞장구, 운영자는 아님`() {
        val ctx = RoomContext()
        val op = Message("단체방", "운영자", "오늘도 수익 내셨나요")
        detector.record(op, detector.detect(op, ctx), ctx)
        val member = Message("단체방", "회원1", "저도 들어갔는데 벌써 올랐네요 선생님 최고")
        val r = detector.detect(member, ctx)
        detector.record(member, r, ctx)
        assertTrue(Signal.R1 in r.signals, "${r.signals}")
        val op2 = Message("단체방", "운영자", "감사합니다 여러분")
        assertFalse(Signal.R1 in detector.detect(op2, ctx).signals)
    }

    @Test fun `R1 아님 - 1대1 대화`() {
        assertNot("감사합니다 최고예요", Signal.R1)
    }

    @Test fun `R2 친밀감`() {
        assertHas("오늘 점심은 드셨어요?", Signal.R2)
        assertHas("당신 같은 사람은 처음이에요", Signal.R2)
    }

    // ── 공통 ──
    @Test fun `회피 표기 - 띄어쓰기와 기호를 끼워 넣어도 찾음`() {
        assertHas("입 금 해 주세요", Signal.D2)
        assertHas("대.출 받아서라도 넣으세요", Signal.G3)
        assertHas("비*밀로 해 주세요", Signal.D6)
    }

    @Test fun `나의 메시지에는 신호를 붙이지 않음`() {
        val ctx = RoomContext()
        val me = Message("1:1", "나", "이 계좌로 보내면 되나요?", isUser = true)
        assertTrue(detector.detect(me, ctx).detections.isEmpty())
    }

    @Test fun `평범한 대화에는 신호가 거의 없음`() {
        assertTrue(signalsOf("내일 몇 시에 볼까? 7시 괜찮아?").isEmpty())
        assertTrue(signalsOf("주말에 영화 보러 갈래").isEmpty())
    }
}
