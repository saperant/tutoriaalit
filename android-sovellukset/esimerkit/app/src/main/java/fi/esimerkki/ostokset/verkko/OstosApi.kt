package fi.esimerkki.ostokset.verkko

import io.ktor.client.HttpClient
import io.ktor.client.call.body
import io.ktor.client.engine.HttpClientEngine
import io.ktor.client.plugins.HttpTimeout
import io.ktor.client.plugins.contentnegotiation.ContentNegotiation
import io.ktor.client.plugins.defaultRequest
import io.ktor.client.request.get
import io.ktor.client.request.put
import io.ktor.client.request.setBody
import io.ktor.http.ContentType
import io.ktor.http.contentType
import io.ktor.http.isSuccess
import io.ktor.serialization.kotlinx.json.json
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import java.io.IOException

// @alku dto
/** Palvelimen esitys tuotteesta. Erillään sovelluksen mallista,
 *  jotta rajapinnan muutos ei leviä koko sovellukseen. */
@Serializable
data class TuoteDto(
    val id: Long,
    val nimi: String,
    val maara: Int,
    val ostettu: Boolean,
)
// @loppu dto

/** Palvelimen virhevastaus. IOException-aliluokka, joten se käsitellään
 *  samoin kuin yhteysvirhe. */
class VerkkoVirhe(viesti: String) : IOException(viesti)

// @alku asiakas
/** HTTP-asiakas. Moottori annetaan parametrina: sovelluksessa OkHttp,
 *  testeissä MockEngine. */
fun luoHttpAsiakas(moottori: HttpClientEngine, osoite: String) =
    HttpClient(moottori) {
        expectSuccess = false
        install(ContentNegotiation) {
            json(Json { ignoreUnknownKeys = true })
        }
        install(HttpTimeout) { requestTimeoutMillis = 10_000 }
        defaultRequest { url(osoite) }
    }

class OstosApi(private val http: HttpClient) {
    suspend fun haeKaikki(): List<TuoteDto> {
        val vastaus = http.get("tuotteet")
        if (!vastaus.status.isSuccess()) {
            throw VerkkoVirhe("Palvelin vastasi ${vastaus.status.value}")
        }
        return vastaus.body()
    }

    suspend fun lahetaMuutokset(tuotteet: List<TuoteDto>) {
        val vastaus = http.put("tuotteet") {
            contentType(ContentType.Application.Json)
            setBody(tuotteet)
        }
        if (!vastaus.status.isSuccess()) {
            throw VerkkoVirhe("Palvelin vastasi ${vastaus.status.value}")
        }
    }
}
// @loppu asiakas
