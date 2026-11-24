package fi.esimerkki.ostokset.verkko

import io.ktor.client.engine.mock.MockEngine
import io.ktor.client.engine.mock.respond
import io.ktor.client.engine.mock.toByteArray
import io.ktor.http.HttpHeaders
import io.ktor.http.HttpMethod
import io.ktor.http.HttpStatusCode
import io.ktor.http.headersOf
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

// @alku testi
class OstosApiTest {
    private val json = headersOf(HttpHeaders.ContentType, "application/json")

    private fun api(moottori: MockEngine) =
        OstosApi(luoHttpAsiakas(moottori, "https://testi/api/"))

    @Test fun haeKaikkiJasentaaVastauksen() = runTest {
        val moottori = MockEngine { pyynto ->
            assertEquals("https://testi/api/tuotteet",
                         pyynto.url.toString())
            respond("""[{"id":7,"nimi":"kahvi","maara":2,"ostettu":false,
                        "uusiKentta":1}]""", HttpStatusCode.OK, json)
        }
        assertEquals(listOf(TuoteDto(7, "kahvi", 2, false)),
                     api(moottori).haeKaikki())
    }

    @Test fun muutoksetLahetetaanJsonina() = runTest {
        var runko = ""
        val moottori = MockEngine { pyynto ->
            assertEquals(HttpMethod.Put, pyynto.method)
            runko = pyynto.body.toByteArray().decodeToString()
            respond("", HttpStatusCode.NoContent)
        }
        api(moottori).lahetaMuutokset(listOf(TuoteDto(1, "maito", 1, true)))
        assertEquals("""[{"id":1,"nimi":"maito","maara":1,"ostettu":true}]""",
                     runko)
    }

    @Test fun palvelinvirheOnVerkkoVirhe() = runTest {
        val moottori = MockEngine {
            respond("", HttpStatusCode.ServiceUnavailable)
        }
        val virhe = runCatching { api(moottori).haeKaikki() }
            .exceptionOrNull()
        assertTrue(virhe is VerkkoVirhe)
        assertEquals("Palvelin vastasi 503", virhe?.message)
    }
}
// @loppu testi
