package fi.esimerkki.ostokset.malli

// @alku tuote
/** Ostoslistan rivi. Muuttumaton: muutos tuottaa uuden olion. */
data class Tuote(
    val id: Long,
    val nimi: String,
    val maara: Int = 1,
    val ostettu: Boolean = false,
) {
    init {
        require(nimi.isNotBlank()) { "nimi puuttuu" }
        require(maara in 1..99) { "määrä 1–99" }
    }
}
// @loppu tuote

/** Lajittelujärjestys, joka tallennetaan käyttäjän asetuksiin. */
enum class Lajittelu { LISAYS, NIMI }
