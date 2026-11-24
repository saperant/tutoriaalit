package fi.esimerkki.ostokset

import android.content.Context
import androidx.datastore.preferences.preferencesDataStore
import androidx.room.Room
import fi.esimerkki.ostokset.data.Asetukset
import fi.esimerkki.ostokset.data.OfflineOstosRepository
import fi.esimerkki.ostokset.data.OstosRepository
import fi.esimerkki.ostokset.data.OstosTietokanta
import fi.esimerkki.ostokset.lista.ListaViewModel
import fi.esimerkki.ostokset.verkko.OstosApi
import fi.esimerkki.ostokset.verkko.luoHttpAsiakas
import io.ktor.client.engine.okhttp.OkHttp

// @alku datastore
// Yksi DataStore-olio tiedostoa kohden koko prosessissa.
private val Context.asetusVarasto by preferencesDataStore("asetukset")
// @loppu datastore

// @alku sailio
/** Riippuvuuksien kokoaminen käsin: sovelluksen oliot luodaan yhdessä
 *  paikassa, ja muut saavat ne muodostimen parametreina. */
class Sailio(konteksti: Context) {
    private val tietokanta = Room.databaseBuilder(
        konteksti, OstosTietokanta::class.java, "ostokset.db",
    ).build()

    private val api = OstosApi(
        luoHttpAsiakas(OkHttp.create(), "https://ostokset.example/api/"),
    )

    val repository: OstosRepository by lazy {
        OfflineOstosRepository(tietokanta.tuotteet(), api)
    }

    val asetukset = Asetukset(konteksti.asetusVarasto)

    fun listaViewModel() = ListaViewModel(repository)
}
// @loppu sailio
