package securityapp.scorer

import java.text.Normalizer as JNormalizer

/**
 * Hugging Face tokenizers 의 BERT 계열 처리(tokenizer.json)를 옮긴 것.
 *   BertNormalizer → BertPreTokenizer → WordPiece → [CLS] … [SEP]
 * 긴 글은 앞쪽을 자름(truncation_side=left, 최근 말을 남김). score.py·train.py 와 같음.
 * 글자 단위는 코드 포인트(Rust char와 같음).
 */
class WordPieceTokenizer(
    private val vocab: Map<String, Int>,
    private val unkToken: String = "[UNK]",
    private val prefix: String = "##",
    private val maxInputCharsPerWord: Int = 100,
    private val cleanText: Boolean = true,
    private val handleChineseChars: Boolean = true,
    private val stripAccents: Boolean = false,
    private val lowercase: Boolean = false,
    val clsId: Int,
    val sepId: Int,
) {
    private val unkId: Int = vocab[unkToken] ?: error("어휘에 $unkToken 이 없습니다")

    /** 글 → input_ids ([CLS] … [SEP] 포함, 길이 ≤ maxLen). */
    fun encode(text: String, maxLen: Int = 256): IntArray {
        val ids = ArrayList<Int>()
        for (word in preTokenize(normalize(text))) wordPiece(word, ids)
        val keep = maxLen - 2
        val body = if (ids.size > keep) ids.subList(ids.size - keep, ids.size) else ids
        val out = IntArray(body.size + 2)
        out[0] = clsId
        for (j in body.indices) out[j + 1] = body[j]
        out[out.size - 1] = sepId
        return out
    }

    /** 토큰 나누기만 (특수 토큰·자르기 없음). 확인용. */
    fun tokenize(text: String): List<Int> {
        val ids = ArrayList<Int>()
        for (word in preTokenize(normalize(text))) wordPiece(word, ids)
        return ids
    }

    // ── BertNormalizer ──
    internal fun normalize(text: String): String {
        val sb = StringBuilder(text.length + 8)
        text.codePoints().forEach { cp ->
            if (cleanText) {
                if (cp == 0 || cp == 0xFFFD || isControl(cp)) return@forEach
                if (isBertWhitespace(cp)) { sb.append(' '); return@forEach }
            }
            if (handleChineseChars && isChinese(cp)) sb.append(' ').appendCodePoint(cp).append(' ')
            else sb.appendCodePoint(cp)
        }
        var s = sb.toString()
        if (stripAccents) {
            val nfd = JNormalizer.normalize(s, JNormalizer.Form.NFD)
            val b = StringBuilder(nfd.length)
            nfd.codePoints().forEach { if (Character.getType(it) != Character.NON_SPACING_MARK.toInt()) b.appendCodePoint(it) }
            s = b.toString()
        }
        if (lowercase) s = s.lowercase(java.util.Locale.ROOT)
        return s
    }

    // ── BertPreTokenizer: 공백에서 자르고(버림), 문장부호는 한 글자씩 따로 ──
    internal fun preTokenize(text: String): List<String> {
        val out = ArrayList<String>()
        val cur = StringBuilder()
        fun cut() { if (cur.isNotEmpty()) { out.add(cur.toString()); cur.setLength(0) } }
        text.codePoints().forEach { cp ->
            when {
                isRustWhitespace(cp) -> cut()
                isBertPunct(cp) -> { cut(); out.add(String(Character.toChars(cp))) }
                else -> cur.appendCodePoint(cp)
            }
        }
        cut()
        return out
    }

    // ── WordPiece: 앞에서부터 가장 긴 조각. 한 조각이라도 없으면 낱말 전체가 [UNK] ──
    private fun wordPiece(word: String, out: MutableList<Int>) {
        val cps = word.codePoints().toArray()
        if (cps.size > maxInputCharsPerWord) { out.add(unkId); return }
        val pieces = ArrayList<Int>()
        var start = 0
        while (start < cps.size) {
            var end = cps.size
            var found = -1
            while (start < end) {
                var sub = String(cps, start, end - start)
                if (start > 0) sub = prefix + sub
                val id = vocab[sub]
                if (id != null) { found = id; break }
                end--
            }
            if (found < 0) { out.add(unkId); return }
            pieces.add(found)
            start = end
        }
        out.addAll(pieces)
    }

    companion object {
        /** tokenizer.json 내용(문자열)으로 만들기. 안드로이드에서는 assets 에서 읽어 넘김. */
        @Suppress("UNCHECKED_CAST")
        fun fromJson(text: String): WordPieceTokenizer {
            val root = Json.obj(text)
            val model = root["model"] as Map<String, Any?>
            require(model["type"] == "WordPiece") { "WordPiece 모델이 아닙니다: ${model["type"]}" }
            val vocab = HashMap<String, Int>()
            for ((k, v) in model["vocab"] as Map<String, Any?>) vocab[k] = (v as Long).toInt()

            val norm = root["normalizer"] as Map<String, Any?>?
            require(norm == null || norm["type"] == "BertNormalizer") { "지원하지 않는 normalizer: ${norm?.get("type")}" }
            val pre = root["pre_tokenizer"] as Map<String, Any?>?
            require(pre == null || pre["type"] == "BertPreTokenizer") { "지원하지 않는 pre_tokenizer: ${pre?.get("type")}" }
            val lower = norm?.get("lowercase") as Boolean? ?: false
            val strip = norm?.get("strip_accents") as Boolean? ?: lower   // null 이면 lowercase 를 따름 (HF 규칙)

            // 특수 토큰이 아닌 추가 토큰이 있으면 HF 는 그것을 먼저 떼어 냄 → 이 구현은 지원하지 않음
            val added = root["added_tokens"] as List<Map<String, Any?>>? ?: emptyList()
            val plain = added.filter { it["special"] != true }
            require(plain.isEmpty()) { "특수 토큰이 아닌 added_tokens ${plain.size}개는 지원하지 않습니다" }

            val (cls, sep) = specialIds(root["post_processor"] as Map<String, Any?>?, vocab)
            return WordPieceTokenizer(
                vocab = vocab,
                unkToken = model["unk_token"] as String? ?: "[UNK]",
                prefix = model["continuing_subword_prefix"] as String? ?: "##",
                maxInputCharsPerWord = (model["max_input_chars_per_word"] as Long? ?: 100L).toInt(),
                cleanText = norm?.get("clean_text") as Boolean? ?: true,
                handleChineseChars = norm?.get("handle_chinese_chars") as Boolean? ?: true,
                stripAccents = strip,
                lowercase = lower,
                clsId = cls, sepId = sep,
            )
        }

        @Suppress("UNCHECKED_CAST")
        private fun specialIds(pp: Map<String, Any?>?, vocab: Map<String, Int>): Pair<Int, Int> {
            fun v(t: String) = vocab[t] ?: error("어휘에 $t 가 없습니다")
            if (pp == null) return v("[CLS]") to v("[SEP]")
            return when (pp["type"]) {
                "BertProcessing" -> ((pp["cls"] as List<Any?>)[1] as Long).toInt() to ((pp["sep"] as List<Any?>)[1] as Long).toInt()
                "TemplateProcessing" -> {
                    val single = pp["single"] as List<Map<String, Any?>>
                    val shape = single.map { if ("Sequence" in it) "A" else ((it["SpecialToken"] as Map<String, Any?>)["id"] as String) }
                    require(shape.size == 3 && shape[1] == "A") { "지원하지 않는 템플릿: $shape" }
                    val sp = pp["special_tokens"] as Map<String, Any?>
                    fun id(t: String) = (((sp[t] as Map<String, Any?>)["ids"] as List<Any?>).single() as Long).toInt()
                    id(shape[0]) to id(shape[2])
                }
                else -> error("지원하지 않는 post_processor: ${pp["type"]}")
            }
        }

        // Rust tokenizers 의 글자 분류 (normalizers/bert.rs, pre_tokenizers/bert.rs)
        private fun isRustWhitespace(cp: Int) = when (cp) {   // char::is_whitespace (White_Space)
            in 0x09..0x0D, 0x20, 0x85, 0xA0, 0x1680, in 0x2000..0x200A, 0x2028, 0x2029, 0x202F, 0x205F, 0x3000 -> true
            else -> false
        }
        private fun isBertWhitespace(cp: Int) = isRustWhitespace(cp) ||
            Character.getType(cp) == Character.SPACE_SEPARATOR.toInt()
        private fun isControl(cp: Int): Boolean {
            if (cp == '\t'.code || cp == '\n'.code || cp == '\r'.code) return false
            return when (Character.getType(cp)) {   // is_other: Cc Cf Cs Co Cn
                Character.CONTROL.toInt(), Character.FORMAT.toInt(), Character.SURROGATE.toInt(),
                Character.PRIVATE_USE.toInt(), Character.UNASSIGNED.toInt() -> true
                else -> false
            }
        }
        private fun isChinese(cp: Int) = cp in 0x4E00..0x9FFF || cp in 0x3400..0x4DBF || cp in 0x20000..0x2A6DF ||
            cp in 0x2A700..0x2B73F || cp in 0x2B740..0x2B81F || cp in 0x2B920..0x2CEAF ||
            cp in 0xF900..0xFAFF || cp in 0x2F800..0x2FA1F
        private fun isBertPunct(cp: Int): Boolean {
            if (cp in 0x21..0x2F || cp in 0x3A..0x40 || cp in 0x5B..0x60 || cp in 0x7B..0x7E) return true
            return when (Character.getType(cp)) {
                Character.CONNECTOR_PUNCTUATION.toInt(), Character.DASH_PUNCTUATION.toInt(),
                Character.START_PUNCTUATION.toInt(), Character.END_PUNCTUATION.toInt(),
                Character.INITIAL_QUOTE_PUNCTUATION.toInt(), Character.FINAL_QUOTE_PUNCTUATION.toInt(),
                Character.OTHER_PUNCTUATION.toInt() -> true
                else -> false
            }
        }
    }
}
