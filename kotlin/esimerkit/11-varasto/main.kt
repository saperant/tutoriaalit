// Ohut pääohjelma: logiikka on paketeissa, joita voi testata erikseen.
import varasto.Otto
import varasto.muistivarasto
import varasto.malli.Koodi
import varasto.malli.Tuote

fun main() {
    System.setOut(java.io.PrintStream(System.out, true, Charsets.UTF_8))
    val varasto = muistivarasto()
    varasto.lisaa(Tuote(Koodi("RUU-001"), "ruuvi M4", 500))
    varasto.lisaa(Tuote(Koodi("MUT-004"), "mutteri M4", 120))
    varasto.lisaa(Tuote(Koodi("RUU-001"), "ruuvi M4", 250))

    val tilaukset = listOf("RUU-001" to 600, "MUT-004" to 200, "XYZ-999" to 1)
    for ((koodi, maara) in tilaukset) {
        val teksti = when (val tulos = varasto.ota(Koodi(koodi), maara)) {
            is Otto.Ok -> "otettu $maara, jäljellä ${tulos.jaljella}"
            is Otto.EiRiita -> "vain ${tulos.saatavilla} saatavilla"
            Otto.Tuntematon -> "tuntematon tuote"
        }
        println("$koodi: $teksti")
    }
    varasto.hyllyssa().forEach { println("${it.koodi.arvo} ${it.hyllyssa}") }
    println(runCatching { Koodi("ruuvi") }.exceptionOrNull()?.message)
}
