package securityapp.scorer

import ai.onnxruntime.OnnxTensor
import ai.onnxruntime.OrtEnvironment
import ai.onnxruntime.OrtSession
import java.nio.LongBuffer
import kotlin.math.exp
import kotlin.math.max

/**
 * ONNX Runtime 으로 점수 매기기. 입력 input_ids·attention_mask·token_type_ids, 출력 logits [1,2].
 * 점수 = softmax(logits)[1], score.py 와 같게 float32 로 계산.
 * 안드로이드: OnnxBackend(assets 에서 읽은 ByteArray), JVM: OnnxBackend(파일 경로).
 */
class OnnxBackend private constructor(private val session: OrtSession, private val env: OrtEnvironment) :
    (IntArray) -> Double, AutoCloseable {

    constructor(modelPath: String, threads: Int = 1) : this(OrtEnvironment.getEnvironment(), threads, modelPath, null)
    constructor(modelBytes: ByteArray, threads: Int = 1) : this(OrtEnvironment.getEnvironment(), threads, null, modelBytes)

    private constructor(env: OrtEnvironment, threads: Int, path: String?, bytes: ByteArray?) : this(
        OrtSession.SessionOptions().use { opt ->
            opt.setIntraOpNumThreads(threads)
            if (path != null) env.createSession(path, opt) else env.createSession(bytes!!, opt)
        },
        env,
    )

    val inputNames: Set<String> get() = session.inputNames

    override fun invoke(ids: IntArray): Double {
        val shape = longArrayOf(1, ids.size.toLong())
        val tensors = LinkedHashMap<String, OnnxTensor>()
        try {
            for (name in session.inputNames) {
                val arr = when (name) {
                    "input_ids" -> LongArray(ids.size) { ids[it].toLong() }
                    "attention_mask" -> LongArray(ids.size) { 1L }
                    "token_type_ids" -> LongArray(ids.size)
                    else -> error("모르는 입력 이름: $name")
                }
                tensors[name] = OnnxTensor.createTensor(env, LongBuffer.wrap(arr), shape)
            }
            session.run(tensors).use { r ->
                @Suppress("UNCHECKED_CAST")
                val lg = (r.get(0).value as Array<FloatArray>)[0]
                val m = max(lg[0], lg[1])
                val e0 = exp(lg[0] - m)
                val e1 = exp(lg[1] - m)
                return (e1 / (e0 + e1)).toDouble()
            }
        } finally {
            tensors.values.forEach { it.close() }
        }
    }

    override fun close() = session.close()
}
