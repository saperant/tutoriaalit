package fi.esimerkki.ostokset.data

import android.content.Context
import androidx.room.Room
import androidx.test.core.app.ApplicationProvider
import androidx.test.ext.junit.runners.AndroidJUnit4
import app.cash.turbine.test
import kotlinx.coroutines.test.runTest
import kotlin.time.Duration.Companion.seconds
import org.junit.After
import org.junit.Assert.assertEquals
import org.junit.Test
import org.junit.runner.RunWith

// @alku testi
/** Robolectric antaa Androidin SQLiten JVM:llä, joten oikeat SQL-kyselyt
 *  testataan ilman laitetta. */
@RunWith(AndroidJUnit4::class)
class TuoteDaoTest {
    private val kanta = Room.inMemoryDatabaseBuilder(
        ApplicationProvider.getApplicationContext<Context>(),
        OstosTietokanta::class.java,
    ).build()
    private val dao = kanta.tuotteet()

    @After fun sulje() = kanta.close()

    @Test fun ostetutListanLoppuunJaPoistoTyhjentaa() = runTest {
        // Room ilmoittaa muutoksista taustasäikeessä oikeassa ajassa, joten
        // hitaalla CI-koneella Turbinen oletusaikaraja (3 s) ei riitä.
        dao.kaikki().test(timeout = 30.seconds) {
            assertEquals(emptyList<TuoteRivi>(), awaitItem())
            val maito = dao.tallenna(TuoteRivi(nimi = "maito", maara = 1,
                                                ostettu = false))
            awaitItem()
            dao.tallenna(TuoteRivi(nimi = "leipä", maara = 1,
                                   ostettu = false))
            awaitItem()
            dao.tallenna(dao.hae(maito)!!.copy(ostettu = true))
            assertEquals(listOf("leipä", "maito"),
                         awaitItem().map { it.nimi })
            assertEquals(1, dao.poistaOstetut())
            assertEquals(listOf("leipä"), awaitItem().map { it.nimi })
        }
    }
}
// @loppu testi
