// Sequence vs. List: lista laskee jokaisen vaiheen kokonaan
// välitaulukoksi, sekvenssi käsittelee alkion kerrallaan ja lopettaa,
// kun tulos on valmis.

fun main() {
    System.setOut(java.io.PrintStream(System.out, true, Charsets.UTF_8))
    val luvut = (1..6).toList()

    println("List:")
    val l = luvut
        .map { println("  map $it"); it * it }
        .filter { println("  filter $it"); it > 4 }
        .first()
    println("tulos $l")

    println("Sequence:")
    val s = luvut.asSequence()
        .map { println("  map $it"); it * it }
        .filter { println("  filter $it"); it > 4 }
        .first()
    println("tulos $s")

    // Ääretön sekvenssi: Collatzin jono luvusta 27.
    val collatz = generateSequence(27) { n ->
        when {
            n == 1 -> null
            n % 2 == 0 -> n / 2
            else -> 3 * n + 1
        }
    }
    println("Collatz(27): ${collatz.count()} jäsentä, " +
        "suurin ${collatz.max()}")
}
