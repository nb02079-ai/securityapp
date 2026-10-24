package securityapp.eval

import securityapp.engine.Level
import securityapp.engine.Message
import securityapp.engine.RuleEngine
import securityapp.engine.Signal
import securityapp.engine.acts.ActDetector
import securityapp.engine.acts.RoomContext
import securityapp.engine.flow.FlowConfig
import securityapp.engine.normalize.NormalizedText

/**
 * 비교할 세 방식 (docs/stage2_engine_design.md 5장). 대화 하나마다 [newRun]으로 새로 만들어
 * 메시지를 하나씩 넣고, 메시지마다 그 방의 단계를 돌려받는다.
 */
interface Method {
    val name: String
    fun newRun(): Run

    interface Run {
        /** 메시지 하나를 넣고 그 방의 단계와, 행위 감지 신호(있는 방식만)를 돌려준다 */
        fun feed(message: Message): Pair<Level, Set<Signal>>
    }
}

/**
 * ① 단어 기준선 (plan.md 7.2): 상대 메시지에 금전 단어가 하나라도 나오면 그 방에 경고.
 * 단어 목록은 plan.md 7.2에 적힌 다섯 개 그대로이며 평가 뒤에 바꾸지 않는다 (설계 1장 "비교의 공정함").
 * 띄어쓰기·기호 끼워 넣기는 엔진과 같은 정규화로 없앤다.
 */
class WordBaseline : Method {
    override val name = "단어 기준선"

    override fun newRun() = object : Method.Run {
        val warned = HashSet<String>()
        override fun feed(message: Message): Pair<Level, Set<Signal>> {
            if (!message.isUser && WORDS.any { it in NormalizedText.of(message.text).compact }) warned += message.room
            return (if (message.room in warned) Level.WARNING else Level.OBSERVE) to emptySet()
        }
    }

    companion object {
        val WORDS = listOf("송금", "입금", "계좌", "투자", "수익")
    }
}

/** ② 행위 단독: 행위 감지가 신호를 하나라도 찾으면 그 방에 경고 (R2 친밀감 쌓기는 맥락 전용이라 제외) */
class ActsOnly : Method {
    override val name = "행위 단독"

    override fun newRun() = object : Method.Run {
        val detector = ActDetector()
        val rooms = HashMap<String, RoomContext>()
        val warned = HashSet<String>()
        override fun feed(message: Message): Pair<Level, Set<Signal>> {
            val ctx = rooms.getOrPut(message.room) { RoomContext() }
            val r = detector.detect(message, ctx)
            detector.record(message, r, ctx)
            if (r.signals.any { !it.isContextOnly }) warned += message.room
            return (if (message.room in warned) Level.WARNING else Level.OBSERVE) to r.signals
        }
    }
}

/** ③ 행위 + 흐름: 엔진 그대로 ([RuleEngine]) */
class ActsAndFlow(private val config: FlowConfig = FlowConfig()) : Method {
    override val name = "행위 + 흐름"

    override fun newRun() = object : Method.Run {
        val engine = RuleEngine(config)
        override fun feed(message: Message): Pair<Level, Set<Signal>> {
            val j = engine.onMessage(message)
            return j.level to j.detections.map { it.signal }.toSet()
        }
    }
}
