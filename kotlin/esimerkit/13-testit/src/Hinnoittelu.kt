// Testattava logiikka: tilauksen hinta alennuksineen.
package hinnoittelu

data class Rivi(val tuote: String, val sentit: Long, val maara: Int) {
    init {
        require(sentit >= 0) { "hinta < 0: $tuote" }
        require(maara > 0) { "määrä <= 0: $tuote" }
    }
}

sealed interface Alennus {
    data class Prosentti(val prosentti: Int) : Alennus {
        init { require(prosentti in 0..100) { "prosentti: $prosentti" } }
    }
    data class Kynnys(val raja: Long, val vahennys: Long) : Alennus
}

fun valisumma(rivit: List<Rivi>): Long = rivit.sumOf { it.sentit * it.maara }

fun yhteensa(rivit: List<Rivi>, alennus: Alennus? = null): Long {
    val summa = valisumma(rivit)
    return when (alennus) {
        null -> summa
        is Alennus.Prosentti -> summa * (100 - alennus.prosentti) / 100
        is Alennus.Kynnys ->
            if (summa >= alennus.raja) summa - alennus.vahennys else summa
    }
}
