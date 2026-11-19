// 분류 모델 판정기: 글 정리 → 토큰 나누기 → ONNX 점수 (docs/v3_plan.md 5단계-2)
// 순수 Kotlin. ONNX Runtime은 compileOnly라서 쓰는 쪽이 넣음:
//   JVM(eval의 parity): com.microsoft.onnxruntime:onnxruntime
//   안드로이드 앱:       com.microsoft.onnxruntime:onnxruntime-android (같은 ai.onnxruntime API)
plugins {
    kotlin("jvm")
}

kotlin {
    jvmToolchain(21)
}

val ortVersion: String by rootProject.extra

dependencies {
    compileOnly("com.microsoft.onnxruntime:onnxruntime:$ortVersion")
    testImplementation(kotlin("test"))
    testRuntimeOnly("org.junit.platform:junit-platform-launcher")
}

tasks.test {
    useJUnitPlatform()
}
