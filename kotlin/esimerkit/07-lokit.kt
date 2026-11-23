// Lokianalyysi: lukee rivejä "aika taso palvelu viesti" ja raportoi
// virheet palveluittain sekä yleisimmät viestit.

data class Tapahtuma(
    val taso: String, val palvelu: String, val viesti: String,
)

private val RIVI = Regex("""^(\S+) (INFO|WARN|ERROR) (\S+) (.+)$""")

fun jasenna(rivi: String): Tapahtuma? =
    RIVI.matchEntire(rivi)?.destructured?.let { (_, taso, palvelu, viesti) ->
        Tapahtuma(taso, palvelu, viesti)
    }

fun main() {
    System.setOut(java.io.PrintStream(System.out, true, Charsets.UTF_8))
    val tapahtumat = generateSequence(::readlnOrNull)
        .mapNotNull(::jasenna)
        .toList()
    println("tapahtumia ${tapahtumat.size}")

    val tasoittain = tapahtumat.groupingBy { it.taso }.eachCount()
    println("tasot: ${tasoittain.toSortedMap()}")

    println("virheet palveluittain:")
    tapahtumat.filter { it.taso == "ERROR" }
        .groupingBy { it.palvelu }
        .eachCount()
        .entries
        .sortedWith(compareByDescending<Map.Entry<String, Int>> { it.value }
            .thenBy { it.key })
        .forEach { (palvelu, n) -> println("  ${palvelu.padEnd(8)} $n") }

    val yleisin = tapahtumat.groupingBy { it.viesti }.eachCount()
        .maxByOrNull { it.value }
    println("yleisin viesti: ${yleisin?.key} (${yleisin?.value})")
}
