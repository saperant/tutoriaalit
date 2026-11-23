// Odotetut virheet tyyppinä: suljettu tulos kertoo kutsujalle kaikki
// vaihtoehdot, ja kääntäjä valvoo, että ne käsitellään.
// "Parse, don't validate": syöte jäsennetään kerran tyypiksi, jonka
// olemassaolo takaa kelvollisuuden.

@JvmInline
value class Sahkoposti private constructor(val arvo: String) {
    companion object {
        // Ainoa tapa luoda Sahkoposti: konstruktori on yksityinen.
        fun jasenna(teksti: String): Sahkoposti? {
            val t = teksti.trim().lowercase()
            val osat = t.split('@')
            return if (osat.size == 2 && osat.all { it.isNotEmpty() } &&
                '.' in osat[1]) Sahkoposti(t) else null
        }
    }
}

sealed interface Rekisterointi {
    data class Ok(val sahkoposti: Sahkoposti, val ika: Int) : Rekisterointi
    sealed interface Virhe : Rekisterointi {
        data class VirheellinenSahkoposti(val syote: String) : Virhe
        data class LiianNuori(val ika: Int) : Virhe
        data object PuuttuvaIka : Virhe
    }
}

fun rekisteroi(sposti: String, ika: String): Rekisterointi {
    val osoite = Sahkoposti.jasenna(sposti)
        ?: return Rekisterointi.Virhe.VirheellinenSahkoposti(sposti)
    val vuodet = ika.toIntOrNull() ?: return Rekisterointi.Virhe.PuuttuvaIka
    if (vuodet < 13) return Rekisterointi.Virhe.LiianNuori(vuodet)
    return Rekisterointi.Ok(osoite, vuodet)
}

fun viesti(tulos: Rekisterointi): String = when (tulos) {
    is Rekisterointi.Ok -> "tervetuloa, ${tulos.sahkoposti.arvo}"
    is Rekisterointi.Virhe.VirheellinenSahkoposti ->
        "tarkista osoite '${tulos.syote}'"
    is Rekisterointi.Virhe.LiianNuori -> "ikäraja 13 (annettu ${tulos.ika})"
    Rekisterointi.Virhe.PuuttuvaIka -> "anna ikä numeroina"
}

fun main() {
    System.setOut(java.io.PrintStream(System.out, true, Charsets.UTF_8))
    val syotteet = listOf(
        "Aino@Example.org" to "34",
        "aino.example.org" to "34",
        "eino@example.org" to "11",
        "iida@example.org" to "",
    )
    for ((sposti, ika) in syotteet) println(viesti(rekisteroi(sposti, ika)))
}
