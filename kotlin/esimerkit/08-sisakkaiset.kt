// Oliolauseke sekä sisäkkäinen ja inner-luokka.

// Kaksi metodia: lambda ei riitä toteutukseksi.
interface Kuuntelija {
    fun avattu(nimi: String)
    fun suljettu(nimi: String)
}

class Ovi(private val nimi: String) {
    private var avauksia = 0

    // Sisäkkäinen luokka on oletuksena staattinen: ei viitettä oveen.
    class Asetukset(val lukittava: Boolean)

    // inner-luokka näkee ulomman olion jäsenet.
    inner class Laskuri {
        fun raportti() = "$nimi avattu $avauksia kertaa"
    }

    fun kayta(kuuntelija: Kuuntelija) {
        avauksia++
        kuuntelija.avattu(nimi)
        kuuntelija.suljettu(nimi)
    }
}

fun main() {
    System.setOut(java.io.PrintStream(System.out, true, Charsets.UTF_8))
    val loki = mutableListOf<String>()
    // Oliolauseke: nimetön olio, joka toteuttaa rajapinnan ja näkee
    // ympäröivän funktion muuttujat.
    val kirjaaja = object : Kuuntelija {
        override fun avattu(nimi: String) {
            loki += "$nimi auki"
        }

        override fun suljettu(nimi: String) {
            loki += "$nimi kiinni"
        }
    }
    val ovi = Ovi("etuovi")
    ovi.kayta(kirjaaja)
    ovi.kayta(kirjaaja)
    println(loki.distinct())
    println(ovi.Laskuri().raportti())
    println(Ovi.Asetukset(lukittava = true).lukittava)
}
