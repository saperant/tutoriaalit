package fi.esimerkki.ostokset.lista

import app.cash.turbine.ReceiveTurbine
import app.cash.turbine.test
import fi.esimerkki.ostokset.malli.Tuote
import fi.esimerkki.ostokset.testi.MainDispatcherRule
import fi.esimerkki.ostokset.testi.VaarennosRepository
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test

// @alku testi
class ListaViewModelTest {
    @get:Rule val main = MainDispatcherRule()

    private val maito = Tuote(1, "maito")
    private val repo = VaarennosRepository(listOf(maito))
    private val vm = ListaViewModel(repo)

    @Test fun lisaysTyhjentaaKentanJaLisaaTuotteen() = runTest {
        vm.tila.test {
            assertTrue(awaitItem().ladataan)        // alkuarvo
            assertEquals(listOf(maito), awaitItem().tuotteet)

            vm.nimiMuuttui("leipä")
            assertTrue(awaitItem().voiLisata)
            vm.lisaa()
            assertEquals("", awaitItem().uusiNimi)
            assertEquals(listOf("maito", "leipä"),
                         awaitItem().tuotteet.map { it.nimi })
        }
    }

    @Test fun epaonnistunutSynkronointiNayttaaViestin() = runTest {
        repo.verkkoToimii = false
        vm.tila.test {
            // Välitiloja voi tulla enemmän tai vähemmän (StateFlow yhdistää
            // peräkkäiset arvot), joten odotetaan ehtoja eikä laskettuja
            // tiloja.
            odota { !it.ladataan }
            vm.synkronoi()
            odota { it.synkronoidaan }
            val valmis = odota { !it.synkronoidaan }
            assertEquals(Viesti.EiYhteytta, valmis.viesti)
            vm.viestiNaytetty()
            assertEquals(null, odota { it.viesti == null }.viesti)
        }
    }

    /** Ottaa tiloja vastaan, kunnes ehto täyttyy, ja palauttaa sen tilan. */
    private suspend fun ReceiveTurbine<ListaUiState>.odota(
        ehto: (ListaUiState) -> Boolean,
    ): ListaUiState {
        while (true) {
            val tila = awaitItem()
            if (ehto(tila)) return tila
        }
    }
}
// @loppu testi
