// @alku asetukset
pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}
dependencyResolutionManagement {
    repositoriesMode = RepositoriesMode.FAIL_ON_PROJECT_REPOS
    repositories {
        google()
        // Googlen peili Maven Centralista: CI:n ajokoneilta Maven
        // Central rajoittaa latauksia (HTTP 429).
        maven("https://maven-central.storage-download.googleapis.com/maven2/")
        mavenCentral()
    }
}

rootProject.name = "ostokset"
include(":app")
// @loppu asetukset
