package securityapp.scorer

import kotlin.test.Test
import kotlin.test.assertEquals

/** 기대값은 tools/model/common.py 로 만든 것 (파이썬 3.13). 유니코드 전체 대조는 docs/v3_plan.md 5단계-2 기록 참고. */
class TextPrepTest {
    private val cases = listOf(
        "고객님 명의로 대출이 접수되어 확인차 연락드렸습니다." to "고객님 명의로 대출이 접수되어 확인차 연락드렸습니다",
        "010-1234-5678로 전화 주세요!!" to "# # #로 전화 주세요",
        "OOO 수사관입니다 ○○지검 김○ 검사" to "○ 수사관입니다 ○ 지검 김○ 검사",
        "계좌 000-00-0000 / 1,500,000원" to "계좌 ○ # ○ # # ○ 원",
        "ＡＢＣ\u3000전각\u00a0공백\t탭\n줄" to "ａｂｃ 전각 공백 탭 줄",
        "Hello WORLD İstanbul ΣΑΣ" to "hello world i\u0307stanbul σας",
        "café naïve e\u0301" to "café naïve e",
        "\ud83d\ude00\ud83d\ude00 웃음 ㅋㅋㅋ ㅠㅠ \ud83d\udc4d🏻" to "웃음 ㅋㅋㅋ ㅠㅠ",
        "漢字 金融 𠀀" to "漢字 金融 𠀀",
        "١٢٣ 𝟏𝟐 ①② x²" to "# # ①② x²",
        "under_score __init__" to "under score init",
        "#해시 |파이프| a|b#c" to "#해시 |파이프| a|b#c",
        "!!!" to "",
        "zero\u200bwidth \ufeffBOM \u0000ctrl\u0007" to "zero width bom ctrl",
        "**카드 ＊＊＊ XX은행 ●●●" to "○ 카드 ○ ○ 은행 ○",
    )

    @Test
    fun normalizeSameAsPython() {
        for ((input, want) in cases) assertEquals(want, TextPrep.normalize(input), "입력: $input")
    }

    @Test
    fun prefixSkipsBlankAndKeepsEmptyNormalized() {
        val msgs = listOf("안녕하세요!", "   ", "!!!", "\ud83d\ude00".repeat(700), "가".repeat(700))
        assertEquals("안녕하세요", TextPrep.prefixText(msgs, 1))
        assertEquals("안녕하세요", TextPrep.prefixText(msgs, 2))
        assertEquals("안녕하세요 | ", TextPrep.prefixText(msgs, 3))
        assertEquals("안녕하세요 |  | ", TextPrep.prefixText(msgs, 4))
        val p5 = TextPrep.prefixText(msgs, 5)
        assertEquals(600, p5.codePointCount(0, p5.length))
        assertEquals("가".repeat(600), p5)
    }

    @Test
    fun tailCountsCodePoints() {
        val s = "a" + "\ud840\udc00".repeat(3)   // 𠀀 = UTF-16 두 칸
        assertEquals("\ud840\udc00".repeat(2), TextPrep.tailCodePoints(s, 2))
        assertEquals(s, TextPrep.tailCodePoints(s, 10))
    }
}
