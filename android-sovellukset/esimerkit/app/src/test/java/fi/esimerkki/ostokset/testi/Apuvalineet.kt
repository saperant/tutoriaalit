package fi.esimerkki.ostokset.testi

import fi.esimerkki.ostokset.data.OstosRepository
import fi.esimerkki.ostokset.malli.Tuote
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.test.StandardTestDispatcher
import kotlinx.coroutines.test.TestDispatcher
import kotlinx.coroutines.test.resetMain
import kotlinx.coroutines.test.setMain
import org.junit.rules.TestWatcher
import org.junit.runner.Description
import java.io.IOException

// @alku saannot
/** Korvaa Dispatchers.Mainin testin ajaksi, jotta viewModelScope toimii
 *  JVM:llä ja ajastusta voi ohjata. */
@OptIn(ExperimentalCoroutinesApi::class)
class MainDispatcherRule(
    val dispatcher: TestDispatcher = StandardTestDispatcher(),
) : TestWatcher() {
    override fun starting(description: Description) =
        Dispatchers.setMain(dispatcher)
    override fun finished(description: Description) =
        Dispatchers.resetMain()
}
// @loppu saannot

// @alku vaarennos
/** Väärennös (fake): toimiva, yksinkertainen toteutus muistissa.
 *  Testi tarkistaa lopputilan, ei kutsujen järjestystä. */
class VaarennosRepository(
    alku: List<Tuote> = emptyList(),
    var verkkoToimii: Boolean = true,
) : OstosRepository {
    private val tila = MutableStateFlow(alku)
    override val tuotteet: StateFlow<List<Tuote>> = tila

    override suspend fun lisaa(nimi: String, maara: Int) {
        tila.update { it + Tuote((it.maxOfOrNull { t -> t.id } ?: 0) + 1,
                                 nimi, maara) }
    }

    override suspend fun merkitse(id: Long, ostettu: Boolean) {
        tila.update { lista ->
            lista.map { if (it.id == id) it.copy(ostettu = ostettu) else it }
        }
    }

    override suspend fun poistaOstetut() {
        tila.update { lista -> lista.filterNot { it.ostettu } }
    }

    override suspend fun synkronoi(): Result<Int> =
        if (verkkoToimii) Result.success(tila.value.size)
        else Result.failure(IOException("ei verkkoa"))
}
// @loppu vaarennos
