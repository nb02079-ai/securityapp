package securityapp.eval

import securityapp.engine.Level
import securityapp.engine.Signal
import kotlin.math.exp

/** 사기 사례 하나의 결과 (docs/stage2_engine_design.md 6장) */
data class ScamOutcome(
    val caseId: String,
    val note: String,
    val points: MoneyPoints?,
    val firstCaution: Int?,
    val firstWarning: Int?,
    val warningRoom: String?,
    /** 첫 경고까지 엔진에 넣은 상대 메시지 수 (ERDE의 k) */
    val warningK: Int?,
    /** 첫 경고 뒤 첫 송금 직전 메시지까지 남은 상대 메시지 수 (경고가 얼마나 앞섰는지) */
    val leadTransfer: Int?,
    val counterpartCount: Int,
) {
    private fun by(deadline: Int?): Boolean = firstWarning != null && deadline != null && firstWarning <= deadline
    val beforeTransfer: Boolean get() = by(points?.firstTransferBefore)
    val beforeSuggest: Boolean get() = by(points?.firstSuggest)
    val beforeIntent: Boolean get() = by(points?.intentDeadline)
}

/** 일반 대화 하나의 결과. 화자마다 "나"로 놓고 돌린 것 중 가장 높은 단계 */
data class NormalOutcome(
    val id: String,
    val note: String,
    val maxLevel: Level,
    val perspectives: Int,
    val warnedPerspectives: Int,
)

data class SignalScore(val signal: Signal, val tp: Int, val fp: Int, val fn: Int) {
    val precision: Double? get() = if (tp + fp == 0) null else tp.toDouble() / (tp + fp)
    val recall: Double? get() = if (tp + fn == 0) null else tp.toDouble() / (tp + fn)
}

data class Summary(
    val method: String,
    val includeUser: Boolean,
    val scams: List<ScamOutcome>,
    val normals: List<NormalOutcome>,
) {
    val labeledScams: List<ScamOutcome> get() = scams.filter { it.points != null }
    val warnedScams: Int get() = scams.count { it.firstWarning != null }
    val beforeTransfer: Int get() = labeledScams.count { it.beforeTransfer }
    val beforeSuggest: Int get() = labeledScams.count { it.beforeSuggest }
    val beforeIntent: Int get() = labeledScams.count { it.beforeIntent }
    val normalWarned: Int get() = normals.count { it.maxLevel == Level.WARNING }
    val normalCautionOnly: Int get() = normals.count { it.maxLevel == Level.CAUTION }
    val medianLead: Double? get() = Metrics.median(labeledScams.filter { it.beforeTransfer }.mapNotNull { it.leadTransfer })
    fun erde(o: Int): Double? = Metrics.erde(labeledScams, normals, o)
}

object Metrics {
    fun scamOutcome(conv: Conversation, r: ReplayResult, points: MoneyPoints?): ScamOutcome {
        val fw = r.firstSeq(Level.WARNING)
        val k = fw?.let { w -> r.counterpartSeqs.count { it <= w } }
        val lead = if (fw != null && points != null && fw <= points.firstTransferBefore)
            r.counterpartSeqs.count { it > fw && it <= points.firstTransferBefore } else null
        return ScamOutcome(
            caseId = conv.id, note = conv.note, points = points,
            firstCaution = r.firstSeq(Level.CAUTION), firstWarning = fw,
            warningRoom = r.firstLevelRoom[Level.WARNING], warningK = k, leadTransfer = lead,
            counterpartCount = r.counterpartSeqs.size,
        )
    }

    fun normalOutcome(conv: Conversation, rs: List<ReplayResult>): NormalOutcome = NormalOutcome(
        id = conv.id, note = conv.note,
        maxLevel = rs.maxOfOrNull { it.maxLevel } ?: Level.OBSERVE,
        perspectives = rs.size,
        warnedPerspectives = rs.count { it.maxLevel == Level.WARNING },
    )

    /**
     * ERDE_o (eRisk, Losada & Crestani 2016): 대화마다 비용을 매겨 평균.
     *  - 사기, 마감점(첫 송금 직전)까지 경고: 1 − 1/(1 + e^(k − o)), k = 첫 경고까지 넣은 상대 메시지 수
     *  - 사기, 마감점까지 경고 없음 (늦은 경고 포함): 1
     *  - 일반 대화에 경고: 사기 비율 (전체 중 사기 사례 수 / 전체 대화 수)
     *  - 일반 대화에 경고 없음: 0
     * o는 평가 전에 5와 10으로 정해 둔다 (eRisk의 ERDE5·ERDE50 관례를 대화 길이에 맞춤).
     */
    fun erde(scams: List<ScamOutcome>, normals: List<NormalOutcome>, o: Int): Double? {
        val total = scams.size + normals.size
        if (total == 0 || scams.isEmpty()) return null
        val cFp = scams.size.toDouble() / total
        val scamCost = scams.sumOf { s ->
            if (s.beforeTransfer) latency(s.warningK!!, o) else 1.0
        }
        val normalCost = normals.count { it.maxLevel == Level.WARNING } * cFp
        return (scamCost + normalCost) / total
    }

    fun latency(k: Int, o: Int): Double = 1.0 - 1.0 / (1.0 + exp((k - o).toDouble()))

    fun median(xs: List<Int>): Double? {
        if (xs.isEmpty()) return null
        val s = xs.sorted()
        return if (s.size % 2 == 1) s[s.size / 2].toDouble() else (s[s.size / 2 - 1] + s[s.size / 2]) / 2.0
    }

    /** 최종 라벨이 있는 상대 메시지마다 신호를 비교 (R2 포함 17개 모두) */
    fun signalScores(results: List<Pair<String, ReplayResult>>, labels: Map<Pair<String, Int>, Set<String>>): List<SignalScore> {
        val tp = HashMap<Signal, Int>(); val fp = HashMap<Signal, Int>(); val fn = HashMap<Signal, Int>()
        for ((caseId, r) in results) for ((seq, got) in r.signals) {
            val want = labels[caseId to seq]?.mapNotNull { Signal.fromCode(it) }?.toSet() ?: continue
            for (s in got) if (s in want) tp.merge(s, 1, Int::plus) else fp.merge(s, 1, Int::plus)
            for (s in want) if (s !in got) fn.merge(s, 1, Int::plus)
        }
        return Signal.entries.map { SignalScore(it, tp[it] ?: 0, fp[it] ?: 0, fn[it] ?: 0) }
    }
}
