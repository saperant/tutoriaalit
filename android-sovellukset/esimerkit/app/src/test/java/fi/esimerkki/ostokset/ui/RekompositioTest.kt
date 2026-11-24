package fi.esimerkki.ostokset.ui

import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.compose.ui.test.junit4.v2.createComposeRule
import androidx.test.ext.junit.runners.AndroidJUnit4
import fi.esimerkki.ostokset.malli.Tuote
import org.junit.Assert.assertEquals
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import java.util.concurrent.atomic.AtomicInteger

// @alku testi
/** Muutetaan vain otsikkoa kolmesti ja lasketaan, montako kertaa
 *  Yhteenveto koostetaan. */
@RunWith(AndroidJUnit4::class)
class RekompositioTest {
    @get:Rule val compose = createComposeRule()
    private val tuotteet = listOf(Tuote(1, "maito"), Tuote(2, "leipä"))

    private fun koostamiset(
        nakyma: @Composable (List<Tuote>, String, () -> Unit) -> Unit,
    ): Int {
        var otsikko by mutableStateOf("Ostokset")
        val kerrat = AtomicInteger()
        // Lambda kaappaa vain vakaan viitteen (val), joten Compose
        // muistaa sen; var-muuttujan kaappaava lambda olisi joka
        // kerta uusi ja pakottaisi lapsen koostamaan uudelleen.
        compose.setContent {
            nakyma(tuotteet, otsikko) { kerrat.incrementAndGet() }
        }
        repeat(3) {
            otsikko = "Ostokset $it"
            compose.waitForIdle()
        }
        return kerrat.get()
    }

    @Test fun uusiEpavakaaOlioKoostaaJokaKerta() =
        assertEquals(4, koostamiset { t, o, k -> NakymaHuono(t, o, k) })

    @Test fun muistettuOlioOhittaaLapsen() =
        assertEquals(1, koostamiset { t, o, k -> NakymaHyva(t, o, k) })

    @Test fun yhtasuuriVakaaArvoOhittaaLapsen() =
        assertEquals(1, koostamiset { t, o, k -> NakymaVakaa(t, o, k) })
}
// @loppu testi
