package securityapp.scorer

import kotlin.test.Test
import kotlin.test.assertContentEquals
import kotlin.test.assertEquals
import kotlin.test.assertFailsWith

/** 작은 가짜 어휘로 규칙만 확인. 실제 어휘와의 일치는 :eval:parity 로 확인 (집 PC). */
class WordPieceTokenizerTest {
    private fun json(added: String = """{"id":0,"content":"[PAD]","special":true}""", lower: String = "false") = """
    {"version":"1.0","added_tokens":[$added],
     "normalizer":{"type":"BertNormalizer","clean_text":true,"handle_chinese_chars":true,"strip_accents":null,"lowercase":$lower},
     "pre_tokenizer":{"type":"BertPreTokenizer"},
     "post_processor":{"type":"TemplateProcessing",
       "single":[{"SpecialToken":{"id":"[CLS]","type_id":0}},{"Sequence":{"id":"A","type_id":0}},{"SpecialToken":{"id":"[SEP]","type_id":0}}],
       "pair":[],"special_tokens":{"[CLS]":{"id":"[CLS]","ids":[2],"tokens":["[CLS]"]},"[SEP]":{"id":"[SEP]","ids":[3],"tokens":["[SEP]"]}}},
     "model":{"type":"WordPiece","unk_token":"[UNK]","continuing_subword_prefix":"##","max_input_chars_per_word":100,
       "vocab":{"[PAD]":0,"[UNK]":1,"[CLS]":2,"[SEP]":3,"[MASK]":4,"고객":5,"##님":6,"님":7,"|":8,"#":9,"대출":10,"##이":11,"漢":12,"a":13,"##b":14,"○":15,"é":16}}}
    """.trimIndent()

    private val tok = WordPieceTokenizer.fromJson(json())

    @Test
    fun greedyLongestWithPrefix() {
        assertContentEquals(intArrayOf(2, 5, 6, 8, 10, 11, 3), tok.encode("고객님 | 대출이"))
    }

    @Test
    fun unknownPieceMakesWholeWordUnk() {
        assertContentEquals(intArrayOf(2, 1, 7, 3), tok.encode("고객x 님"))
    }

    @Test
    fun chineseCharsAndPunctuationSplit() {
        // 漢 앞뒤로 공백 → a / 漢 / b, b 는 낱말 첫 조각이라 ##b 를 못 씀 → [UNK]
        assertContentEquals(intArrayOf(2, 13, 12, 1, 3), tok.encode("a漢b"))
        assertContentEquals(intArrayOf(2, 9, 5, 8, 7, 3), tok.encode("#고객|님"))
        assertContentEquals(intArrayOf(2, 15, 3), tok.encode("○"))   // ○ 은 문장부호 아님(So)
    }

    @Test
    fun leftTruncationKeepsEnd() {
        val ids = tok.encode("대출 " + "님 ".repeat(300) + "고객")
        assertEquals(256, ids.size)
        assertEquals(2, ids.first()); assertEquals(3, ids.last())
        assertEquals(5, ids[254]); assertEquals(7, ids[1])
    }

    @Test
    fun longWordIsUnk() {
        assertContentEquals(intArrayOf(2, 1, 3), tok.encode("가".repeat(101)))
    }

    @Test
    fun noAccentStripWhenNotLowercase() {
        assertContentEquals(intArrayOf(2, 16, 3), tok.encode("é"))
        // lowercase=true 면 strip_accents(null) 도 켜짐 → é → e (어휘에 없음 → UNK)
        val lowerTok = WordPieceTokenizer.fromJson(json(lower = "true"))
        assertContentEquals(intArrayOf(2, 1, 3), lowerTok.encode("é"))
    }

    @Test
    fun rejectsNonSpecialAddedTokens() {
        assertFailsWith<IllegalArgumentException> {
            WordPieceTokenizer.fromJson(json(added = """{"id":5,"content":"고객","special":false}"""))
        }
    }
}
