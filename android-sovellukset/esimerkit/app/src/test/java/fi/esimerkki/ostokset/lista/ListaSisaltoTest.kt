package fi.esimerkki.ostokset.lista

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.compose.ui.test.assertIsEnabled
import androidx.compose.ui.test.assertIsNotEnabled
import androidx.compose.ui.test.junit4.v2.createComposeRule
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.performTextInput
import androidx.test.ext.junit.runners.AndroidJUnit4
import org.junit.Assert.assertEquals
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

// @alku testi
@RunWith(AndroidJUnit4::class)
class ListaSisaltoTest {
    @get:Rule val compose = createComposeRule()

    @Test fun lisaaOnKaytossaVastaKunNimiOnAnnettu() {
        var tila by mutableStateOf(ListaUiState(ladataan = false))
        compose.setContent {
            ListaSisalto(
                tila = tila,
                onNimi = { tila = tila.copy(uusiNimi = it) },
                onLisaa = {}, onOstettu = { _, _ -> }, onAvaa = {},
                onSynkronoi = {}, onViestiNaytetty = {},
            )
        }
        compose.onNodeWithText("Lisää").assertIsNotEnabled()
        compose.onNodeWithText("Uusi tuote").performTextInput("kahvi")
        compose.onNodeWithText("Lisää").assertIsEnabled()
    }

    @Test fun viestiNaytetaanJaKuitataan() {
        var kuitattu = 0
        compose.setContent {
            ListaSisalto(
                tila = ListaUiState(ladataan = false,
                                    viesti = Viesti.Lahetetty(2)),
                onNimi = {}, onLisaa = {}, onOstettu = { _, _ -> },
                onAvaa = {}, onSynkronoi = {},
                onViestiNaytetty = { kuitattu++ },
            )
        }
        compose.onNodeWithText("Lähetetty 2 muutosta").assertExists()
        // Snackbar sulkeutuu itsestään; testin kello kelataan eteenpäin.
        compose.mainClock.advanceTimeBy(10_000)
        compose.waitForIdle()
        assertEquals(1, kuitattu)
    }
}
// @loppu testi
