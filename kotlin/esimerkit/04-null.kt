// Null-turvallisuus käyttäjäprofiilin käsittelyssä.

data class Osoite(val katu: String, val postinumero: String?)
data class Kayttaja(val nimi: String, val osoite: Osoite?, val ika: Int?)

fun postinumero(k: Kayttaja): String =
    k.osoite?.postinumero ?: "tuntematon"      // turvallinen kutsu + elvis

fun tervehdys(k: Kayttaja?): String {
    if (k == null) return "Hei, vieras!"
    return "Hei, ${k.nimi}!"                   // älykäs tyyppimuunnos
}

fun ikaluokka(k: Kayttaja): String {
    val ika = k.ika ?: return "ikä ei tiedossa" // elvis + return
    return if (ika >= 18) "aikuinen" else "alaikäinen"
}

fun main() {
    System.setOut(java.io.PrintStream(System.out, true, Charsets.UTF_8))
    val kayttajat = listOf(
        Kayttaja("Aino", Osoite("Rantatie 1", "00100"), 34),
        Kayttaja("Eino", Osoite("Kujatie 5", null), null),
        Kayttaja("Iida", null, 16),
    )
    for (k in kayttajat) {
        println("${k.nimi}: ${postinumero(k)}, ${ikaluokka(k)}")
    }
    println(tervehdys(null))
    println(tervehdys(kayttajat.first()))

    // let suorittaa lohkon vain, kun arvo ei ole null.
    kayttajat.last().ika?.let { println("Iidan ikä: $it") }

    // Kokoelmien null-funktiot: mapNotNull, filterNotNull, firstOrNull.
    val iat = kayttajat.mapNotNull { it.ika }
    println("tunnetut iät: $iat, keskiarvo ${iat.average()}")
    println(kayttajat.firstOrNull { it.nimi.startsWith("Ö") })

    // Javan rajapinnasta tuleva arvo: ilmoita tyyppi itse (String?),
    // niin kääntäjä vaatii null-tarkistuksen.
    val koti: String? = System.getenv("TUTORIAALIN_EI_OLEMASSA")
    println("ympäristö: ${koti ?: "ei asetettu"}")

    // requireNotNull: null on ohjelmointivirhe, ei odotettu tilanne.
    val aino = requireNotNull(kayttajat.find { it.nimi == "Aino" }) {
        "Aino puuttuu"
    }
    println("${aino.nimi} löytyi")
}
