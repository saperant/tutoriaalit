package fi.esimerkki.ostokset.data

import androidx.room.Dao
import androidx.room.Database
import androidx.room.Entity
import androidx.room.PrimaryKey
import androidx.room.Query
import androidx.room.RoomDatabase
import androidx.room.Upsert
import fi.esimerkki.ostokset.malli.Tuote
import kotlinx.coroutines.flow.Flow

// @alku entiteetti
/** Taulun rivi. Erillinen tietokantatyyppi pitää skeeman ja
 *  sovelluksen mallin toisistaan riippumattomina. */
@Entity(tableName = "tuote")
data class TuoteRivi(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val nimi: String,
    val maara: Int,
    val ostettu: Boolean,
    /** Muutettu paikallisesti, ei vielä lähetetty palvelimelle. */
    val synkronoimatta: Boolean = true,
)

fun TuoteRivi.malliksi() = Tuote(id, nimi, maara, ostettu)
// @loppu entiteetti

// @alku dao
@Dao
interface TuoteDao {
    /** Flow lähettää uuden listan aina, kun taulu muuttuu. */
    @Query("SELECT * FROM tuote ORDER BY ostettu, id")
    fun kaikki(): Flow<List<TuoteRivi>>

    @Query("SELECT * FROM tuote WHERE id = :id")
    suspend fun hae(id: Long): TuoteRivi?

    @Query("SELECT * FROM tuote WHERE synkronoimatta")
    suspend fun synkronoimattomat(): List<TuoteRivi>

    @Upsert
    suspend fun tallenna(rivi: TuoteRivi): Long

    @Query("UPDATE tuote SET synkronoimatta = 0 WHERE id IN (:idt)")
    suspend fun merkitseSynkronoiduksi(idt: List<Long>)

    @Query("DELETE FROM tuote WHERE ostettu")
    suspend fun poistaOstetut(): Int
}
// @loppu dao

// @alku tietokanta
@Database(entities = [TuoteRivi::class], version = 1, exportSchema = false)
abstract class OstosTietokanta : RoomDatabase() {
    abstract fun tuotteet(): TuoteDao
}
// @loppu tietokanta
