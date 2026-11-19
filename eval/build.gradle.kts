// 재생 평가기: 엔진에 평가 세트를 메시지 하나씩 흘려 넣고 지표를 계산
plugins {
    kotlin("jvm")
    application
}

kotlin {
    jvmToolchain(21)
}

dependencies {
    implementation(project(":engine"))
    implementation(project(":scorer"))
    implementation("com.microsoft.onnxruntime:onnxruntime:${rootProject.extra["ortVersion"]}")
    testImplementation(kotlin("test"))
    testRuntimeOnly("org.junit.platform:junit-platform-launcher")
}

application {
    mainClass.set("securityapp.eval.MainKt")
}

// 상대 경로(--input data/dev/synthetic 등)를 저장소 최상위 기준으로, 콘솔 한글은 UTF-8로 (Windows는 chcp 65001)
tasks.named<JavaExec>("run") {
    workingDir = rootProject.projectDir
    jvmArgs("-Dfile.encoding=UTF-8", "-Dstdout.encoding=UTF-8", "-Dstderr.encoding=UTF-8")
}

tasks.test {
    useJUnitPlatform()
}

// 파이썬·Kotlin 판정기 일치 확인 (Parity.kt, 5단계-2)
tasks.register<JavaExec>("parity") {
    group = "verification"
    description = "make_parity_vectors.py 결과와 Kotlin 판정기 비교"
    classpath = sourceSets["main"].runtimeClasspath
    mainClass.set("securityapp.eval.ParityKt")
    workingDir = rootProject.projectDir
    jvmArgs("-Dfile.encoding=UTF-8", "-Dstdout.encoding=UTF-8", "-Dstderr.encoding=UTF-8")
}
