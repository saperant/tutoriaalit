package fi.esimerkki.ostokset.ui

import androidx.compose.ui.semantics.SemanticsProperties
import androidx.compose.ui.test.SemanticsMatcher
import androidx.compose.ui.test.assert
import androidx.compose.ui.test.assertIsEnabled
import androidx.compose.ui.test.assertIsNotEnabled
import androidx.compose.ui.test.junit4.StateRestorationTester
import androidx.compose.ui.test.junit4.v2.createComposeRule
import androidx.compose.ui.test.onNodeWithContentDescription
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.performClick
import androidx.test.ext.junit.runners.AndroidJUnit4
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

// @alku testi
@RunWith(AndroidJUnit4::class)
class MaaraValitsinTest {
    @get:Rule val compose = createComposeRule()

    private fun tila(arvo: String) = SemanticsMatcher.expectValue(
        SemanticsProperties.StateDescription, arvo)

    @Test fun rajatEstavatPainikkeet() {
        compose.setContent { MaaraValitsinTilalla(alku = 1) }
        compose.onNodeWithContentDescription("Vähennä").assertIsNotEnabled()
        compose.onNodeWithContentDescription("Lisää")
            .assertIsEnabled()
            .performClick()
        compose.onNodeWithText("2").assertExists()
        compose.onNodeWithContentDescription("Vähennä").assertIsEnabled()
    }

    @Test fun ruudunlukijaKuuleeMaaran() {
        compose.setContent { MaaraValitsin(maara = 3, onMuutos = {}) }
        // Yhdistetty solmu: rivi luetaan yhtenä kokonaisuutena.
        compose.onNode(tila("3 kpl")).assertExists()
    }

    @Test fun tilaSailyyUudelleenluonnissa() {
        val palautus = StateRestorationTester(compose)
        palautus.setContent { MaaraValitsinTilalla(alku = 5) }
        compose.onNodeWithContentDescription("Lisää").performClick()
        palautus.emulateSavedInstanceStateRestore()
        compose.onNode(tila("6 kpl")).assert(tila("6 kpl"))
    }
}
// @loppu testi
