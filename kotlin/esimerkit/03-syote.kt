// Lukee lämpötiloja riveittäin, kunnes syöte loppuu. Virheelliset ja
// fysikaalisesti mahdottomat arvot raportoidaan.

const val ABSOLUUTTINEN_NOLLA = -273.15

fun main() {
    System.setOut(java.io.PrintStream(System.out, true, Charsets.UTF_8))
    val arvot = mutableListOf<Double>()
    var rivi = 0
    while (true) {
        val teksti = readlnOrNull() ?: break   // null = syöte loppui
        rivi++
        val arvo = teksti.trim().replace(',', '.').toDoubleOrNull()
        when {
            teksti.isBlank() -> continue
            arvo == null -> println("rivi $rivi: ei luku: '$teksti'")
            arvo < ABSOLUUTTINEN_NOLLA ->
                println("rivi $rivi: alle absoluuttisen nollan: $arvo")
            else -> arvot += arvo
        }
    }
    if (arvot.isEmpty()) {
        println("ei kelvollisia arvoja")
        return
    }
    println("n=${arvot.size} min=${arvot.min()} max=${arvot.max()} " +
        "ka=${"%.1f".format(arvot.average())}")
}
