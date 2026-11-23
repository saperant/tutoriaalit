// Luokat: pääkonstruktori, ominaisuudet, invariantit ja companion object.

class Tili private constructor(
    val iban: String,
    saldoAlussa: Long,
) {
    // Ominaisuus, jonka asetus on yksityinen: lukeminen on julkista.
    var saldoSentteina: Long = saldoAlussa
        private set

    private val tapahtumat = mutableListOf<Long>()

    init {
        require(saldoAlussa >= 0) { "alkusaldo ei voi olla negatiivinen" }
    }

    // Laskettu ominaisuus: ei taustakenttää.
    val tapahtumia: Int get() = tapahtumat.size

    fun pane(sentit: Long) {
        require(sentit > 0) { "summan on oltava positiivinen" }
        saldoSentteina += sentit
        tapahtumat += sentit
    }

    fun nosta(sentit: Long): Boolean {
        require(sentit > 0) { "summan on oltava positiivinen" }
        if (sentit > saldoSentteina) return false
        saldoSentteina -= sentit
        tapahtumat += -sentit
        return true
    }

    override fun toString() = "Tili($iban, $saldoSentteina snt)"

    // Javan staattiset tehdasmetodit: companion object.
    companion object {
        private val MUOTO = Regex("""FI\d{16}""")

        fun avaa(iban: String, alkusaldo: Long = 0): Tili {
            val siisti = iban.replace(" ", "").uppercase()
            require(MUOTO.matches(siisti)) { "virheellinen IBAN: $iban" }
            return Tili(siisti, alkusaldo)
        }
    }
}

// object: säieturvallisesti laiskasti luotava singleton.
object Tunnukset {
    private var seuraava = 1
    fun uusi() = "T-${seuraava++}"
}

fun main() {
    val tili = Tili.avaa("fi21 1234 5600 0007 85", 10_000)
    tili.pane(2_500)
    println("nosto 20000: ${tili.nosta(20_000)}")
    println("nosto 5000: ${tili.nosta(5_000)}")
    println("$tili, ${tili.tapahtumia} tapahtumaa")
    // tili.saldoSentteina = 0     // ei käänny: setter on private

    val virhe = runCatching { Tili.avaa("SE123") }.exceptionOrNull()
    println(virhe?.message)
    println(listOf(Tunnukset.uusi(), Tunnukset.uusi()))
}
