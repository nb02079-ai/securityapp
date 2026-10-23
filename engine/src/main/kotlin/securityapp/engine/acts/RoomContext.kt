package securityapp.engine.acts

/**
 * 행위 감지가 참고하는 대화방의 지난 흐름. 메시지 내용 자체는 저장하지 않고, 판단에 필요한 요약만 남긴다
 * (plan.md 4.7.2 "덜 남기기").
 *
 * 맥락이 필요한 신호: R1(단체방인지, 운영자인지), G2(돈 이야기가 이미 나왔는지), G3(앞선 요구 금액), G4("나"의 거절)
 */
class RoomContext {
    /** 상대방 메시지 수 (방에 들어온 순서대로) */
    var counterpartCount = 0
        private set

    /** 보낸 사람별 상대방 메시지 수 */
    private val senderCounts = LinkedHashMap<String, Int>()

    /** 돈과 관련된 행위(돈 요구·수익 약속·선보상)가 이 방에서 이미 나왔는지 */
    var moneyTalkStarted = false
        private set

    /** 돈 이야기 없이 오간 상대방 메시지 수 (G2 판단용) */
    var nonMoneyCounterpartBefore = 0
        private set

    /** 지금까지 상대가 요구·권유한 가장 큰 금액 (원) */
    var maxDemandAmount = 0L
        private set

    /** 가장 최근 "나"의 메시지가 거절·망설임이었는지. 앱에서는 "나"의 메시지가 들어오지 않으므로 항상 false */
    var userJustRefused = false
        private set

    /** 단체방으로 볼지: 상대방 쪽 보낸 사람이 둘 이상 */
    val isGroup: Boolean get() = senderCounts.size >= 2

    /** 방을 연 사람(가장 먼저 말한 상대)을 운영자로 본다 */
    val operator: String? get() = senderCounts.keys.firstOrNull()

    fun isOperator(sender: String) = sender == operator

    fun knownSenders(): Set<String> = senderCounts.keys

    internal fun recordUser(refused: Boolean) {
        userJustRefused = refused
    }

    internal fun recordCounterpart(sender: String, moneyTalk: Boolean, demandAmounts: List<Long>) {
        counterpartCount++
        senderCounts[sender] = (senderCounts[sender] ?: 0) + 1
        if (moneyTalk) moneyTalkStarted = true else if (!moneyTalkStarted) nonMoneyCounterpartBefore++
        demandAmounts.maxOrNull()?.let { if (it > maxDemandAmount) maxDemandAmount = it }
        userJustRefused = false
    }

    /** 단체방 판단에 쓰기 위해 보낸 사람만 미리 알린다 (첫 메시지에서 운영자를 정하려고) */
    internal fun noteSender(sender: String) {
        if (sender !in senderCounts) senderCounts[sender] = 0
    }
}
