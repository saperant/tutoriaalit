// Kokoelmat: vain luku -rajapinnat, muunnokset ja ryhmittely
// henkilöstödatalle.

data class Tyontekija(
    val nimi: String, val osasto: String, val palkka: Int, val vuosi: Int,
)

fun main() {
    System.setOut(java.io.PrintStream(System.out, true, Charsets.UTF_8))
    val henkilot = listOf(
        Tyontekija("Aino", "kehitys", 5200, 2019),
        Tyontekija("Eero", "myynti", 4100, 2021),
        Tyontekija("Iida", "kehitys", 6100, 2015),
        Tyontekija("Oona", "tuki", 3600, 2023),
        Tyontekija("Ukko", "myynti", 4700, 2017),
    )

    // List on vain luku -näkymä, ei muuttumaton: sama olio voi muuttua
    // MutableList-viitteen kautta.
    val muokattava = mutableListOf("a")
    val nakyma: List<String> = muokattava
    muokattava += "b"
    println("näkymä: $nakyma")
    val kopio = muokattava.toList()      // puolustava kopio
    muokattava.clear()
    println("kopio: $kopio, näkymä: $nakyma")

    // Ryhmittely ja koosteet.
    val osastoittain = henkilot.groupBy { it.osasto }
    for ((osasto, jasenet) in osastoittain) {
        println("$osasto: ${jasenet.map { it.nimi }} " +
            "ka ${jasenet.map { it.palkka }.average()}")
    }
    val nimella = henkilot.associateBy { it.nimi }
    println("Iidan osasto: ${nimella["Iida"]?.osasto}")

    // Järjestys usealla avaimella.
    val jarjestetty = henkilot.sortedWith(
        compareBy<Tyontekija> { it.osasto }.thenByDescending { it.palkka },
    )
    println(jarjestetty.joinToString { "${it.osasto}/${it.nimi}" })

    // partition, sumOf, maxBy, chunked ja windowed.
    val (vanhat, uudet) = henkilot.partition { it.vuosi < 2020 }
    println("ennen 2020: ${vanhat.size}, myöhemmin: ${uudet.size}")
    println("palkkasumma ${henkilot.sumOf { it.palkka }}")
    println("suurin: ${henkilot.maxBy { it.palkka }.nimi}")
    println(henkilot.map { it.nimi }.chunked(2))
    println((1..6).windowed(3) { it.sum() })

    // getOrPut: hae tai luo arvo yhdellä kutsulla (hakemisto, välimuisti).
    val alkukirjaimittain = mutableMapOf<Char, MutableList<String>>()
    for (h in henkilot) {
        alkukirjaimittain.getOrPut(h.osasto.first()) { mutableListOf() } +=
            h.nimi
    }
    println(alkukirjaimittain)
}
