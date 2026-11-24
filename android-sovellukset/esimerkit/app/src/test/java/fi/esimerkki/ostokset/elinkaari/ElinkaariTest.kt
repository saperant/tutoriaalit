package fi.esimerkki.ostokset.elinkaari

import androidx.activity.ComponentActivity
import androidx.activity.compose.LocalActivityResultRegistryOwner
import androidx.activity.result.ActivityResultRegistry
import androidx.activity.result.ActivityResultRegistryOwner
import androidx.activity.result.contract.ActivityResultContract
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.ui.test.junit4.StateRestorationTester
import androidx.compose.ui.test.junit4.v2.createComposeRule
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.performClick
import androidx.core.app.ActivityOptionsCompat
import androidx.test.core.app.ActivityScenario
import androidx.test.ext.junit.runners.AndroidJUnit4
import org.junit.Assert.assertEquals
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class ElinkaariTest {
    @get:Rule val compose = createComposeRule()

    // @alku elinkaari
    @Test fun konfiguraatiomuutosTuhoaaActivityn() {
        val loki = mutableListOf<String>()
        ActivityScenario.launch(ComponentActivity::class.java).use { s ->
            s.onActivity { it.lifecycle.addObserver(ElinkaariLoki(loki)) }
            s.recreate()   // konfiguraatiomuutos, esim. näytön kierto
        }
        assertEquals(
            listOf("onCreate", "onStart", "onResume", "onPause",
                   "onStop", "onDestroy"),
            loki,
        )
    }
    // @loppu elinkaari

    // @alku tallennus
    @Test fun vainSaveableSailyy() {
        val palautus = StateRestorationTester(compose)
        palautus.setContent { KaksiLaskuria() }
        compose.onNodeWithText("Lisää").performClick()
        palautus.emulateSavedInstanceStateRestore()
        compose.onNodeWithText("remember: 0").assertExists()
        compose.onNodeWithText("rememberSaveable: 1").assertExists()
    }
    // @loppu tallennus

    // @alku lupa
    @Test fun lupapyynnonTulosValitetaan() {
        val tulokset = mutableListOf<Boolean>()
        // Rekisteri vastaa heti "sallittu" järjestelmädialogin sijaan.
        val rekisteri = object : ActivityResultRegistry() {
            override fun <I, O> onLaunch(
                requestCode: Int,
                contract: ActivityResultContract<I, O>,
                input: I,
                options: ActivityOptionsCompat?,
            ) {
                dispatchResult(requestCode, true)
            }
        }
        val omistaja = object : ActivityResultRegistryOwner {
            override val activityResultRegistry = rekisteri
        }
        compose.setContent {
            CompositionLocalProvider(
                LocalActivityResultRegistryOwner provides omistaja,
            ) { IlmoitusLupaPainike { tulokset += it } }
        }
        compose.onNodeWithText("Salli muistutukset").performClick()
        assertEquals(listOf(true), tulokset)
    }
    // @loppu lupa
}
