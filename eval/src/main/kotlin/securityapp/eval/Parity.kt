package securityapp.eval

import securityapp.scorer.OnnxBackend
import securityapp.scorer.ScamModel
import securityapp.scorer.TextPrep
import securityapp.scorer.WordPieceTokenizer
import java.io.File
import kotlin.math.abs
import kotlin.system.exitProcess

/**
 * 파이썬과 Kotlin 판정기가 같은지 확인 (5단계-2).
 * 입력: tools/model/make_parity_vectors.py 가 만든 vectors.jsonl
 *   한 줄 = 한 관점: {"conv","persp","msgs":[상대 메시지…],"items":[{"k","text","ids","score"}…]}
 * 확인 세 가지:
 *   1. 글 정리   TextPrep.prefixText(msgs, k) == text
 *   2. 토큰      tokenizer.encode(text) == ids
 *   3. 점수      OnnxBackend(ids) 와 score 차이, 문턱 판정이 같은가 (--onnx 를 줄 때만)
 * 실행: gradlew :eval:parity --args="--vectors <파일> --tokenizer <tokenizer.json> --onnx <model_int8.onnx>"
 */
fun main(args: Array<String>) {
    val o = HashMap<String, String>()
    var i = 0
    while (i < args.size) {
        require(args[i].startsWith("--") && i + 1 < args.size) { "인자 형식: --이름 값 (${args[i]})" }
        o[args[i].removePrefix("--")] = args[i + 1]; i += 2
    }
    val vectors = o["vectors"]; val tokPath = o["tokenizer"]
    if (vectors == null || tokPath == null) {
        System.err.println("사용법: --vectors <vectors.jsonl> --tokenizer <tokenizer.json> [--onnx <model_int8.onnx>] [--threshold 0.843446001] [--tol 0.001]")
        exitProcess(2)
    }
    val th = o["threshold"]?.toDouble() ?: ScamModel.FROZEN_THRESHOLD
    val tol = o["tol"]?.toDouble() ?: 1e-3
    val tok = WordPieceTokenizer.fromJson(File(tokPath).readText(Charsets.UTF_8))
    val backend = o["onnx"]?.let { OnnxBackend(it, o["threads"]?.toInt() ?: 1) }
    backend?.let { println("ONNX 입력: ${it.inputNames}") }

    var n = 0; var textBad = 0; var idsBad = 0; var scored = 0; var decBad = 0; var overTol = 0
    var maxDiff = 0.0; var nanos = 0L
    val shown = ArrayList<String>()
    fun show(s: String) { if (shown.size < 15) shown.add(s) }

    File(vectors).forEachLine(Charsets.UTF_8) { line ->
        if (line.isBlank()) return@forEachLine
        val row = Json.obj(line)
        @Suppress("UNCHECKED_CAST") val msgs = (row["msgs"] as List<Any?>).map { it as String }
        @Suppress("UNCHECKED_CAST") val items = row["items"] as List<Map<String, Any?>>
        val where = "${row["conv"]} ${row["persp"]}"
        for (it in items) {
            n++
            val k = (it["k"] as Long).toInt()
            val pyText = it["text"] as String
            val ktText = TextPrep.prefixText(msgs, k)
            if (ktText != pyText) {
                textBad++
                val d = ktText.zip(pyText).indexOfFirst { (a, b) -> a != b }.let { x -> if (x < 0) minOf(ktText.length, pyText.length) else x }
                show("[글] $where k=$k 위치 $d: kt=${esc(ktText.drop(maxOf(0, d - 10)).take(30))} / py=${esc(pyText.drop(maxOf(0, d - 10)).take(30))}")
            }
            @Suppress("UNCHECKED_CAST") val pyIds = (it["ids"] as List<Any?>).map { x -> (x as Long).toInt() }
            val ktIds = tok.encode(pyText).toList()
            if (ktIds != pyIds) {
                idsBad++
                val d = ktIds.zip(pyIds).indexOfFirst { (a, b) -> a != b }.let { x -> if (x < 0) minOf(ktIds.size, pyIds.size) else x }
                show("[토큰] $where k=$k 길이 kt=${ktIds.size} py=${pyIds.size}, 위치 $d: kt=${ktIds.drop(d).take(5)} py=${pyIds.drop(d).take(5)}")
            }
            val py = it["score"] as? Double
            if (backend != null && py != null) {
                val t0 = System.nanoTime()
                val s = backend(tok.encode(pyText))
                nanos += System.nanoTime() - t0
                scored++
                val diff = abs(s - py)
                if (diff > maxDiff) maxDiff = diff
                if (diff > tol) overTol++
                if ((s >= th) != (py >= th)) {
                    decBad++
                    show("[판정] $where k=$k kt=${"%.6f".format(s)} py=${"%.6f".format(py)}")
                }
            }
        }
    }
    backend?.close()

    println("위치 ${n}개")
    println("1. 글 정리 다름: $textBad")
    println("2. 토큰 다름:    $idsBad")
    if (scored > 0) {
        println("3. 점수 비교 ${scored}개: 최대 차이 ${"%.2e".format(maxDiff)}, 허용치(${tol}) 넘음 $overTol, 문턱 $th 판정 다름 $decBad")
        println("   Kotlin 점수 계산 위치당 ${"%.1f".format(nanos / 1e6 / scored)}ms (토큰 나누기 포함, CPU 1스레드 기본)")
    } else println("3. 점수 비교 안 함 (--onnx 없음 또는 벡터에 점수 없음)")
    shown.forEach { println("  $it") }
    val ok = textBad == 0 && idsBad == 0 && decBad == 0 && overTol == 0
    println(if (ok) "→ 같음" else "→ 다름 있음")
    exitProcess(if (ok) 0 else 1)
}

private fun esc(s: String) = s.map { c -> if (c.code < 0x20 || c.code in 0x7F..0x9F) "\\u%04x".format(c.code) else c.toString() }.joinToString("")
