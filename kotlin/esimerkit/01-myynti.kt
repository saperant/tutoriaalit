// Myyntiraportti: lukee rivejä "tuote;määrä;yksikköhinta" ja tulostaa
// tuotteittaiset summat suurimmasta pienimpään. Virheelliset rivit
// raportoidaan ja ohitetaan.

data class Myynti(val tuote: String, val maara: Int, val sentit: Long)

fun jasenna(rivi: String): Myynti? {
    val osat = rivi.split(';').map { it.trim() }
    if (osat.size != 3) return null
    val maara = osat[1].toIntOrNull() ?: return null
    val hinta = osat[2].replace(',', '.').toBigDecimalOrNull()
        ?: return null
    val sentit = hinta.movePointRight(2).toLong()
    return Myynti(osat[0], maara, maara * sentit)
}

fun euroina(sentit: Long): String =
    "%d,%02d €".format(sentit / 100, sentit % 100)

fun main() {
    System.setOut(java.io.PrintStream(System.out, true, Charsets.UTF_8))
    val myynnit = mutableListOf<Myynti>()
    generateSequence(::readlnOrNull).forEachIndexed { i, rivi ->
        if (rivi.isBlank()) return@forEachIndexed
        val myynti = jasenna(rivi)
        if (myynti == null) {
            println("rivi ${i + 1} ohitettu: $rivi")
        } else {
            myynnit += myynti
        }
    }
    val summat = myynnit
        .groupBy { it.tuote }
        .mapValues { (_, rivit) -> rivit.sumOf { it.sentit } }
        .entries
        .sortedByDescending { it.value }
    for ((tuote, sentit) in summat) {
        println("${tuote.padEnd(10)} ${euroina(sentit).padStart(10)}")
    }
    println("yhteensä   ${euroina(summat.sumOf { it.value }).padStart(10)}")
}
