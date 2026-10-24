package securityapp.engine.flow

import org.junit.jupiter.api.Test
import securityapp.engine.Level
import securityapp.engine.Message
import securityapp.engine.RuleEngine
import securityapp.engine.Signal
import kotlin.test.assertEquals
import kotlin.test.assertNotNull
import kotlin.test.assertTrue

/** 흐름 판정 테스트. 대화는 모두 지어낸 것 (평가 세트 문장 아님). */
class FlowTest {
    private fun levels(vararg lines: Pair<String, String>, room: String = "1:1", group: Boolean? = false): List<Level> {
        val e = RuleEngine()
        return lines.map { (who, text) -> e.onMessage(Message(room, who, text, isUser = who == "나", isGroup = group)).level }
    }

    @Test fun `신호 하나로는 경고하지 않는다`() {
        val j = FlowJudge()
        assertEquals(Level.OBSERVE, j.onCounterpart(setOf(Signal.D3)).level)
        assertEquals(Level.OBSERVE, j.onCounterpart(setOf(Signal.D3)).level)
    }

    @Test fun `요구와 다른 분류가 함께면 주의`() {
        val j = FlowJudge()
        j.onCounterpart(setOf(Signal.P1))
        assertEquals(Level.CAUTION, j.onCounterpart(setOf(Signal.D1)).level)
    }

    @Test fun `돈 요구와 신호 세 가지 이상이면 경고`() {
        val j = FlowJudge()
        j.onCounterpart(setOf(Signal.P1))
        j.onCounterpart(setOf(Signal.D1))
        val v = j.onCounterpart(setOf(Signal.D2))
        assertEquals(Level.WARNING, v.level)
        assertNotNull(v.reason)
    }

    @Test fun `강한 신호면 둘만으로도 경고`() {
        val j = FlowJudge()
        j.onCounterpart(setOf(Signal.D3))
        assertEquals(Level.WARNING, j.onCounterpart(setOf(Signal.G4)).level)
    }

    @Test fun `계좌 안내와 서두르라는 말만으로는 주의도 아님`() {
        val j = FlowJudge()
        j.onCounterpart(setOf(Signal.D4))
        assertEquals(Level.OBSERVE, j.onCounterpart(setOf(Signal.P3)).level)
    }

    @Test fun `계좌 안내와 수익 약속이면 주의`() {
        val j = FlowJudge()
        j.onCounterpart(setOf(Signal.D4))
        assertEquals(Level.CAUTION, j.onCounterpart(setOf(Signal.P1)).level)
    }

    @Test fun `계좌 안내는 경고의 신호 수에 세지 않는다`() {
        val j = FlowJudge()
        j.onCounterpart(setOf(Signal.D2, Signal.P1))
        assertEquals(Level.CAUTION, j.onCounterpart(setOf(Signal.D4)).level)
        assertEquals(Level.WARNING, j.onCounterpart(setOf(Signal.P2)).level)
    }

    @Test fun `사진만 있는 메시지는 같은 사람의 앞 메시지를 따른다`() {
        val e = RuleEngine(FlowConfig(window = 2))
        fun say(t: String) = e.onMessage(Message("1:1", "상대", t, isGroup = false)).level
        say("원금은 보장됩니다")
        // 창이 2라 "[사진]"이 앞 메시지의 수익 약속을 이어받아야 다음 요구와 함께 주의가 남
        say("[사진]")
        assertEquals(Level.CAUTION, say("이 사이트에 회원가입부터 해 주세요"))
    }

    @Test fun `친밀감은 조합에 세지 않는다`() {
        val j = FlowJudge()
        j.onCounterpart(setOf(Signal.R2))
        assertEquals(Level.OBSERVE, j.onCounterpart(setOf(Signal.D3)).level)
    }

    @Test fun `창 밖으로 밀려난 신호는 조합에서 빠진다`() {
        val j = FlowJudge(FlowConfig(window = 3))
        j.onCounterpart(setOf(Signal.P1))
        repeat(3) { j.onCounterpart(emptySet()) }
        assertEquals(Level.OBSERVE, j.onCounterpart(setOf(Signal.D2)).level)
    }

    @Test fun `한 번 오른 단계는 내려가지 않는다`() {
        val j = FlowJudge(FlowConfig(window = 2))
        j.onCounterpart(setOf(Signal.D3))
        j.onCounterpart(setOf(Signal.G4))
        repeat(5) { assertEquals(Level.WARNING, j.onCounterpart(emptySet()).level) }
    }

    @Test fun `친구에게 급하게 돈 빌리기는 경고하지 않는다`() {
        val got = levels(
            "친구" to "미안한데 지갑을 놓고 나왔어",
            "나" to "얼마나?",
            "친구" to "2만원만 빌려줄 수 있어? 저녁에 갚을게",
            "나" to "보냈어",
            "친구" to "고마워 진짜",
        )
        assertTrue(got.all { it == Level.OBSERVE }, "$got")
    }

    @Test fun `수익 약속에서 계좌 입금, 증액으로 이어지면 경고`() {
        val got = levels(
            "상대" to "요즘 날씨가 좋네요",
            "상대" to "저는 어제 등산 다녀왔어요",
            "상대" to "참, 요즘 코인 해 보셨어요? 원금은 보장되고 한 달에 30%는 기본이에요",
            "나" to "그런 게 있어요?",
            "상대" to "처음엔 50만 원만 이 계좌로 보내 보세요 123-456-789012",
            "나" to "보냈어요",
            "상대" to "이번에는 300만 원 넣어 보세요",
        )
        // "보내 보세요"는 친구 사이에도 쓰는 말이라 v1 행위 감지는 돈 요구로 보지 않음 → 계좌 안내에서는 주의까지
        assertEquals(Level.CAUTION, got[4], "$got")
        assertEquals(Level.WARNING, got.last(), "$got")
    }

    @Test fun `나의 메시지는 단계를 바꾸지 않는다`() {
        val got = levels("나" to "투자금 보내 드릴게요, 원금 보장이죠?", "나" to "계좌 알려 주세요")
        assertTrue(got.all { it == Level.OBSERVE }, "$got")
    }

    @Test fun `대화방마다 따로 판정한다`() {
        val e = RuleEngine()
        e.onMessage(Message("방A", "상대", "원금은 보장됩니다", isGroup = false))
        val b = e.onMessage(Message("방B", "상대", "이 사이트에 회원가입부터 해 주세요", isGroup = false))
        assertEquals(Level.OBSERVE, b.level)
    }
}
