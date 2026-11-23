// Perustyypit, muunnokset ja muotoilu mittausdatan käsittelyssä.

fun main() {
    System.setOut(java.io.PrintStream(System.out, true, Charsets.UTF_8))
    // Tyyppi päätellään; val ei muutu, var voi muuttua.
    val anturi = "T-17"
    var naytteita = 0
    val lukemat = doubleArrayOf(21.5, 22.25, 19.75)
    naytteita += lukemat.size

    // Ei implisiittistä levennystä: Int ei muutu Longiksi itsestään.
    val tavut: Int = 1_500_000_000
    val yhteensa: Long = tavut.toLong() * 3
    println("tavuja yhteensä $yhteensa")

    // Kokonaisluvun ylivuoto kiertää kuten Javassa ...
    println("Int.MAX_VALUE + 1 = ${Int.MAX_VALUE + 1}")
    // ... ellei sitä tarkisteta erikseen.
    val tulos = runCatching { Math.multiplyExact(tavut, 3) }
    println("multiplyExact: ${tulos.exceptionOrNull()?.message}")

    // Jakolasku: kokonaisluvuilla katkaisu, liukuluvuilla ei.
    println("7 / 2 = ${7 / 2}, 7 % 2 = ${7 % 2}, 7.0 / 2 = ${7.0 / 2}")

    // Merkkijonopohjat ja muotoilu.
    val keskiarvo = lukemat.average()
    println("$anturi: $naytteita näytettä, ka %.2f °C".format(keskiarvo))
    println("min ${lukemat.min()}, max ${lukemat.max()}")

    // Raaka merkkijono: ei pakomerkkejä, trimIndent poistaa sisennyksen.
    val raportti = """
        anturi:  $anturi
        polku:   C:\data\$anturi.csv
    """.trimIndent()
    println(raportti)

    // Char on UTF-16-koodiyksikkö, ei merkki: U+1F321 (lämpömittari-
    // emoji) vie kaksi koodiyksikköä eli sijaisparin.
    val viesti = "lämpö " + Character.toString(0x1F321)
    println("${viesti.length} koodiyksikköä, " +
        "${viesti.codePointCount(0, viesti.length)} koodipistettä")
}
