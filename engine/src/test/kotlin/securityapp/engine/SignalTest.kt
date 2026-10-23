package securityapp.engine

import org.junit.jupiter.api.Test
import kotlin.test.assertEquals
import kotlin.test.assertNull
import kotlin.test.assertTrue

class SignalTest {
    @Test
    fun `기준표 v2_1의 신호 17개와 코드가 같다`() {
        val expected = listOf("R1", "R2", "D1", "D2", "D3", "D4", "D5", "D6", "D7",
            "P1", "P2", "P3", "P4", "G1", "G2", "G3", "G4")
        assertEquals(expected, Signal.entries.map { it.code })
    }

    @Test
    fun `돈 요구는 D2부터 D5까지다`() {
        assertEquals(setOf(Signal.D2, Signal.D3, Signal.D4, Signal.D5), Signal.entries.filter { it.isMoneyDemand }.toSet())
    }

    @Test
    fun `친밀감 쌓기만 맥락 전용이다`() {
        assertEquals(listOf(Signal.R2), Signal.entries.filter { it.isContextOnly })
    }

    @Test
    fun `코드 문자열로 찾을 때 공백과 소문자를 허용하고 없는 코드는 null`() {
        assertEquals(Signal.D4, Signal.fromCode(" d4 "))
        assertNull(Signal.fromCode("X9"))
    }

    @Test
    fun `자리 표시 엔진은 항상 관찰 단계다`() {
        val j = NoopEngine().onMessage(Message("room", "상대", "안녕하세요"))
        assertEquals(Level.OBSERVE, j.level)
        assertTrue(j.detections.isEmpty())
    }
}
