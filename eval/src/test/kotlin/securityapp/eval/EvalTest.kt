package securityapp.eval

import org.junit.jupiter.api.Test
import securityapp.engine.Level
import kotlin.math.abs
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertNull
import kotlin.test.assertTrue

/** 평가기 테스트. 대화는 모두 지어낸 것 (평가 세트 문장 아님). */
class EvalTest {
    private fun conv(label: String, vararg lines: String, meta: String = "") =
        Loader.parse(listOf("""{"type":"meta","case_id":"t1","label":"$label"$meta}""") + lines.toList(), "t1")

    private fun msg(seq: Int, sender: String, text: String, user: Boolean? = false, room: String = "dm") =
        """{"type":"message","seq":$seq,"room":"$room","sender":"$sender"""" +
            (if (user == null) "" else ""","is_user":$user""") + ""","text":"$text"}"""

    @Test fun `JSON 해석`() {
        val m = Json.obj("""{"a":"줄\n바꿈 \"따옴표\" A","b":[1,2.5,true,null],"c":{"d":-3}}""")
        assertEquals("줄\n바꿈 \"따옴표\" A", m["a"])
        assertEquals(listOf(1L, 2.5, true, null), m["b"])
        assertEquals(mapOf("d" to -3L), m["c"])
    }

    @Test fun `대화 읽기와 라벨`() {
        val c = conv("scam", msg(1, "상대", "안녕하세요"), msg(2, "나", "네", user = true))
        assertTrue(c.isScam)
        assertFalse(c.userUnknown)
        assertEquals(listOf("상대", "나"), c.senders)
    }

    @Test fun `개발 세트의 kind도 라벨로 읽음`() {
        val c = Loader.parse(listOf("""{"type":"meta","case_id":"x","kind":"normal"}""", msg(1, "친구", "밥 먹자")), "x")
        assertEquals("normal", c.label)
    }

    @Test fun `방 이름으로 단체방 여부`() {
        assertEquals(true, Loader.groupFlag("group_telegram", null))
        assertEquals(true, Loader.groupFlag("단체방(동호회)", null))
        assertEquals(true, Loader.groupFlag("오픈채팅(캠핑)", null))
        assertEquals(false, Loader.groupFlag("dm_secretary", null))
        assertEquals(false, Loader.groupFlag("1:1(민수)", null))
        assertEquals(false, Loader.groupFlag("중고거래 채팅", null))
        assertEquals(true, Loader.groupFlag("BAND_1_01__s1", true))
        assertNull(Loader.groupFlag("BAND_1_01__s1", null))
    }

    @Test fun `기본은 나의 메시지를 넣지 않는다`() {
        val c = conv("scam", msg(1, "상대", "안녕하세요"), msg(2, "나", "투자 수익 계좌 알려 주세요", user = true), msg(3, "상대", "네"))
        val base = Replay.run(WordBaseline(), c).single()
        assertEquals(listOf(1, 3), base.levels.map { it.first })
        assertEquals(Level.OBSERVE, base.maxLevel)
        // 나 포함 판에서도 단어 기준선은 상대 메시지만 셈
        assertEquals(Level.OBSERVE, Replay.run(WordBaseline(), c, includeUser = true).single().maxLevel)
    }

    @Test fun `나가 정해지지 않은 대화는 화자마다 한 번씩`() {
        val c = conv("normal", msg(1, "1", "요즘 주식 투자 해?", user = null, room = "r"), msg(2, "2", "아니 안 해", user = null, room = "r"))
        val rs = Replay.run(WordBaseline(), c)
        assertEquals(listOf("1", "2"), rs.map { it.userSender })
        // 2가 "나"일 때만 1의 "투자"를 받음
        assertEquals(listOf(Level.OBSERVE, Level.WARNING), rs.map { it.maxLevel })
        val n = Metrics.normalOutcome(c, rs)
        assertEquals(Level.WARNING, n.maxLevel)
        assertEquals(1, n.warnedPerspectives)
    }

    @Test fun `띄어쓰기를 끼워 넣어도 단어 기준선이 잡음`() {
        val c = conv("scam", msg(1, "상대", "입 금 부탁해요"))
        assertEquals(Level.WARNING, Replay.run(WordBaseline(), c).single().maxLevel)
    }

