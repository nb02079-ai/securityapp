// 판정 엔진: 외부 라이브러리 없는 순수 Kotlin (작업 5단계 안드로이드 앱에 그대로 들어감)
plugins {
    kotlin("jvm")
}

kotlin {
    jvmToolchain(21)
}

dependencies {
    testImplementation(kotlin("test"))
    testRuntimeOnly("org.junit.platform:junit-platform-launcher")
}

tasks.test {
    useJUnitPlatform()
}
