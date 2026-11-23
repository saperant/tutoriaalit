// inline-funktiot: lambda kopioidaan kutsukohtaan, joten oliota ei
// luoda, return palaa ympäröivästä funktiosta ja tyyppiparametri voi
// olla reified (tunnettu ajonaikana).

// Kirjausapuri, joka ei maksa lambdasta mitään: inline. Samalla
// tavalla toimivat vakiokirjaston measureNanoTime, synchronized,
// withLock ja use.
inline fun <T> kirjaten(nimi: String, lohko: () -> T): T {
    println("> $nimi")
    val tulos = lohko()
    println("< $nimi = $tulos")
    return tulos
}

// reified: T on käytettävissä ajonaikana (is T, T::class).
inline fun <reified T> List<Any>.vainTyyppia(): List<T> =
    filter { it is T }.map { it as T }

fun ensimmainenNegatiivinen(luvut: List<Int>): Int? {
    luvut.forEach {
        if (it < 0) return it   // ei-paikallinen return: forEach on inline
    }
    return null
}

fun main() {
    System.setOut(java.io.PrintStream(System.out, true, Charsets.UTF_8))
    val summa = kirjaten("summa") { (1..1_000).sum() }
    println("kaksinkertainen ${summa * 2}")

    val sekalaiset: List<Any> = listOf(1, "kaksi", 3.0, "neljä", 5)
    println(sekalaiset.vainTyyppia<String>())
    println(sekalaiset.vainTyyppia<Int>().sum())
    // Vakiokirjasto tekee saman: filterIsInstance on inline + reified.
    println(sekalaiset.filterIsInstance<Double>())

    println(ensimmainenNegatiivinen(listOf(3, 1, -4, -1)))
    println(ensimmainenNegatiivinen(listOf(2, 7)))
}
