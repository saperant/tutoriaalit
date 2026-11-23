// Laajennusfunktiot ja -ominaisuudet: uusia operaatioita valmiille
// tyypeille. Laajennus on staattinen apufunktio, ei virtuaalinen metodi.

import java.time.LocalDate

fun String.hetuSyntymapaiva(): LocalDate? {
    if (length != 11) return null
    val vuosisata = when (this[6]) {
        '+' -> 1800
        '-', 'Y', 'X', 'W', 'V', 'U' -> 1900
        'A', 'B', 'C', 'D', 'E', 'F' -> 2000
        else -> return null
    }
    val pp = substring(0, 2).toIntOrNull() ?: return null
    val kk = substring(2, 4).toIntOrNull() ?: return null
    val vv = substring(4, 6).toIntOrNull() ?: return null
    return runCatching { LocalDate.of(vuosisata + vv, kk, pp) }.getOrNull()
}

// Laajennusominaisuus: ei taustakenttää, lasketaan joka kerta.
val LocalDate.onViikonloppu: Boolean
    get() = dayOfWeek.value >= 6

// Nullable-vastaanotin: kutsu onnistuu myös null-arvolle.
fun String?.tyhjaksiViiva(): String = if (isNullOrBlank()) "-" else this

open class Muoto
class Ympyra : Muoto()

fun Muoto.nimi() = "muoto"
fun Ympyra.nimi() = "ympyrä"

fun main() {
    System.setOut(java.io.PrintStream(System.out, true, Charsets.UTF_8))
    for (tunnus in listOf("131052-308T", "010123A123F", "310299-1234")) {
        val pvm = tunnus.hetuSyntymapaiva()
        println("$tunnus -> ${pvm ?: "virheellinen"}")
    }
    println(LocalDate.of(2026, 11, 21).onViikonloppu)
    val puuttuva: String? = null
    println(puuttuva.tyhjaksiViiva() + " " + "arvo".tyhjaksiViiva())

    // Laajennus valitaan staattisen tyypin mukaan, ei ajonaikaisen.
    val m: Muoto = Ympyra()
    println("${m.nimi()} / ${Ympyra().nimi()}")
}
