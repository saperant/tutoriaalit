package fi.esimerkki.ostokset.data

import androidx.datastore.preferences.core.PreferenceDataStoreFactory
import fi.esimerkki.ostokset.malli.Lajittelu
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Rule
import org.junit.Test
import org.junit.rules.TemporaryFolder

// @alku testi
/** DataStore on puhdasta Kotlinia: testi ajetaan suoraan JVM:llä
 *  ilman Robolectricia. */
class AsetuksetTest {
    @get:Rule val kansio = TemporaryFolder()

    @Test fun lajitteluTallentuuJaOletusOnLisays() = runTest {
        val varasto = PreferenceDataStoreFactory.create(
            scope = backgroundScope,
            produceFile = { kansio.newFile("asetukset.preferences_pb") },
        )
        val asetukset = Asetukset(varasto)
        assertEquals(Lajittelu.LISAYS, asetukset.lajittelu.first())
        asetukset.asetaLajittelu(Lajittelu.NIMI)
        assertEquals(Lajittelu.NIMI, asetukset.lajittelu.first())
    }
}
// @loppu testi
