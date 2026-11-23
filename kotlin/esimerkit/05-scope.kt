// Scope-funktiot: let, apply, also, run ja takeIf käytössä.

class Yhteys {
    var osoite = ""
    var aikakatkaisuMs = 1000
    var uudelleenyrityksia = 0
    override fun toString() =
        "Yhteys($osoite, ${aikakatkaisuMs}ms, $uudelleenyrityksia)"
}

fun main() {
    System.setOut(java.io.PrintStream(System.out, true, Charsets.UTF_8))
    // apply: alustaa olion ja palauttaa sen (vastaanottaja this).
    val yhteys = Yhteys().apply {
        osoite = "db.example.org:5432"
        aikakatkaisuMs = 3000
        uudelleenyrityksia = 2
    }

    // also: sivuvaikutus (loki) ketjun keskellä, palauttaa olion.
    val lista = mutableListOf("b", "a")
        .also { println("ennen järjestystä: $it") }
        .apply { sort() }
    println("jälkeen: $lista")

    // let: muunnos nullable-arvolle; tulos on lohkon arvo.
    val portti = yhteys.osoite.substringAfter(':', "")
        .toIntOrNull()
        ?.let { if (it in 1..65535) it else null }
    println("portti $portti")

    // run: laske arvo olion kentistä (vastaanottaja this).
    val kuvaus = yhteys.run {
        val pisin = aikakatkaisuMs * (uudelleenyrityksia + 1)
        "$osoite, pahimmillaan $pisin ms"
    }
    println(kuvaus)

    // takeIf: arvo tai null ehdon mukaan.
    val nimi = "  ".takeIf { it.isNotBlank() } ?: "nimetön"
    println(nimi)
    println(yhteys)
}
