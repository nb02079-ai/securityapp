package securityapp.engine.normalize

import java.text.Normalizer as JNormalizer

/**
 * 회피 표기를 줄이기 위한 정규화 (plan.md 4.7.2 "탐지 회피 대응").
 *
 * - [plain]: 소문자·NFC, 보이지 않는 문자 제거, 연속 공백을 하나로
 * - [compact]: 글자 사이의 공백과 구분 기호를 모두 뺀 형태. "입 금", "대.출", "계*좌" → "입금", "대출", "계좌"
 *   규칙(acts)은 주로 이 형태에서 찾는다.
 * - [toOriginal]: compact 안의 위치를 원래 문장 위치로 바꾼다 (경고 화면에 근거 구간을 보여 주기 위함)
 */
class NormalizedText private constructor(
    val original: String,
    val plain: String,
    val compact: String,
    private val compactToOriginal: IntArray,
) {
    /** compact 기준 구간 → 원래 문장 기준 구간 */
    fun toOriginal(range: IntRange): IntRange {
        if (compactToOriginal.isEmpty() || range.isEmpty()) return IntRange.EMPTY
        val s = compactToOriginal[range.first.coerceIn(0, compactToOriginal.lastIndex)]
        val e = compactToOriginal[range.last.coerceIn(0, compactToOriginal.lastIndex)]
        return s..e
    }

    companion object {
        // 글자 사이에 끼워 넣어 단어를 끊는 데 흔히 쓰는 기호
        private const val SEPARATORS = " \t\r\n.,·ㆍ-_~*^'\"`|/\\:;!?()[]{}<>+=#@&"
        private val INVISIBLE = Regex("[\\u200B-\\u200D\\u2060\\uFEFF\\u00AD]")
        private val SPACES = Regex("\\s+")

        fun of(text: String): NormalizedText {
            val nfc = JNormalizer.normalize(text, JNormalizer.Form.NFC)
            // 원래 위치를 유지하기 위해 보이지 않는 문자는 compact를 만들 때만 건너뛴다
            val sb = StringBuilder()
            val map = ArrayList<Int>(nfc.length)
            for ((i, ch) in nfc.withIndex()) {
                if (INVISIBLE.matches(ch.toString())) continue
                if (ch in SEPARATORS || ch.isWhitespace()) continue
                sb.append(ch.lowercaseChar())
                map.add(i)
            }
            val plain = SPACES.replace(INVISIBLE.replace(nfc, ""), " ").trim().lowercase()
            return NormalizedText(nfc, plain, sb.toString(), map.toIntArray())
        }
    }
}
