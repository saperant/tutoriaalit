package fi.esimerkki.ostokset.data

import android.content.Context
import androidx.room.Room
import androidx.test.core.app.ApplicationProvider
import androidx.test.ext.junit.runners.AndroidJUnit4
import fi.esimerkki.ostokset.verkko.OstosApi
import fi.esimerkki.ostokset.verkko.luoHttpAsiakas
import io.ktor.client.engine.mock.MockEngine
import io.ktor.client.engine.mock.respond
import io.ktor.http.HttpHeaders
import io.ktor.http.HttpMethod
import io.ktor.http.HttpStatusCode
import io.ktor.http.headersOf
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.test.runTest
import org.junit.After
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import org.junit.runner.RunWith
import java.io.IOException

// @alku testi
@RunWith(AndroidJUnit4::class)
class OstosRepositoryTest {
    private val kanta = Room.inMemoryDatabaseBuilder(
        ApplicationProvider.getApplicationContext<Context>(),
        OstosTietokanta::class.java,
    ).build()

    @After fun sulje() = kanta.close()

    private var verkossa = false
    private val lahetetyt = mutableListOf<String>()
    private val palvelin = MockEngine { pyynto ->
        if (!verkossa) throw IOException("ei yhteyttä")
        if (pyynto.method == HttpMethod.Put) {
            lahetetyt += pyynto.url.encodedPath
            respond("", HttpStatusCode.NoContent)
        } else {
            respond("""[{"id":99,"nimi":"kahvi","maara":1,
                         "ostettu":false}]""",
                    HttpStatusCode.OK,
                    headersOf(HttpHeaders.ContentType, "application/json"))
        }
    }
    private val repo = OfflineOstosRepository(
        kanta.tuotteet(),
        OstosApi(luoHttpAsiakas(palvelin, "https://testi/api/")),
    )

    @Test fun toimiiIlmanVerkkoaJaSynkronoiMyohemmin() = runTest {
        repo.lisaa("  maito ", 2)
        assertTrue(repo.synkronoi().isFailure)
        // Tieto on silti tallessa ja näkyvissä.
        assertEquals(listOf("maito"), repo.tuotteet.first().map { it.nimi })

        verkossa = true
        assertEquals(1, repo.synkronoi().getOrThrow())
        assertEquals(listOf("/api/tuotteet"), lahetetyt)
        assertEquals(listOf("maito", "kahvi"),
                     repo.tuotteet.first().map { it.nimi })
        assertEquals(0, repo.synkronoi().getOrThrow())
    }
}
// @loppu testi