    @Test fun `여러 방 중 하나라도 경고면 사례 경고, 처음 경고한 방 기록`() {
        val c = conv("scam",
            msg(1, "운영자", "오늘도 좋은 하루", room = "group"),
            msg(2, "상대", "이 계좌로 입금하세요", room = "dm"),
            msg(3, "운영자", "공지입니다", room = "group"))
        val r = Replay.run(WordBaseline(), c).single()
        assertEquals(2, r.firstSeq(Level.WARNING))
        assertEquals("dm", r.firstLevelRoom[Level.WARNING])
        assertEquals(Level.WARNING, r.levels.last().second)
    }

    @Test fun `송금 전 경고와 앞선 메시지 수`() {
        val c = conv("scam",
            msg(1, "상대", "안녕"), msg(2, "나", "응", user = true), msg(3, "상대", "투자해 볼래?"),
            msg(4, "상대", "좋아"), msg(5, "나", "어디로?", user = true), msg(6, "상대", "여기로"), msg(7, "상대", "보내"))
        val p = MoneyPoints("t1", firstSuggest = 3, firstIntentBefore = 4, firstTransferBefore = 7, transferSeen = true)
        val o = Metrics.scamOutcome(c, Replay.run(WordBaseline(), c).single(), p)
        assertEquals(3, o.firstWarning)
        assertEquals(2, o.warningK) // 상대 메시지 1, 3
        assertEquals(3, o.leadTransfer) // 상대 메시지 4, 6, 7
        assertTrue(o.beforeTransfer && o.beforeSuggest && o.beforeIntent)
    }

    @Test fun `마감점 뒤 경고는 놓친 것`() {
        val c = conv("scam", msg(1, "상대", "안녕"), msg(2, "상대", "반가워"), msg(3, "상대", "수익 났어"))
        val p = MoneyPoints("t1", 1, 2, 2, true)
        val o = Metrics.scamOutcome(c, Replay.run(WordBaseline(), c).single(), p)
        assertEquals(3, o.firstWarning)
        assertFalse(o.beforeTransfer)
        assertNull(o.leadTransfer)
    }

    @Test fun `결심 전 마감은 두 지점 중 앞의 것`() {
        assertEquals(5, MoneyPoints("x", 3, 8, 5, false).intentDeadline)
        assertEquals(4, MoneyPoints("x", 3, 4, 9, true).intentDeadline)
    }

    @Test fun `ERDE 계산`() {
        fun close(a: Double, b: Double) = assertTrue(abs(a - b) < 1e-9, "$a != $b")
        close(0.5, Metrics.latency(5, 5))
        val p = MoneyPoints("a", 1, 1, 10, true)
        val hit = ScamOutcome("a", "", p, null, 5, null, 5, 0, 10)
        val miss = ScamOutcome("b", "", p, null, null, null, null, null, 10)
        val fp = NormalOutcome("n1", "", Level.WARNING, 2, 1)
        val tn = NormalOutcome("n2", "", Level.CAUTION, 2, 0)
        // (0.5 + 1 + 0.5(사기 비율 2/4) + 0) / 4
        close((0.5 + 1.0 + 0.5) / 4, Metrics.erde(listOf(hit, miss), listOf(fp, tn), 5)!!)
    }

    @Test fun `중앙값`() {
        assertEquals(2.0, Metrics.median(listOf(3, 1, 2)))
        assertEquals(2.5, Metrics.median(listOf(4, 1, 2, 3)))
        assertNull(Metrics.median(emptyList()))
    }

    @Test fun `금전 지점 CSV 읽기`() {
        val f = kotlin.io.path.createTempFile(suffix = ".csv").toFile()
        f.writeText("﻿case_id,first_suggest,first_intent_before,first_transfer_before,transfer_seen,source\nx,3,5,7,Y,세 모델 일치\n")
        val p = Loader.loadPoints(f)["x"]!!
        assertEquals(listOf(3, 5, 7), listOf(p.firstSuggest, p.firstIntentBefore, p.firstTransferBefore))
        assertTrue(p.transferSeen)
        f.delete()
    }

    @Test fun `인자 읽기`() {
        val m = parseArgs(arrayOf("--input", "a", "--input", "b", "--eval-set", "--out", "o"))
        assertEquals(listOf("a", "b"), m["input"])
        assertEquals(emptyList(), m["eval-set"])
        assertEquals(listOf("o"), m["out"])
    }
}
