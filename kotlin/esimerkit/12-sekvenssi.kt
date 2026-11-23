// sequence { } on vakiokirjaston korutiini: yield keskeyttää
// rakentajan, ja suoritus jatkuu, kun kuluttaja pyytää seuraavaa.
// Esimerkki: sivutettu rajapinta näkyy kuluttajalle yhtenä virtana.

data class Sivu(val rivit: List<String>, val viimeinen: Boolean)

// Simuloitu palvelin: 7 riviä, 3 riviä sivulla.
fun haeSivu(numero: Int): Sivu {
    println("  (haetaan sivu $numero)")
    val kaikki = (1..7).map { "rivi $it" }
    val rivit = kaikki.drop(numero * 3).take(3)
    return Sivu(rivit, (numero + 1) * 3 >= kaikki.size)
}

fun kaikkiRivit(): Sequence<String> = sequence {
    var numero = 0
    while (true) {
        val sivu = haeSivu(numero++)
        yieldAll(sivu.rivit)
        if (sivu.viimeinen) break
    }
}

fun main() {
    // Vain tarvittavat sivut haetaan.
    println(kaikkiRivit().take(4).toList())
    println(kaikkiRivit().count())
}
