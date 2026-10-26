package securityapp.eval

import securityapp.engine.Level
import securityapp.engine.Message
import securityapp.engine.Signal

/**
 * 재생 결과: 대화 하나 × "나"로 놓은 사람 하나.
 * @property levels 넣은 메시지마다 (seq, 그때까지 모든 방 중 가장 높은 단계)
 * @property signals 상대 메시지마다 행위 감지 신호
 * @property firstLevelRoom 단계마다 처음 오른 방
 */
data class ReplayResult(
    val conversationId: String,
    val userSender: String?,
    val levels: List<Pair<Int, Level>>,
    val signals: Map<Int, Set<Signal>>,
    val counterpartSeqs: List<Int>,
    val firstLevelRoom: Map<Level, String>,
) {
    fun firstSeq(level: Level): Int? = levels.firstOrNull { it.second >= level }?.first
    val maxLevel: Level get() = levels.maxOfOrNull { it.second } ?: Level.OBSERVE
}

object Replay {
    /**
     * @param includeUser false(기본)면 "나"의 메시지는 엔진에 넣지 않는다 (앱은 받은 알림만 봄, 설계 4장)
     * @return "나"가 정해진 대화는 결과 1개, 정해지지 않은 대화(AI-Hub)는 화자마다 1개씩
     */
    fun run(method: Method, conv: Conversation, includeUser: Boolean = false): List<ReplayResult> =
        if (conv.userUnknown) conv.senders.map { runAs(method, conv, it, includeUser) }
        else listOf(runAs(method, conv, null, includeUser))

    private fun runAs(method: Method, conv: Conversation, userSender: String?, includeUser: Boolean): ReplayResult {
        val run = method.newRun()
        val roomLevel = HashMap<String, Level>()
        val firstRoom = LinkedHashMap<Level, String>()
        val levels = ArrayList<Pair<Int, Level>>()
        val signals = LinkedHashMap<Int, Set<Signal>>()
        val counterpart = ArrayList<Int>()
        for (m in conv.messages) {
            if (m.voice) continue
            val isUser = if (userSender != null) m.sender == userSender else m.isUser == true
            if (isUser && !includeUser) continue
            val msg = Message(
                room = m.room,
                sender = if (isUser) "나" else m.sender,
                text = m.text,
                isUser = isUser,
                isGroup = Loader.groupFlag(m.room, conv.multiParty),
            )
            val (level, sig) = run.feed(msg)
            roomLevel[m.room] = maxOf(roomLevel[m.room] ?: Level.OBSERVE, level)
            for (lv in Level.entries) if (lv > Level.OBSERVE && level >= lv) firstRoom.putIfAbsent(lv, m.room)
            if (!isUser) { counterpart += m.seq; signals[m.seq] = sig }
            levels += m.seq to roomLevel.values.max()
        }
        return ReplayResult(conv.id, userSender, levels, signals, counterpart, firstRoom)
    }
}
