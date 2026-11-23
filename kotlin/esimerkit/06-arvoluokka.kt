// Arvoluokka (value class): tyyppiturvallinen kääre ilman olion hintaa.
// Ajonaikana Sentit on pelkkä long, kunhan sitä ei käytetä
// nullable- tai geneerisenä tyyppinä.

@JvmInline
value class Sentit(val arvo: Long) {
    operator fun plus(muu: Sentit) = Sentit(Math.addExact(arvo, muu.arvo))
    operator fun times(kerroin: Int) =
        Sentit(Math.multiplyExact(arvo, kerroin.toLong()))
    override fun toString() = "%d,%02d €".format(arvo / 100, arvo % 100)
}

@JvmInline
value class TuoteId(val arvo: String)

data class Rivi(val tuote: TuoteId, val hinta: Sentit, val maara: Int)

// Parametrien järjestystä ei voi sekoittaa: tyypit ovat eri.
fun rivi(tuote: TuoteId, hinta: Sentit, maara: Int) =
    Rivi(tuote, hinta, maara)

fun main() {
    System.setOut(java.io.PrintStream(System.out, true, Charsets.UTF_8))
    val ostoskori = listOf(
        rivi(TuoteId("kahvi-500"), Sentit(649), 2),
        rivi(TuoteId("maito-1l"), Sentit(119), 3),
    )
    val summa = ostoskori
        .map { it.hinta * it.maara }
        .fold(Sentit(0)) { a, b -> a + b }
    println("yhteensä $summa")

    // Ajonaikainen esitys: kenttä on primitiivi long, ei olio.
    val kentta = Rivi::class.java.getDeclaredField("hinta")
    println("Rivi.hinta JVM:ssä: ${kentta.type}")

    // Nullable- tai geneerisessä käytössä arvo laatikoidaan.
    val ehka: Sentit? = summa
    println("nullable: ${(ehka as Any).javaClass.simpleName}")
}
