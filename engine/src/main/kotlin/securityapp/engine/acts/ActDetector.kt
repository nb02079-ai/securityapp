package securityapp.engine.acts

import securityapp.engine.Detection
import securityapp.engine.Message
import securityapp.engine.Signal
import securityapp.engine.normalize.Amounts
import securityapp.engine.normalize.NormalizedText

/**
 * ① 행위 감지 (plan.md 4.2.1): 메시지 하나 → 신호 집합과 근거 구간.
 *
 * 대부분의 신호는 그 메시지만 보고 정하고, 맥락이 필요한 신호(R1·G2·G3·G4)는 [RoomContext]를 참고한다.
 * 감지가 끝나면 [record]로 맥락을 갱신해야 다음 메시지 판단에 반영된다 (흐름 판정 층이 부름).
 */
class ActDetector {
    data class Result(
        val detections: List<Detection>,
        val demandAmounts: List<Long>,
        /** 돈 이야기가 나온 메시지인지 (돈 요구·수익 약속·선보상, 또는 돈 관련 낱말) — G2 판단용 */
        val moneyTalk: Boolean = false,
    ) {
        val signals: Set<Signal> get() = detections.map { it.signal }.toSet()
    }

    fun detect(message: Message, ctx: RoomContext): Result {
        if (message.isUser) return Result(emptyList(), emptyList())
        ctx.noteSender(message.sender, message.isGroup)
        val n = NormalizedText.of(message.text)
        val c = n.compact
        val found = LinkedHashMap<Signal, IntRange>()

        fun hit(signal: Signal, re: Regex): Boolean {
            val m = re.find(c) ?: return false
            found.putIfAbsent(signal, n.toOriginal(m.range))
            return true
        }

        // 사진·파일만 있는 메시지는 글자 신호가 없다. 기준표 v2.1의 "앞 설명을 따름"은 흐름 층에서 처리.
        if (isPhotoOnly(message.text)) {
            if (ctx.isGroup && !ctx.isOperator(message.sender)) found[Signal.R1] = message.text.indices
            return Result(found.map { Detection(it.key, it.value) }, emptyList())
        }

        // ── D 요구 ──
        hit(Signal.D1, Lexicon.D1)
        val sellOnly = Lexicon.D2_SELL.containsMatchIn(c) && !Lexicon.D2_BUY.containsMatchIn(c)
        if (!sellOnly && !hit(Signal.D2, Lexicon.D2) && Lexicon.D2_CONTEXT.containsMatchIn(c)) {
            hit(Signal.D2, Lexicon.D2_GENERIC)
        }
        // [v1.1] 투자 이야기가 나온 방에서 금액 + 시작·준비·맞춤은 투자금 요구
        if (!sellOnly && !found.containsKey(Signal.D2) && (ctx.investTalk || Lexicon.G2_TRIGGER.containsMatchIn(c)) &&
            Lexicon.D2_AMOUNT_VERB.containsMatchIn(c) && !Lexicon.G1.containsMatchIn(c) && !Lexicon.D2_DONE.containsMatchIn(c) &&
            Amounts.extract(message.text).isNotEmpty()) {
            Lexicon.D2_AMOUNT_VERB.find(c)?.let { found.putIfAbsent(Signal.D2, n.toOriginal(it.range)) }
        }
        val d5 = hit(Signal.D5, Lexicon.D5)
        // 출금하려고 내는 돈이면 D5만 (기준표 D3 "붙이지 않는 경우")
        if (!d5) hit(Signal.D3, Lexicon.D3)
        if (!hit(Signal.D4, Lexicon.D4)) {
            Lexicon.D4_ACCOUNT_SHAPE.find(message.text)?.let { found.putIfAbsent(Signal.D4, it.range) }
        }
        hit(Signal.D6, Lexicon.D6)
        if (!Lexicon.D7_AMOUNT_ONLY.containsMatchIn(c) && !Lexicon.D7_NOT.containsMatchIn(c)) hit(Signal.D7, Lexicon.D7)

        // ── P 설득 ──
        if (!Lexicon.P1_HEDGE.containsMatchIn(c)) {
            // [v1.1] 부정한 보장("보장하지 않습니다")은 같은 길이의 빈칸으로 바꿔 위치를 지키고 다시 찾음
            val cP1 = Lexicon.P1_NEG.replace(c) { " ".repeat(it.value.length) }
            Lexicon.P1.find(cP1)?.let { found.putIfAbsent(Signal.P1, n.toOriginal(it.range)) }
        }
        hit(Signal.P2, Lexicon.P2)
        hit(Signal.P3, Lexicon.P3)
        hit(Signal.P4, Lexicon.P4)

        // ── G 진행 ──
        if (!Lexicon.G1_FUTURE.containsMatchIn(c)) hit(Signal.G1, Lexicon.G1)

        val moneyDemand = found.keys.any { it.isMoneyDemand }
        val amounts = if (moneyDemand) Amounts.extract(message.text) else emptyList()
        // G3: 대출 권유·큰 금액 유리 규칙, 또는 앞서 요구한 금액보다 큰 금액을 요구
        if (!hit(Signal.G3, Lexicon.G3_LOAN) && !hit(Signal.G3, Lexicon.G3_TIER)) {
            val maxNow = amounts.maxOrNull()
            val risingInOne = amounts.size >= 3 && amounts.zipWithNext().all { (a, b) -> b > a }
            if (maxNow != null && ((ctx.maxDemandAmount > 0 && maxNow > ctx.maxDemandAmount) || risingInOne)) {
                found.putIfAbsent(Signal.G3, message.text.indices)
            }
        }
        // G4: "나"의 거절 뒤 다시 돈을 요구하거나, 그만두지 못하게 붙잡는 말
        val holdOn = Lexicon.G4.containsMatchIn(c)
        if (holdOn || (ctx.userJustRefused && moneyDemand)) {
            found.putIfAbsent(Signal.G4, Lexicon.G4.find(c)?.let { n.toOriginal(it.range) } ?: message.text.indices)
        }
        // G2: 돈과 상관없던 대화가 이 메시지에서 돈 이야기로 넘어감 (방마다 한 번)
        // 계좌 안내(D4)만으로는 "돈 이야기로 넘어감"으로 보지 않음 (정산·거래에도 흔함)
        val moneyNow = found.keys.any { it == Signal.D2 || it == Signal.D3 || it == Signal.D5 } ||
            found.containsKey(Signal.P1) || found.containsKey(Signal.G1) || Lexicon.G2_TRIGGER.containsMatchIn(c)
        if (moneyNow && !ctx.moneyTalkStarted && ctx.nonMoneyCounterpartBefore >= G2_MIN_BEFORE) {
            found.putIfAbsent(Signal.G2, Lexicon.G2_TRIGGER.find(c)?.let { n.toOriginal(it.range) } ?: message.text.indices)
        }

        // ── R 관계 ──
        if (ctx.isGroup && !ctx.isOperator(message.sender)) hit(Signal.R1, Lexicon.R1)
        hit(Signal.R2, Lexicon.R2)

        return Result(found.map { Detection(it.key, it.value) }, amounts, moneyNow)
    }

    /** 감지 결과로 방 맥락을 갱신한다. 상대 메시지는 [result]와 함께, "나"의 메시지는 거절 여부만 남긴다. */
    fun record(message: Message, result: Result, ctx: RoomContext) {
        if (message.isUser) {
            ctx.recordUser(Lexicon.USER_REFUSAL.containsMatchIn(NormalizedText.of(message.text).compact))
        } else {
            ctx.recordCounterpart(message.sender, result.moneyTalk, result.demandAmounts)
            if (Lexicon.G2_TRIGGER.containsMatchIn(NormalizedText.of(message.text).compact)) ctx.investTalk = true
        }
    }

    companion object {
        /** G2: 돈 이야기 전에 이만큼의 상대 메시지가 오가야 "갑자기 넘어감"으로 본다. 개발 세트로 다시 정함 */
        const val G2_MIN_BEFORE = 2
        private val photoOnly = Regex("^\\s*\\[(사진|파일|동영상|이모티콘)\\]\\s*$")
        /** 글자 없이 사진·파일만 보낸 메시지인지 (기준표 v2.1: 앞 설명을 따름 → 흐름 층에서 처리) */
        fun isPhotoOnly(text: String): Boolean = photoOnly.matches(text)
    }
}
