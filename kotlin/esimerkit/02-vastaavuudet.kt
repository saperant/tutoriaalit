// Tilauksen käsittely: Javan kymmenet rivit kootusti Kotlinina.

// Javan record/POJO equals-, hashCode-, toString- ja copy-metodeineen.
data class Asiakas(val nimi: String, val sahkoposti: String?)

// Suljettu hierarkia: kääntäjä tietää kaikki tilat.
sealed interface Tila {
    data object Uusi : Tila
    data class Lahetetty(val seuranta: String) : Tila
    data class Peruttu(val syy: String) : Tila
}

data class Tilaus(val id: Int, val asiakas: Asiakas, val tila: Tila)

// Laajennusfunktio: uusi "metodi" ilman perimistä tai apuluokkaa.
fun Tilaus.kuvaus(): String = when (val t = tila) {
    Tila.Uusi -> "#$id odottaa käsittelyä"
    is Tila.Lahetetty -> "#$id lähetetty (${t.seuranta})"
    is Tila.Peruttu -> "#$id peruttu: ${t.syy}"
}

fun main() {
    System.setOut(java.io.PrintStream(System.out, true, Charsets.UTF_8))
    val ada = Asiakas("Ada", "ada@example.org")
    val tilaukset = listOf(
        Tilaus(1, ada, Tila.Uusi),
        Tilaus(2, Asiakas("Bo", null), Tila.Lahetetty("JJFI123")),
        Tilaus(3, ada, Tila.Peruttu("asiakkaan pyyntö")),
    )
    tilaukset.forEach { println(it.kuvaus()) }

    // Null-turvallisuus: ?. ja ?: korvaavat if (x != null) -ketjut.
    val osoite = tilaukset[1].asiakas.sahkoposti ?: "ei sähköpostia"
    println("Bo: $osoite")

    // copy luo muutetun kopion; alkuperäinen ei muutu.
    val lahetetty = tilaukset[0].copy(tila = Tila.Lahetetty("JJFI456"))
    println(lahetetty.kuvaus())
    println(tilaukset[0] == lahetetty.copy(tila = Tila.Uusi))
}
