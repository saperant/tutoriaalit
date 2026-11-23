// Yhteiskäyttö Javan kanssa: annotaatiot ohjaavat, millaisia
// JVM-metodeja Kotlin-koodista syntyy Java-kutsujille. Javan
// reflektio näyttää tuloksen.

import java.lang.reflect.Modifier

class Hinnoittelu {
    // @JvmOverloads: oletusargumenteista syntyy ylikuormitukset.
    @JvmOverloads
    fun hinta(perus: Long, alv: Int = 255, alennus: Int = 0): Long =
        perus * (1000 + alv) / 1000 * (100 - alennus) / 100

    companion object {
        // @JvmStatic: Hinnoittelu.oletus() Javasta ilman Companionia.
        @JvmStatic
        fun oletus() = Hinnoittelu()

        // @JvmField: julkinen kenttä ilman getteriä.
        @JvmField
        val VALUUTTA = "EUR"
    }
}

// @JvmName: tiedoston funktio näkyy Javalle tällä nimellä.
@JvmName("muotoileSentit")
fun Long.euroina(): String = "%d,%02d".format(this / 100, this % 100)

fun main() {
    System.setOut(java.io.PrintStream(System.out, true, Charsets.UTF_8))
    val metodit = Hinnoittelu::class.java.declaredMethods
        .filter { it.name == "hinta" || it.name == "oletus" }
        .map { m ->
            val alku = if (Modifier.isStatic(m.modifiers)) "static " else ""
            val parametrit = m.parameterTypes.joinToString { it.name }
            "$alku${m.name}($parametrit)"
        }
        .sorted()
    metodit.forEach(::println)
    val kentta = Hinnoittelu::class.java.getField("VALUUTTA")
    val staattinen = Modifier.isStatic(kentta.modifiers)
    println("kenttä ${kentta.name}, static=$staattinen")

    val h = Hinnoittelu.oletus()
    println(h.hinta(10_000).euroina() + " " + Hinnoittelu.VALUUTTA)
    println(h.hinta(10_000, alennus = 20).euroina())

    // Javan kokoelmat ovat Kotlinille tavallisia kokoelmia.
    val jono = java.util.PriorityQueue(listOf(5, 1, 3))
    println(generateSequence { jono.poll() }.toList())
}
