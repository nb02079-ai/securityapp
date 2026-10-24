package securityapp.eval

/**
 * 외부 라이브러리 없이 .jsonl 한 줄을 읽는 작은 JSON 해석기.
 * 결과: Map<String, Any?> / List<Any?> / String / Long / Double / Boolean / null
 */
object Json {
    fun parse(text: String): Any? {
        val p = Parser(text)
        p.ws()
        val v = p.value()
        p.ws()
        require(p.i == text.length) { "JSON 뒤에 남은 글자가 있습니다 (위치 ${p.i})" }
        return v
    }

    @Suppress("UNCHECKED_CAST")
    fun obj(text: String): Map<String, Any?> =
        parse(text) as? Map<String, Any?> ?: throw IllegalArgumentException("JSON 객체가 아닙니다")

    private class Parser(val s: String) {
        var i = 0

        fun ws() { while (i < s.length && s[i].isWhitespace()) i++ }

        fun value(): Any? {
            require(i < s.length) { "JSON이 중간에 끝났습니다" }
            return when (val c = s[i]) {
                '{' -> obj()
                '[' -> arr()
                '"' -> str()
                't' -> lit("true", true)
                'f' -> lit("false", false)
                'n' -> lit("null", null)
                else -> if (c == '-' || c.isDigit()) num() else throw IllegalArgumentException("알 수 없는 글자 '$c' (위치 $i)")
            }
        }

        fun lit(word: String, v: Any?): Any? {
            require(s.startsWith(word, i)) { "'$word'가 와야 합니다 (위치 $i)" }
            i += word.length
            return v
        }

        fun obj(): Map<String, Any?> {
            val m = LinkedHashMap<String, Any?>()
            i++; ws()
            if (s[i] == '}') { i++; return m }
            while (true) {
                ws(); require(s[i] == '"') { "키가 와야 합니다 (위치 $i)" }
                val k = str(); ws()
                require(s[i] == ':') { "':'가 와야 합니다 (위치 $i)" }
                i++; ws()
                m[k] = value(); ws()
                when (s[i]) {
                    ',' -> i++
                    '}' -> { i++; return m }
                    else -> throw IllegalArgumentException("',' 또는 '}'가 와야 합니다 (위치 $i)")
                }
            }
        }

        fun arr(): List<Any?> {
            val a = ArrayList<Any?>()
            i++; ws()
            if (s[i] == ']') { i++; return a }
            while (true) {
                ws(); a.add(value()); ws()
                when (s[i]) {
                    ',' -> i++
                    ']' -> { i++; return a }
                    else -> throw IllegalArgumentException("',' 또는 ']'가 와야 합니다 (위치 $i)")
                }
            }
        }

        fun str(): String {
            val b = StringBuilder()
            i++
            while (true) {
                require(i < s.length) { "문자열이 닫히지 않았습니다" }
                val c = s[i++]
                when (c) {
                    '"' -> return b.toString()
                    '\\' -> {
                        when (val e = s[i++]) {
                            '"' -> b.append('"'); '\\' -> b.append('\\'); '/' -> b.append('/')
                            'b' -> b.append('\b'); 'f' -> b.append('\u000C'); 'n' -> b.append('\n')
                            'r' -> b.append('\r'); 't' -> b.append('\t')
                            'u' -> { b.append(s.substring(i, i + 4).toInt(16).toChar()); i += 4 }
                            else -> throw IllegalArgumentException("알 수 없는 이스케이프 \\$e")
                        }
                    }
                    else -> b.append(c)
                }
            }
        }

        fun num(): Any {
            val st = i
            if (s[i] == '-') i++
            while (i < s.length && (s[i].isDigit() || s[i] in ".eE+-")) i++
            val t = s.substring(st, i)
            return if (t.any { it in ".eE" }) t.toDouble() else t.toLong()
        }
    }
}
