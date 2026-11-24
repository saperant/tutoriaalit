package fi.esimerkki.ostokset.data

import fi.esimerkki.ostokset.malli.Tuote
import fi.esimerkki.ostokset.verkko.OstosApi
import fi.esimerkki.ostokset.verkko.TuoteDto
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import java.io.IOException

// @alku rajapinta
/** Sovelluksen ainoa tie ostoslistan tietoon. ViewModel ei tiedä,
 *  tuleeko tieto tietokannasta vai verkosta. */
interface OstosRepository {
    val tuotteet: Flow<List<Tuote>>
    suspend fun lisaa(nimi: String, maara: Int)
    suspend fun merkitse(id: Long, ostettu: Boolean)
    suspend fun poistaOstetut()
    suspend fun synkronoi(): Result<Int>
}
// @loppu rajapinta

// @alku toteutus
/** Offline first: tietokanta on ainoa totuuden lähde. Käyttöliittymä
 *  lukee aina tietokantaa, ja verkko vain päivittää sitä. */
class OfflineOstosRepository(
    private val dao: TuoteDao,
    private val api: OstosApi,
) : OstosRepository {
    override val tuotteet: Flow<List<Tuote>> =
        dao.kaikki().map { rivit -> rivit.map { it.malliksi() } }

    override suspend fun lisaa(nimi: String, maara: Int) {
        Tuote(0, nimi.trim(), maara)  // tarkistaa säännöt
        dao.tallenna(TuoteRivi(nimi = nimi.trim(), maara = maara,
                               ostettu = false))
    }

    override suspend fun merkitse(id: Long, ostettu: Boolean) {
        val rivi = dao.hae(id) ?: return
        dao.tallenna(rivi.copy(ostettu = ostettu, synkronoimatta = true))
    }

    override suspend fun poistaOstetut() {
        dao.poistaOstetut()
    }

    /** Lähettää paikalliset muutokset ja hakee palvelimen tilan.
     *  Virhe ei kaada sovellusta: tieto on jo tietokannassa. */
    override suspend fun synkronoi(): Result<Int> = try {
        val muuttuneet = dao.synkronoimattomat()
        if (muuttuneet.isNotEmpty()) {
            api.lahetaMuutokset(muuttuneet.map { it.dto() })
            dao.merkitseSynkronoiduksi(muuttuneet.map { it.id })
        }
        api.haeKaikki().forEach { dao.tallenna(it.rivi()) }
        Result.success(muuttuneet.size)
    } catch (e: IOException) {
        // Verkko- ja palvelinvirheet ovat odotettuja; peruutus
        // (CancellationException) ei ole IOException, joten se etenee.
        Result.failure(e)
    }
}

private fun TuoteRivi.dto() = TuoteDto(id, nimi, maara, ostettu)
private fun TuoteDto.rivi() =
    TuoteRivi(id, nimi, maara, ostettu, synkronoimatta = false)
// @loppu toteutus
