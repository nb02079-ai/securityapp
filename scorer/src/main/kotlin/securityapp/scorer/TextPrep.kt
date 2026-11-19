package securityapp.scorer

/**
 * tools/model/common.py 의 normalize·prefix_text 를 그대로 옮긴 것.
 * 파이썬 re(유니코드 \w \d \s)와 결과가 같아야 하므로 정규식 대신 글자 분류를 직접 씀.
 * 글자 단위는 코드 포인트(파이썬 str과 같음). UTF-16 길이로 자르면 이모지 등에서 달라짐.
 */
object TextPrep {
    const val SEP = " | "
    const val MAX_CHARS = 600
    private val MASK = Regex("(?:[OoXx○●*＊]{2,}|0{3,})")

    /** 파이썬 str.isspace() 와 같은 집합 (\s). */
    fun pySpace(cp: Int): Boolean = when (cp) {
        in 0x09..0x0D, in 0x1C..0x20, 0x85, 0xA0, 0x1680, in 0x2000..0x200A,
        0x2028, 0x2029, 0x202F, 0x205F, 0x3000 -> true
        else -> false
    }

    /** 파이썬 \d (유니코드 십진 숫자, Nd). */
    fun pyDigit(cp: Int): Boolean = Character.getType(cp) == Character.DECIMAL_DIGIT_NUMBER.toInt()

    /** 파이썬 \w = str.isalnum() 또는 '_' (글자 L*, 숫자 N*). */
    fun pyWord(cp: Int): Boolean {
        if (cp == '_'.code) return true
        return when (Character.getType(cp)) {
            Character.UPPERCASE_LETTER.toInt(), Character.LOWERCASE_LETTER.toInt(),
            Character.TITLECASE_LETTER.toInt(), Character.MODIFIER_LETTER.toInt(),
            Character.OTHER_LETTER.toInt(), Character.DECIMAL_DIGIT_NUMBER.toInt(),
            Character.LETTER_NUMBER.toInt(), Character.OTHER_NUMBER.toInt() -> true
            else -> false
        }
    }

    /** 파이썬 str.strip() 뒤에 글자가 남는가. */
    fun hasContent(s: String): Boolean {
        var i = 0
        while (i < s.length) {
            val cp = s.codePointAt(i)
            if (!pySpace(cp)) return true
            i += Character.charCount(cp)
        }
        return false
    }

    /** 가림 기호 → ○, 숫자 덩어리 → #, 문장부호·밑줄 → 띄어쓰기, 띄어쓰기 하나로, 앞뒤 공백 제거, 소문자. */
    fun normalize(text: String): String {
        val t = MASK.replace(text, " ○ ")
        val sb = StringBuilder(t.length)
        var pendingSpace = false   // 띄어쓰기 덩어리를 하나로 (맨 앞은 버림 = strip)
        var inDigits = false
        var i = 0
        while (i < t.length) {
            val cp = t.codePointAt(i)
            i += Character.charCount(cp)
            if (pyDigit(cp)) {                      // DIGITS: \d+ → #
                if (!inDigits) { flush(sb, pendingSpace); pendingSpace = false; sb.append('#') }
                inDigits = true
                continue
            }
            inDigits = false
            val keep = cp != '_'.code && (pyWord(cp) || cp == '|'.code || cp == '#'.code || cp == '○'.code)
            if (keep) {
                flush(sb, pendingSpace); pendingSpace = false
                sb.appendCodePoint(cp)
            } else {                                 // PUNCT·'_'·공백 → 띄어쓰기
                pendingSpace = true
            }
        }
        // 끝 공백은 버림 (strip)
        return sb.toString().lowercase(java.util.Locale.ROOT)
    }

    private fun flush(sb: StringBuilder, pending: Boolean) {
        if (pending && sb.isNotEmpty()) sb.append(' ')
    }

    /** 상대 메시지 1..k 를 정리해 " | " 로 잇고 끝에서 maxChars 글자(코드 포인트)만 남김. */
    fun prefixText(counterpart: List<String>, k: Int = counterpart.size, maxChars: Int = MAX_CHARS): String {
        val joined = counterpart.take(k).filter { hasContent(it) }.joinToString(SEP) { normalize(it) }
        return tailCodePoints(joined, maxChars)
    }

    fun tailCodePoints(s: String, n: Int): String {
        val total = s.codePointCount(0, s.length)
        if (total <= n) return s
        return s.substring(s.offsetByCodePoints(0, total - n))
    }
}
