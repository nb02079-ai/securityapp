package securityapp.scorer

/**
 * 한 대화방의 "상대" 메시지들 → 사기 점수와 경고 여부.
 * 앱은 새 메시지가 올 때마다 그 방의 상대 메시지 전체로 다시 부름 (score.py 의 위치 k 와 같음).
 * backend: input_ids → 사기일 확률. JVM·안드로이드 모두 OnnxBackend 를 씀.
 */
class ScamModel(
    val tokenizer: WordPieceTokenizer,
    private val backend: (IntArray) -> Double,
    val threshold: Double = FROZEN_THRESHOLD,
    val maxLen: Int = 256,
    val maxChars: Int = TextPrep.MAX_CHARS,
) {
    data class Verdict(val score: Double, val warn: Boolean, val text: String, val tokens: Int)

    fun judge(counterpart: List<String>): Verdict {
        require(counterpart.isNotEmpty()) { "상대 메시지가 없으면 점수를 매기지 않습니다" }
        // 정리 뒤 글이 비어도("!!!"뿐) score.py 처럼 [CLS][SEP] 로 점수를 매김
        val text = TextPrep.prefixText(counterpart, counterpart.size, maxChars)
        val ids = tokenizer.encode(text, maxLen)
        val s = backend(ids)
        return Verdict(s, s >= threshold, text, ids.size)
    }

    companion object {
        /** model-v2 고정 문턱 (결정 32, docs/results/model-v2/freeze.json). */
        const val FROZEN_THRESHOLD = 0.843446001
    }
}
