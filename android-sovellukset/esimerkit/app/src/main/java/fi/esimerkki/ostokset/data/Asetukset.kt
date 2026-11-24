package fi.esimerkki.ostokset.data

import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import fi.esimerkki.ostokset.malli.Lajittelu
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map

// @alku asetukset
/** Käyttäjän asetukset DataStoressa: asynkroninen, transaktionaalinen
 *  ja Flow-pohjainen korvaaja SharedPreferencesille. */
class Asetukset(private val varasto: DataStore<Preferences>) {
    private val avain = stringPreferencesKey("lajittelu")

    val lajittelu: Flow<Lajittelu> = varasto.data.map { arvot ->
        arvot[avain]
            ?.let { nimi -> Lajittelu.entries.find { it.name == nimi } }
            ?: Lajittelu.LISAYS
    }

    suspend fun asetaLajittelu(lajittelu: Lajittelu) {
        varasto.edit { it[avain] = lajittelu.name }
    }
}
// @loppu asetukset
