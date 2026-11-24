package fi.esimerkki.ostokset.ui

import androidx.compose.ui.test.assertIsOff
import androidx.compose.ui.test.assertIsOn
import androidx.compose.ui.test.hasStateDescription
import androidx.compose.ui.test.junit4.v2.createComposeRule
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.performClick
import androidx.test.ext.junit.runners.AndroidJUnit4
import fi.esimerkki.ostokset.malli.Tuote
import org.junit.Assert.assertEquals
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class TuoteListaTest {
    @get:Rule val compose = createComposeRule()

    // @alku testi
    @Test fun valintaruutuJaRiviKutsuvatEriTapahtumia() {
        val tuotteet = listOf(Tuote(1, "maito", 2), Tuote(2, "leipä"))
        val ostetut = mutableListOf<Pair<Long, Boolean>>()
        val avatut = mutableListOf<Long>()
        compose.setContent {
            TuoteLista(
                tuotteet,
                onOstettu = { t, o -> ostetut += t.id to o },
                onAvaa = { avatut += it.id },
            )
        }
        compose.onNodeWithText("maito × 2").performClick()
        compose.onAllNodes(hasStateDescription("ostamatta"))[1]
            .assertIsOff()
            .performClick()
        assertEquals(listOf(1L), avatut)
        assertEquals(listOf(2L to true), ostetut)
    }
    // @loppu testi

    @Test fun ostettuNakyyValittuna() {
        compose.setContent {
            TuoteLista(listOf(Tuote(1, "maito", ostettu = true)), { _, _ -> },
                       {})
        }
        compose.onNode(hasStateDescription("ostettu")).assertIsOn()
    }
}
