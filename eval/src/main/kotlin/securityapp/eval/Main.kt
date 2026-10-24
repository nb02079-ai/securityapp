package securityapp.eval

import java.io.File

/**
 * 재생 평가기 (작업 2-5, docs/stage2_engine_design.md 5·6장).
 *
 * 사용법 (gradlew.bat :eval:run --args="…")
 *   --input <폴더>     .jsonl 대화 폴더 (여러 번 줄 수 있음). meta의 label/kind로 사기·일반을 나눔
 *   --points <csv>     금전 지점 라벨 (final_points.csv). 없으면 경고 여부만 셈
 *   --labels <csv>     메시지별 신호 라벨 (final_messages.csv). 있으면 신호 감지 정확도 계산
 *   --out <폴더>       결과 폴더 (report.md, cases.csv, normals.csv, signals.csv)
 *   --title <글>       보고서 제목
 *   --eval-set         평가 세트(data/eval/)를 입력으로 쓸 때 반드시 붙임. 규칙을 engine-v1로 고정한 뒤에만 (설계 1장)
 */
fun main(args: Array<String>) {
    val opts = parseArgs(args)
    val inputs = opts["input"].orEmpty()
    val out = opts["out"]?.singleOrNull()
    if (inputs.isEmpty() || out == null) {
        System.err.println("사용법: --input <폴더> [--input …] --out <폴더> [--points csv] [--labels csv] [--title 글] [--eval-set]")
        kotlin.system.exitProcess(2)
    }
    val touchesEval = (inputs + opts["points"].orEmpty() + opts["labels"].orEmpty())
        .any { File(it).absoluteFile.normalize().invariantSeparatorsPath.contains("data/eval") }
    if (touchesEval && "eval-set" !in opts) {
        System.err.println("[멈춤] 평가 세트(data/eval/)가 입력에 있습니다. 규칙을 고정(태그 engine-v1)한 뒤 --eval-set을 붙여 한 번만 돌립니다.")
        kotlin.system.exitProcess(3)
    }

    val convs = inputs.flatMap { Loader.loadDir(File(it)) }
    val points = opts["points"]?.singleOrNull()?.let { Loader.loadPoints(File(it)) }
    val labels = opts["labels"]?.singleOrNull()?.let { Loader.loadSignalLabels(File(it)) }
    points?.keys?.minus(convs.filter { it.isScam }.map { it.id }.toSet())?.takeIf { it.isNotEmpty() }?.let {
        System.err.println("[경고] 금전 지점 라벨은 있는데 대화가 없는 사례: $it")
    }

    val methods = listOf(WordBaseline(), ActsOnly(), ActsAndFlow())
    val summaries = ArrayList<Summary>()
    var signalScores: List<SignalScore>? = null
    for (includeUser in listOf(false, true)) for (m in methods) {
        val scams = ArrayList<ScamOutcome>()
        val normals = ArrayList<NormalOutcome>()
        val forSignals = ArrayList<Pair<String, ReplayResult>>()
        for (c in convs) {
            val rs = Replay.run(m, c, includeUser)
            if (c.isScam) {
                scams += Metrics.scamOutcome(c, rs.single(), points?.get(c.id))
                forSignals += c.id to rs.single()
            } else normals += Metrics.normalOutcome(c, rs)
        }
        summaries += Summary(m.name, includeUser, scams, normals)
        if (labels != null && includeUser && m is ActsAndFlow) signalScores = Metrics.signalScores(forSignals, labels)
    }

    val title = opts["title"]?.singleOrNull() ?: "재생 평가 결과"
    Report.write(File(out), title, inputs, summaries, signalScores)
    for (s in summaries.filter { !it.includeUser }) {
        val scamPart = if (s.labeledScams.isNotEmpty()) "송금 전 경고 ${s.beforeTransfer}/${s.labeledScams.size}" else "사기 경고 ${s.warnedScams}/${s.scams.size}"
        println("${s.method}: $scamPart, 일반 대화 경고 ${s.normalWarned}/${s.normals.size}, 주의 ${s.normalCautionOnly}/${s.normals.size}")
    }
    println("결과: ${File(out).absolutePath}")
}

/** "--key value" 모양 인자. 값 없는 키(--eval-set)는 빈 목록 */
fun parseArgs(args: Array<String>): Map<String, List<String>> {
    val m = LinkedHashMap<String, MutableList<String>>()
    var i = 0
    while (i < args.size) {
        val a = args[i]
        require(a.startsWith("--")) { "알 수 없는 인자: $a" }
        val key = a.removePrefix("--")
        val list = m.getOrPut(key) { ArrayList() }
        if (i + 1 < args.size && !args[i + 1].startsWith("--")) { list += args[i + 1]; i += 2 } else i++
    }
    return m
}
