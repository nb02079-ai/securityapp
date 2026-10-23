package securityapp.engine

/**
 * 판정 엔진의 바깥 모양. 메시지가 들어올 때마다 [onMessage]를 부르면 그 대화방의 판단을 돌려준다.
 * 행위 감지(acts)와 흐름 판정(flow)은 작업 2-3·2-4에서 채운다 (docs/stage2_engine_design.md 7장).
 */
interface Engine {
    fun onMessage(message: Message): Judgment

    /** 사용자가 대화방을 지우거나 감시를 끌 때 그 방의 상태를 버린다 */
    fun forget(room: String)
}

/** 아무것도 감지하지 않는 엔진. 골격과 재생 평가기를 먼저 시험하기 위한 자리 표시. */
class NoopEngine : Engine {
    override fun onMessage(message: Message) = Judgment(message.room, Level.OBSERVE, emptyList())
    override fun forget(room: String) {}
}
