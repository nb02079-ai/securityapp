package securityapp.engine.normalize

/**
 * 메시지 안의 금액을 원 단위 숫자로 뽑는다. G3(요구 금액 증가) 판단에 쓴다.
 *
 * 다루는 표기: "300만 원", "1억", "1억 5천만", "5,000원", "50만원", "3만", "2천만 원", "오십만 원", "십만원"
 * 다루지 않는 것: 퍼센트, 주식 수량("1만 8천 주"), 가격처럼 보이지만 금액이 아닌 숫자는 단위 "원"·"만"·"억"이 없으면 무시
 */
object Amounts {
    private val NATIVE = mapOf('일' to 1L, '이' to 2L, '삼' to 3L, '사' to 4L, '오' to 5L,
        '육' to 6L, '칠' to 7L, '팔' to 8L, '구' to 9L)
    private val SMALL_UNIT = mapOf('십' to 10L, '백' to 100L, '천' to 1000L)

    // 숫자(쉼표 가능)·한글 수사와 만/억 단위가 섞인 덩어리, 뒤에 "원"이 오거나 만/억이 들어 있어야 금액으로 봄
    private val CHUNK = Regex(
        "((?:[0-9][0-9,]*(?:\\.[0-9]+)?|[일이삼사오육칠팔구십백천]+)\\s*(?:[십백천]?만|억|천)?\\s*){1,4}(?:원)?"
    )
    private val NOT_MONEY_AFTER = Regex("^\\s*(주|명|개|건|번|회|일|시|분|초|%|퍼센트|배|층|살|세|km|kg)")

    fun extract(text: String): List<Long> {
        val out = ArrayList<Long>()
        for (m in CHUNK.findAll(text)) {
            val raw = m.value.trim()
            if (raw.isEmpty()) continue
            val hasWon = raw.endsWith("원")
            val hasBigUnit = raw.contains('만') || raw.contains('억')
            if (!hasWon && !hasBigUnit) continue
            // 한글 수사만 있고 만/억/원이 붙지 않은 "이", "오" 같은 글자는 금액이 아님
            if (raw.all { it in NATIVE.keys || it in SMALL_UNIT.keys || it.isWhitespace() }) continue
            val after = text.substring(m.range.last + 1)
            if (!hasWon && NOT_MONEY_AFTER.containsMatchIn(after)) continue
            val v = parse(raw.removeSuffix("원")) ?: continue
            if (v >= 1000) out.add(v)
        }
        return out
    }

    /** "1억 5천만" → 150000000. 해석할 수 없으면 null */
    fun parse(s: String): Long? {
        val t = s.replace(",", "").replace(" ", "")
        if (t.isEmpty()) return null
        var total = 0L
        var section = 0L   // 만·억 아래 자리
        var number = 0L    // 지금 읽는 수
        var seen = false
        var i = 0
        while (i < t.length) {
            val c = t[i]
            when {
                c.isDigit() || c == '.' -> {
                    var j = i
                    while (j < t.length && (t[j].isDigit() || t[j] == '.')) j++
                    val d = t.substring(i, j).toDoubleOrNull() ?: return null
                    // "1.5억"처럼 소수가 오면 다음 단위에서 곱함
                    if (j < t.length && (t[j] == '억' || t[j] == '만')) {
                        val unit = if (t[j] == '억') 100_000_000L else 10_000L
                        total += (d * unit).toLong()
                        j++
                    } else if (j < t.length && t[j] == '천') {
                        section += (d * 1000).toLong()
                        j++
                    } else {
                        number = d.toLong()
                    }
                    seen = true
                    i = j
                    continue
                }
                c in NATIVE -> { number = NATIVE.getValue(c); seen = true }
                c in SMALL_UNIT -> {
                    section += (if (number == 0L) 1L else number) * SMALL_UNIT.getValue(c)
                    number = 0; seen = true
                }
                c == '만' -> {
                    val v = section + number
                    total += (if (v == 0L) 1L else v) * 10_000L
                    section = 0; number = 0; seen = true
                }
                c == '억' -> {
                    val v = section + number
                    total += (if (v == 0L) 1L else v) * 100_000_000L
                    section = 0; number = 0; seen = true
                }
                else -> return null
            }
            i++
        }
        if (!seen) return null
        return total + section + number
    }
}
