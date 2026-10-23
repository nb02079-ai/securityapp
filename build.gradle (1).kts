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

tasks.test {
    useJUnitPlatform()
}
