package securityapp.engine.flow

import securityapp.engine.Category
import securityapp.engine.Level
import securityapp.engine.Signal

/**
 * ② 흐름 판정 (plan.md 4.2.1·4.2.3): 대화방마다 최근 상대방 메시지들의 신호를 모아 관찰 / 주의 / 경고를 정한다.
 *
 * 판정 원칙 (plan.md 4.2.3)
 *  1. 신호 하나로는 경고하지 않는다.
 *  2. 경고는 "요구" 신호 + 다른 분류 신호의 조합이 있을 때만.
 *  4. 오래된 신호는 메시지 수 기준으로 약해진다 (평가 데이터에 시각이 없음) → 최근 [FlowConfig.window]개 상대 메시지만 본다.
 *  5. 친밀감 쌓기(R2)는 맥락 전용 — 조합에 세지 않는다.
 *
 * 규칙 v1 (docs/stage2_engine_design.md 4.1)
 *  - 주의: 창 안에 요구(D) 신호 1개 이상 + 다른 분류(P·G·R1) 신호 1개 이상
 *    단, 요구가 계좌 안내(D4)뿐이면 시간 압박(P3)·회피(P4)만으로는 주의를 내지 않는다
 *  - 경고: 주의 조건 + 돈 요구(D2·D3·D5) + (D4를 뺀 서로 다른 신호가 [FlowConfig.minDistinct]개 이상 또는 강한 신호(G3·G4·D5·D6))
 *  - 계좌 안내(D4)는 정산·수납·거래에도 흔해서 "돈 요구"로도, 신호 수로도 세지 않는다 (개발 세트 근거, docs/dev/03_flow_v1.md)
 *  - 한 번 오른 단계는 내려가지 않는다 ([FlowConfig.sticky]). 사용자가 직접 "괜찮아요"로 내려야 함 (앱 단계)
 */
data class FlowConfig(
    val window: Int = 8,
    val minDistinct: Int = 3,
    val sticky: Boolean = true,
    /** 경고의 "서로 다른 신호 수"에 계좌 안내(D4)를 세는지 — 개발 세트로 false (정상 지인 투자 대화의 경고 1건 제거) */
    val countAccount: Boolean = false,
    /** 요구가 계좌 안내(D4)뿐일 때 시간 압박(P3)·회피(P4)만으로도 주의를 낼지 — 개발 세트로 false (회비 걷기 대화의 주의 1건 제거) */
    val accountWithPressure: Boolean = false,
)

class FlowJudge(private val config: FlowConfig = FlowConfig()) {
    data class Verdict(val level: Level, val active: Set<Signal>, val reason: String?)

    private val recent = ArrayDeque<Set<Signal>>()
    private var level = Level.OBSERVE

    val currentLevel: Level get() = level

    /** 상대방 메시지 하나의 신호를 넣고 판정을 돌려준다 */
    fun onCounterpart(signals: Set<Signal>): Verdict {
        recent.addLast(signals)
        while (recent.size > config.window) recent.removeFirst()
        val active = recent.flatten().filterNot { it.isContextOnly }.toSet()
        val computed = evaluate(active)
        val before = level
        level = if (config.sticky) maxOf(level, computed) else computed
        val reason = if (level > before) explain(active, level) else null
        return Verdict(level, active, reason)
    }

    /** "나"의 메시지는 판정을 바꾸지 않는다 (앱에서는 들어오지도 않음) */
    fun current(): Verdict = Verdict(level, recent.flatten().filterNot { it.isContextOnly }.toSet(), null)

    private fun evaluate(active: Set<Signal>): Level {
        val demand = active.any { it.category == Category.DEMAND }
        val other = active.any { it.category != Category.DEMAND }
        if (!(demand && other)) return Level.OBSERVE
        val accountOnly = active.none { it.category == Category.DEMAND && it != Signal.D4 }
        if (accountOnly && !config.accountWithPressure &&
            active.none { it.category != Category.DEMAND && it !in WEAK_WITH_ACCOUNT }) return Level.OBSERVE
        val money = active.any { it in MONEY }
        val strong = active.any { it in STRONG }
        val distinct = if (config.countAccount) active.size else active.count { it != Signal.D4 }
        return if (money && (distinct >= config.minDistinct || strong)) Level.WARNING else Level.CAUTION
    }

    private fun explain(active: Set<Signal>, level: Level): String {
        val names = active.sortedBy { it.ordinal }.joinToString(", ") { it.label }
        return when (level) {
            Level.WARNING -> "돈 요구와 함께 여러 위험 신호가 이어졌습니다: $names"
            Level.CAUTION -> "요구와 설득·진행 신호가 함께 나타났습니다: $names"
            Level.OBSERVE -> names
        }
    }

    companion object {
        /** 경고 조건의 "돈 요구" (D4 계좌 안내만으로는 아님) */
        val MONEY = setOf(Signal.D2, Signal.D3, Signal.D5)
        /** 돈 요구와 함께면 신호 수와 상관없이 경고: 금액 증가·붙잡기·출금 조건·비밀 유지 */
        val STRONG = setOf(Signal.G3, Signal.G4, Signal.D5, Signal.D6)
        /** 계좌 안내와 함께 나와도 정상 정산·수납에 흔한 신호 */
        val WEAK_WITH_ACCOUNT = setOf(Signal.P3, Signal.P4)
    }
}
