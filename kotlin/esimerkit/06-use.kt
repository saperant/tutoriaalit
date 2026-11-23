// Resurssien hallinta: use sulkee AutoCloseable-olion kaikilla poluilla
// (Javan try-with-resources), myös poikkeuksen sattuessa.

import java.io.File

class Lukko(private val nimi: String) : AutoCloseable {
    init { println("lukitaan $nimi") }
    override fun close() = println("vapautetaan $nimi")
}

fun kirjoitaRaportti(tiedosto: File, rivit: List<String>) {
    tiedosto.bufferedWriter().use { kirjoittaja ->
        for (rivi in rivit) {
            kirjoittaja.write(rivi)
            kirjoittaja.newLine()
        }
    }   // suljetaan ja puskuri tyhjennetään tässä
}

fun main() {
    System.setOut(java.io.PrintStream(System.out, true, Charsets.UTF_8))
    val tiedosto = File("raportti.txt")
    kirjoitaRaportti(tiedosto, listOf("alku", "keskus", "loppu"))
    // useLines avaa, lukee laiskasti ja sulkee.
    val pituus = tiedosto.useLines { rivit -> rivit.sumOf { it.length } }
    println("merkkejä $pituus")

    // Sisäkkäiset resurssit suljetaan käänteisessä järjestyksessä.
    Lukko("tili A").use {
        Lukko("tili B").use {
            println("siirto A -> B")
        }
    }

    // Poikkeus ei estä sulkemista.
    try {
        Lukko("tili C").use { error("saldo ei riitä") }
    } catch (e: IllegalStateException) {
        println("virhe: ${e.message}")
    }
    tiedosto.delete()
}
