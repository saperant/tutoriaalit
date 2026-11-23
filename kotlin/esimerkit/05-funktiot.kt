// Funktiot: oletus- ja nimetyt argumentit, funktiotyypit ja lambdat.

data class Ilmoitus(val otsikko: String, val tarkeys: Int, val kanava: String)

// Oletusarvot korvaavat Javan ylikuormitusketjut ja rakentajat.
fun ilmoitus(
    otsikko: String,
    tarkeys: Int = 1,
    kanava: String = "sähköposti",
) = Ilmoitus(otsikko, tarkeys, kanava)

// Funktiotyyppi (Ilmoitus) -> Boolean parametrina.
fun suodata(ilmoitukset: List<Ilmoitus>, ehto: (Ilmoitus) -> Boolean) =
    ilmoitukset.filter(ehto)

// Funktio palauttaa funktion: sulkeuma kaappaa raja-arvon.
fun vahintaan(raja: Int): (Ilmoitus) -> Boolean = { it.tarkeys >= raja }

// Häntärekursio: kääntäjä muuttaa silmukaksi, pino ei kasva.
tailrec fun syt(a: Long, b: Long): Long = if (b == 0L) a else syt(b, a % b)

fun onKiireellinen(i: Ilmoitus) = i.tarkeys >= 3

fun main() {
    System.setOut(java.io.PrintStream(System.out, true, Charsets.UTF_8))
    val lista = listOf(
        ilmoitus("Levytila vähissä", tarkeys = 2),
        ilmoitus("Palvelin alhaalla", 3, kanava = "tekstiviesti"),
        ilmoitus(kanava = "chat", otsikko = "Uusi versio"),
    )
    lista.forEach(::println)
    // Lambda viimeisenä argumenttina kirjoitetaan sulkujen ulkopuolelle.
    println(suodata(lista) { it.kanava != "chat" }.size)
    println(suodata(lista, vahintaan(2)).map { it.otsikko })
    println(suodata(lista, ::onKiireellinen).map { it.otsikko })
    println(syt(1_071, 462))

    // Paikallinen funktio näkee ympäröivän funktion muuttujat.
    var lahetetty = 0
    fun laheta(i: Ilmoitus) {
        lahetetty++
        println("-> ${i.kanava}: ${i.otsikko}")
    }
    lista.filter { it.tarkeys > 1 }.forEach(::laheta)
    println("lähetetty $lahetetty")
}
