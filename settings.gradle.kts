rootProject.name = "securityapp"

dependencyResolutionManagement {
    repositories {
        mavenCentral()
    }
}

include("engine", "scorer", "eval")
