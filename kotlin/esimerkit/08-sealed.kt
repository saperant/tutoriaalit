// Suljettu hierarkia ja kattava when: maksutavan käsittely.

sealed interface Maksutapa {
    data class Kortti(val numero: String, val voimassa: String) : Maksutapa
    data class Lasku(val viite: String, val erapaivia: Int = 14) : Maksutapa
    data class Lahjakortti(val koodi: String, val saldo: Long) : Maksutapa
    data object Kateinen : Maksutapa
}

// when-lauseke on kattava: uusi alatyyppi tekee tästä käännösvirheen,
// joten käsittelyä ei voi unohtaa. Siksi else-haaraa ei kirjoiteta.
fun kuvaus(tapa: Maksutapa): String = when (tapa) {
    is Maksutapa.Kortti -> "kortti **** ${tapa.numero.takeLast(4)}"
    is Maksutapa.Lasku -> "lasku, viite ${tapa.viite}, ${tapa.erapaivia} pv"
    is Maksutapa.Lahjakortti -> "lahjakortti (saldo ${tapa.saldo} snt)"
    Maksutapa.Kateinen -> "käteinen"
}

fun riittaako(tapa: Maksutapa, summa: Long): Boolean = when (tapa) {
    is Maksutapa.Lahjakortti -> tapa.saldo >= summa
    is Maksutapa.Kortti, is Maksutapa.Lasku, Maksutapa.Kateinen -> true
}

fun main() {
    System.setOut(java.io.PrintStream(System.out, true, Charsets.UTF_8))
    val tavat = listOf(
        Maksutapa.Kortti("4111111111111111", "12/28"),
        Maksutapa.Lasku("RF18 5390 0754 7034"),
        Maksutapa.Lahjakortti("LK-77", 2_000),
        Maksutapa.Kateinen,
    )
    for (t in tavat) println("${kuvaus(t)}: ${riittaako(t, 2_500)}")

    // data class: equals, hashCode, toString, copy ja purku.
    val lasku = Maksutapa.Lasku("RF18 5390 0754 7034")
    val pidempi = lasku.copy(erapaivia = 30)
    val (viite, paivat) = pidempi
    println("$viite / $paivat, sama viite: ${lasku.viite == viite}")
    println(lasku == Maksutapa.Lasku("RF18 5390 0754 7034"))
    println(setOf(lasku, lasku.copy()).size)
}
