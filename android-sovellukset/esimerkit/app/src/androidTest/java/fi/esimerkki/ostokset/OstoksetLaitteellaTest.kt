package fi.esimerkki.ostokset

import androidx.compose.ui.test.junit4.v2.createAndroidComposeRule
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.performClick
import androidx.compose.ui.test.performTextInput
import androidx.test.ext.junit.runners.AndroidJUnit4
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

// @alku testi
/** Päästä päähän: oikea sovellus, oikea tietokanta ja oikea laite tai
 *  emulaattori. Käännetään aina, ajetaan komennolla
 *  ./gradlew connectedDebugAndroidTest. */
@RunWith(AndroidJUnit4::class)
class OstoksetLaitteellaTest {
    @get:Rule val compose = createAndroidComposeRule<MainActivity>()

    @Test fun lisattyTuoteNakyyListassa() {
        compose.onNodeWithText("Uusi tuote").performTextInput("kahvi")
        compose.onNodeWithText("Lisää").performClick()
        compose.onNodeWithText("kahvi × 1").assertExists()
    }
}
// @loppu testi
