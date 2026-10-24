package securityapp.eval

import securityapp.engine.Level
import securityapp.engine.Signal
import securityapp.engine.flow.FlowConfig
import securityapp.engine.flow.FlowJudge
import java.io.File

/**
 * 진단: 행위 감지 결과 대신 최종 라벨의 신호를 흐름 판정에 그대로 넣었을 때의 결과.
 * 흐름 판정 규칙의 한계와 행위 감지의 한계를 나눠 보기 위한 것이며, 규칙을 바꾸지 않는다
 * (docs/stage2_results_v1.md 3.2). 상대 메시지만, 방 단위.
 *
 * 사용법: --input <사기 .jsonl 폴더> --labels <final_messages.csv> --points <final_points.csv> [--eval-set]
 */
fun main(args: Array<String>) {
    val o = parseArgs(args)
    val input = o["input"]?.singleOrNull(); val lab = o["labels"]?.singleOrNull(); val pts = o["points"]?.singleOrNull()
    if (input == null || lab == null || pts == null) {
        System.err.println("사용법: --input <폴더> --labels <csv> --points <csv> [--eval-set]")
        kotlin.system.exitProcess(2)
    }
    if (listOf(input, lab, pts).any { File(it).absoluteFile.normalize().invariantSeparatorsPath.contains("data/eval") } && "eval-set" !in o) {
        System.err.println("[멈춤] 평가 세트가 입력에 있습니다. --eval-set을 붙이세요.")
        kotlin.system.exitProcess(3)
    }
    val labels = Loader.loadSignalLabels(File(lab))
    val points = Loader.loadPoints(File(pts))
    var hit = 0; var n = 0
    for (c in Loader.loadDir(File(input)).filter { it.isScam }) {
        val p = points[c.id] ?: continue
        val rooms = HashMap<String, FlowJudge>()
        var fc: Int? = null; var fw: Int? = null
        for (m in c.messages) {
            if (m.isUser == true) continue
            val sig: Set<Signal> = labels[c.id to m.seq]?.mapNotNull { Signal.fromCode(it) }?.toSet() ?: emptySet()
            val v = rooms.getOrPut(m.room) { FlowJudge(FlowConfig()) }.onCounterpart(sig)
            if (v.level >= Level.CAUTION && fc == null) fc = m.seq
            if (v.level == Level.WARNING && fw == null) fw = m.seq
        }
        val ok = fw != null && fw <= p.firstTransferBefore
        n++; if (ok) hit++
        println("${c.id}\t첫 금전 권유 ${p.firstSuggest}\t첫 송금 직전 ${p.firstTransferBefore}\t첫 주의 ${fc ?: "-"}\t첫 경고 ${fw ?: "-"}\t${if (ok) "O" else "X"}")
    }
    println("정답 신호 + 흐름 판정 v1: 송금 전 경고 $hit/$n")
}
