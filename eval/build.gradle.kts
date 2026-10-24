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
