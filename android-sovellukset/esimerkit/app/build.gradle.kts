import org.gradle.api.tasks.testing.logging.TestExceptionFormat

// @alku liitannaiset
plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.compose)
    alias(libs.plugins.kotlin.serialization)
    alias(libs.plugins.ksp)
}
// @loppu liitannaiset

// @alku android
android {
    namespace = "fi.esimerkki.ostokset"
    compileSdk {
        version = release(37) { minorApiLevel = 2 }
    }

    defaultConfig {
        applicationId = "fi.esimerkki.ostokset"
        minSdk = 26
        targetSdk = 37
        versionCode = 1
        versionName = "1.0"
        // Laitteella ajettavat testit (src/androidTest).
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }

    buildFeatures {
        compose = true
    }

    // @alku lint
    lint {
        warningsAsErrors = true
        // Ajan myötä vanhenevat tarkistukset pois, jotta sama koodi
        // läpäisee tarkistuksen myös vuoden päästä. Päivitykset
        // seurataan erikseen (esim. Renovate tai Dependabot).
        disable += setOf(
            "GradleDependency", "NewerVersionAvailable",
            "AndroidGradlePluginVersion", "OldTargetApi",
        )
    }
    // @loppu lint

    testOptions {
        // Robolectric tarvitsee resurssit ja manifestin JVM-testeissä.
        unitTests.isIncludeAndroidResources = true
        // CI:n lokiin kaatuneen testin nimi ja virhe kokonaisuudessaan.
        unitTests.all {
            // Roborazzi tallentaa kuvakaappaukset (luku 10).
            it.systemProperty("roborazzi.test.record", "true")
            it.testLogging {
                events("failed")
                exceptionFormat = TestExceptionFormat.FULL
            }
        }
    }
}
// @loppu android

// @alku kotlin
kotlin {
    jvmToolchain(21)
    compilerOptions {
        allWarningsAsErrors = true
    }
}
// @loppu kotlin

// @alku riippuvuudet
dependencies {
    implementation(libs.androidx.core)
    implementation(libs.androidx.activity.compose)
    implementation(platform(libs.compose.bom))
    implementation(libs.compose.ui)
    implementation(libs.compose.material3)
    implementation(libs.compose.ui.tooling.preview)
    debugImplementation(libs.compose.ui.tooling)
    implementation(libs.lifecycle.viewmodel.compose)
    implementation(libs.lifecycle.runtime.compose)
    implementation(libs.navigation.compose)
    implementation(libs.room.runtime)
    implementation(libs.room.ktx)
    ksp(libs.room.compiler)
    implementation(libs.datastore.preferences)
    implementation(libs.work.runtime)
    implementation(libs.coroutines.android)
    implementation(libs.serialization.json)
    implementation(libs.ktor.client.core)
    implementation(libs.ktor.client.okhttp)
    implementation(libs.ktor.client.content.negotiation)
    implementation(libs.ktor.serialization.json)

    testImplementation(libs.junit)
    testImplementation(libs.robolectric)
    testImplementation(libs.androidx.test.core)
    testImplementation(libs.androidx.test.junit)
    testImplementation(libs.coroutines.test)
    testImplementation(libs.turbine)
    testImplementation(libs.ktor.client.mock)
    testImplementation(libs.work.testing)
    testImplementation(libs.navigation.testing)
    testImplementation(platform(libs.compose.bom))
    testImplementation(libs.compose.ui.test.junit4)
    debugImplementation(libs.compose.ui.test.manifest)
    testImplementation(libs.roborazzi)
    testImplementation(libs.roborazzi.compose)

    androidTestImplementation(libs.androidx.test.runner)
    androidTestImplementation(libs.androidx.test.junit)
    androidTestImplementation(platform(libs.compose.bom))
    androidTestImplementation(libs.compose.ui.test.junit4)
}
// @loppu riippuvuudet
