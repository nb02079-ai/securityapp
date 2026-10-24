package securityapp.engine

import securityapp.engine.acts.ActDetector
import securityapp.engine.acts.RoomContext
import securityapp.engine.flow.FlowConfig
import securityapp.engine.flow.FlowJudge

/**
 * 규칙 기반 판정 엔진 (plan.md 4.3 A안): ① 행위 감지 → ② 흐름 판정, 대화방 단위 (plan.md 4.2.1 v1).
 * 메시지 원문은 저장하지 않는다. 방마다 요약 맥락(RoomContext), 최근 신호 몇 개, 보낸 사람별 직전 신호만 남긴다.
 */
class RuleEngine(private val config: FlowConfig = FlowConfig()) : Engine {
    private class Room(val flow: FlowJudge) {
        val ctx = RoomContext()
        /** 보낸 사람별 직전 글자 메시지의 신호 — 사진만 있는 메시지가 따름 */
        val lastBySender = HashMap<String, Set<Signal>>()
    }

    private val detector = ActDetector()
    private val rooms = HashMap<String, Room>()

    override fun onMessage(message: Message): Judgment {
        val room = rooms.getOrPut(message.room) { Room(FlowJudge(config)) }
        val result = detector.detect(message, room.ctx)
        detector.record(message, result, room.ctx)
        if (message.isUser) {
            return Judgment(message.room, room.flow.current().level, emptyList())
        }
        val signals = if (ActDetector.isPhotoOnly(message.text)) {
            // 기준표 v2.1: 사진만 있는 메시지는 같은 사람의 바로 앞 설명을 따른다 (R1은 감지 층이 붙인 그대로)
            result.signals + (room.lastBySender[message.sender] ?: emptySet())
        } else {
            room.lastBySender[message.sender] = result.signals
            result.signals
        }
        val v = room.flow.onCounterpart(signals)
        return Judgment(message.room, v.level, result.detections, v.reason)
    }

    override fun forget(room: String) {
        rooms.remove(room)
    }
}
