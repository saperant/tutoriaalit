// Virheenkäsittely: ei tarkistettuja poikkeuksia; require/check/error,
// try lausekkeena ja runCatching rajapinnan reunalla.

import java.io.File
import java.io.IOException

class AsetusVirhe(viesti: String, syy: Throwable? = null) :
    Exception(viesti, syy)

data class Asetukset(val portti: Int, val tyontekijat: Int)

fun lueAsetukset(tiedosto: File): Asetukset {
    // Kotlin ei pakota käsittelemään IOExceptionia; kääritään se
    // sovelluksen omaksi virheeksi, ja alkuperäinen jää syyksi.
    val rivit = try {
        tiedosto.readLines()
    } catch (e: IOException) {
        throw AsetusVirhe("asetuksia ei voi lukea: ${tiedosto.name}", e)
    }
    val arvot = rivit.filter { '=' in it }.associate {
        it.substringBefore('=').trim() to it.substringAfter('=').trim()
    }
    fun luku(avain: String, oletus: Int): Int {
        val teksti = arvot[avain] ?: return oletus
        return teksti.toIntOrNull()
            ?: throw AsetusVirhe("$avain: ei kokonaisluku: '$teksti'")
    }
    val asetukset = Asetukset(luku("portti", 8080), luku("tyontekijat", 4))
    // require: kutsujan virhe (IllegalArgumentException).
    require(asetukset.portti in 1..65535) { "portti: ${asetukset.portti}" }
    return asetukset
}

fun main() {
    System.setOut(java.io.PrintStream(System.out, true, Charsets.UTF_8))
    File("ok.conf").writeText("portti = 9000\n")
    File("rikki.conf").writeText("portti = yhdeksän\n")
    File("raja.conf").writeText("portti = 70000\n")
    for (nimi in listOf("ok.conf", "rikki.conf", "raja.conf", "puuttuu")) {
        // runCatching muuttaa poikkeuksen arvoksi (Result).
        val tulos = runCatching { lueAsetukset(File(nimi)) }
        val teksti = tulos.fold(
            onSuccess = { "ok $it" },
            onFailure = { "${it::class.simpleName}: ${it.message}" },
        )
        println("$nimi -> $teksti")
    }
    // check: oman tilan virhe (IllegalStateException), error: aina.
    val tila = runCatching {
        check(File("ok.conf").delete()) { "ei poistettu" }
    }
    println("poisto onnistui: ${tila.isSuccess}")
    listOf("rikki.conf", "raja.conf").forEach { File(it).delete() }
}
