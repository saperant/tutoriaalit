// Tyyppiturvallinen rakentaja (DSL): vastaanottajallinen lambda
// (Taulukko.() -> Unit) ja @DslMarker, joka estää ulomman vastaanottajan
// vahingossa tapahtuvan käytön.

@DslMarker
annotation class RaporttiDsl

@RaporttiDsl
class Raportti(private val otsikko: String) {
    private val osat = mutableListOf<String>()

    fun kappale(teksti: String) {
        osat += teksti
    }

    fun taulukko(lohko: Taulukko.() -> Unit) {
        osat += Taulukko().apply(lohko).muotoile()
    }

    fun muotoile() = buildString {
        appendLine(otsikko.uppercase())
        appendLine("=".repeat(otsikko.length))
        osat.forEach { appendLine(it) }
    }
}

@RaporttiDsl
class Taulukko {
    private var otsakkeet = listOf<String>()
    private val rivit = mutableListOf<List<String>>()

    fun otsake(vararg sarakkeet: String) {
        otsakkeet = sarakkeet.toList()
    }

    fun rivi(vararg solut: Any) {
        require(solut.size == otsakkeet.size) { "sarakemäärä" }
        rivit += solut.map { it.toString() }
    }

    fun muotoile(): String {
        val kaikki = listOf(otsakkeet) + rivit
        val leveys = otsakkeet.indices.map { i ->
            kaikki.maxOf { it[i].length }
        }
        return kaikki.joinToString("\n") { rivi ->
            rivi.mapIndexed { i, s -> s.padEnd(leveys[i]) }
                .joinToString(" | ")
                .trimEnd()
        }
    }
}

fun raportti(otsikko: String, lohko: Raportti.() -> Unit): String =
    Raportti(otsikko).apply(lohko).muotoile()

fun main() {
    System.setOut(java.io.PrintStream(System.out, true, Charsets.UTF_8))
    val myynti = mapOf("Helsinki" to 1_250, "Tampere" to 830, "Oulu" to 410)
    val teksti = raportti("Myynti marraskuu") {
        kappale("Kaupungit myynnin mukaan.")
        taulukko {
            otsake("kaupunki", "kpl", "osuus")
            val yhteensa = myynti.values.sum()
            for ((kaupunki, kpl) in myynti) {
                rivi(kaupunki, kpl, "${kpl * 100 / yhteensa} %")
            }
            // kappale("...")  // ei käänny: @DslMarker estää
        }
        kappale("Yhteensä ${myynti.values.sum()} kpl.")
    }
    print(teksti)
}
