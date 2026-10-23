package securityapp.eval

import securityapp.engine.Message
import securityapp.engine.NoopEngine

/**
 * 재생 평가기 입구. 지금은 골격 확인용이며, 작업 2-5에서
 * 평가 세트 읽기·기준선·지표 계산을 붙인다 (docs/stage2_engine_design.md 5·6장).
 */
fun main(args: Array<String>) {
    val engine = NoopEngine()
    val j = engine.onMessage(Message(room = "시험", sender = "상대", text = "골격 확인"))
    println("securityapp eval 골격 동작: ${j.level}")
}
