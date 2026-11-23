// Rajapinnat, abstraktit ja avoimet luokat sekä enum. Luokat ovat
// oletuksena final: periytyminen on sallittava erikseen (open).

interface Muoto {
    val nimi: String
    fun ala(): Double
    // Oletustoteutus rajapinnassa.
    fun kuvaus() = "$nimi, ala %.2f".format(ala())
}

abstract class Monikulmio(final override val nimi: String) : Muoto {
    abstract val sivut: List<Double>
    fun piiri() = sivut.sum()
}

class Suorakulmio(val leveys: Double, val korkeus: Double) :
    Monikulmio("suorakulmio") {
    override val sivut = listOf(leveys, korkeus, leveys, korkeus)
    override fun ala() = leveys * korkeus
}

class Ympyra(private val r: Double) : Muoto {
    override val nimi = "ympyrä"
    override fun ala() = Math.PI * r * r
}

// enum: kiinteä joukko arvoja ominaisuuksineen ja metodeineen.
enum class Prioriteetti(val vasteaikaTunteina: Int) {
    KRIITTINEN(1), KORKEA(8), NORMAALI(72);

    fun kiireellisempiKuin(muu: Prioriteetti) = ordinal < muu.ordinal
}

fun main() {
    System.setOut(java.io.PrintStream(System.out, true, Charsets.UTF_8))
    val muodot: List<Muoto> = listOf(Suorakulmio(3.0, 2.0), Ympyra(1.0))
    muodot.forEach { println(it.kuvaus()) }
    println("piiri ${(muodot[0] as Monikulmio).piiri()}")

    println(Prioriteetti.entries.map { "$it=${it.vasteaikaTunteina}h" })
    println(Prioriteetti.valueOf("KORKEA")
        .kiireellisempiKuin(Prioriteetti.NORMAALI))
}
