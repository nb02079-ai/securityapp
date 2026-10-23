package securityapp.engine.normalize

import org.junit.jupiter.api.Test
import kotlin.test.assertEquals

class NormalizeTest {
    @Test fun `compact는 공백과 구분 기호를 뺀다`() {
        assertEquals("입금해주세요", NormalizedText.of("입 금 해 주세요").compact)
        assertEquals("대출", NormalizedText.of("대.출").compact)
        assertEquals("계좌", NormalizedText.of("계*좌").compact)
        assertEquals("atm", NormalizedText.of("ATM").compact)
        assertEquals("입금", NormalizedText.of("입​금").compact)
    }

    @Test fun `compact 위치를 원래 문장 위치로 되돌린다`() {
        val n = NormalizedText.of("이 계좌로 보내")
        val i = n.compact.indexOf("계좌")
        val r = n.toOriginal(i..i + 1)
        assertEquals("계좌", n.original.substring(r.first, r.last + 1))
    }

    @Test fun `금액 해석`() {
        assertEquals(3_000_000L, Amounts.parse("300만"))
        assertEquals(150_000_000L, Amounts.parse("1억5천만"))
        assertEquals(20_000_000L, Amounts.parse("2천만"))
        assertEquals(500_000L, Amounts.parse("오십만"))
        assertEquals(5_000L, Amounts.parse("5,000"))
        assertEquals(150_000_000L, Amounts.parse("1.5억"))
    }

    @Test fun `문장에서 금액 뽑기`() {
        assertEquals(listOf(3_000_000L), Amounts.extract("300만 원만 보내 주세요"))
        assertEquals(listOf(50_000L, 10_000_000L), Amounts.extract("5만원 넣으면 1,000만원까지 가능"))
        assertEquals(listOf(150_000_000L), Amounts.extract("1억 5천만 원"))
    }

    @Test fun `금액이 아닌 숫자는 뽑지 않음`() {
        assertEquals(emptyList(), Amounts.extract("1만 8천 주를 사세요"))
        assertEquals(emptyList(), Amounts.extract("40% 수익"))
        assertEquals(emptyList(), Amounts.extract("이 사이트에 가입"))
        assertEquals(emptyList(), Amounts.extract("천천히 하세요"))
    }
}
