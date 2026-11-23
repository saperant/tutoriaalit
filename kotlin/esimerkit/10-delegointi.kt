// Delegointi: luokan rajapinnan delegointi (by) ja delegoidut
// ominaisuudet (lazy, observable, map).

import kotlin.properties.Delegates

// Koostaminen periytymisen sijaan: kaikki MutableSet-metodit ohjataan
// sisäiselle joukolle, vain add ja addAll ylikirjoitetaan.
class LaskevaJoukko<T>(
    private val sisa: MutableSet<T> = HashSet(),
) : MutableSet<T> by sisa {
    var yrityksia = 0
        private set

    override fun add(element: T): Boolean {
        yrityksia++
        return sisa.add(element)
    }

    override fun addAll(elements: Collection<T>): Boolean =
        elements.map { add(it) }.any { it }
}

class Asetukset(arvot: Map<String, Any?>) {
    // Ominaisuudet luetaan mapista nimen perusteella.
    val palvelin: String by arvot
    val portti: Int by arvot

    // Lasketaan ensimmäisellä käytöllä, oletuksena säieturvallisesti.
    val osoite: String by lazy {
        println("(lasketaan osoite)")
        "https://$palvelin:$portti"
    }

    // Kuuntelija jokaiselle muutokselle.
    var taso: String by Delegates.observable("INFO") { _, vanha, uusi ->
        println("lokitaso $vanha -> $uusi")
    }
}

fun main() {
    System.setOut(java.io.PrintStream(System.out, true, Charsets.UTF_8))
    val joukko = LaskevaJoukko<String>()
    joukko.addAll(listOf("a", "b", "a"))
    joukko.add("b")
    println("${joukko.size} alkiota, ${joukko.yrityksia} lisäysyritystä")

    val a = Asetukset(mapOf("palvelin" to "api.example.org", "portti" to 443))
    println(a.osoite)
    println(a.osoite)
    a.taso = "DEBUG"
}
