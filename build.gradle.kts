plugins {
    kotlin("jvm") version "2.2.0" apply false
}

// 모듈별 설정은 engine/, scorer/, eval/ 의 build.gradle.kts에 있다.
// ONNX Runtime 판(Java). 파이썬(onnxruntime 1.32.0)과 같아야 int8 점수가 같음 (docs/v3_plan.md 5단계-2 결과)
// 앱의 onnxruntime-android 도 같은 판을 씀
extra["ortVersion"] = providers.gradleProperty("ortVersion").getOrElse("1.32.0")
