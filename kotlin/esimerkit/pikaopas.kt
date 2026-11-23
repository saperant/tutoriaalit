// Pikaoppaan koodi: jokainen osa on testattu tämän tiedoston osana.

// @alku tyypit
@JvmInline value class Euro(val sentit: Long)

data class Tuote(val nimi: String, val hinta: Euro, val ale: Int? = null)

sealed interface Tulos<out T> {
    data class Ok<T>(val arvo: T) : Tulos<T>
    data class Virhe(val syy: String) : Tulos<Nothing>
}

enum class Taso { INFO, VAROITUS, VIRHE }

object Laskuri {
    var arvo = 0
        private set
    fun kasvata() = ++arvo
}
// @loppu tyypit

// @alku funktiot
fun hinta(t: Tuote, maara: Int = 1): Long =
    t.hinta.sentit * maara * (100 - (t.ale ?: 0)) / 100

fun String.otsikoksi() = replaceFirstChar { it.uppercase() }

inline fun <reified T> Any.onko() = this is T
// @loppu funktiot

fun main() {
    // @alku perus
    val nimi = "kotlin"                  // muuttumaton viite
    var n = 0                            // muuttuva
    n += 2
    val kuvaus = when {
        n > 5 -> "iso"
        n in 1..5 -> "pieni"
        else -> "nolla"
    }
    println("${nimi.otsikoksi()} $n $kuvaus ${nimi.length}")
    for (i in 0..<3) print("$i ")
    println((10 downTo 0 step 5).toList())
    // @loppu perus

    // @alku null
    val syote: String? = readlnOrNull()
    val pituus = syote?.trim()?.length ?: 0
    val luku = syote?.trim()?.toIntOrNull() ?: -1
    syote?.let { println("luettiin '$it'") }
    println("$pituus $luku")
    // @loppu null

    // @alku kokoelmat
    val kori = listOf(
        Tuote("kahvi", Euro(650), ale = 10),
        Tuote("pulla", Euro(220)),
    )
    val summa = kori.sumOf { hinta(it, 2) }
    val nimet = kori.map { it.nimi }.sorted()
    val hinnat = kori.associate { it.nimi to it.hinta.sentit }
    val (alessa, muut) = kori.partition { it.ale != null }
    println("$summa $nimet $hinnat ${alessa.size}/${muut.size}")
    val m = mutableMapOf<String, Int>()
    m.merge("a", 1, Int::plus)
    println(m.getOrDefault("b", 0))
    // @loppu kokoelmat

    // @alku muut
    val t: Tulos<Int> = Tulos.Ok(42)
    val teksti = when (t) {
        is Tulos.Ok -> "ok ${t.arvo}"
        is Tulos.Virhe -> "virhe ${t.syy}"
    }
    val varmistettu = runCatching { require(n > 0) { "n" }; n }
        .getOrElse { 0 }
    val olio = StringBuilder().apply { append("a"); append("b") }
    println("$teksti $varmistettu $olio ${Laskuri.kasvata()}")
    println("${Taso.entries} ${"x".onko<String>()} ${kori[1].copy(ale = 5)}")
    // @loppu muut
}
