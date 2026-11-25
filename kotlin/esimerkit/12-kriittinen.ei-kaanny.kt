// synchronized ei sovi korutiineihin: keskeytyskohta kriittisen alueen
// sisällä on käännösvirhe, koska korutiini voi jatkua toisessa
// säikeessä, joka ei omista lukkoa.

import kotlin.coroutines.suspendCoroutine
import kotlin.coroutines.resume

private val lukko = Any()
private val loki = mutableListOf<String>()

// Keskeyttävä funktio, esimerkiksi kirjoitus levylle tai verkkoon.
suspend fun tallenna(rivi: String): Unit = suspendCoroutine { jatko ->
    loki += rivi
    jatko.resume(Unit)
}

suspend fun kirjaa(rivi: String) {
    synchronized(lukko) {
        loki += "aloitus"
        tallenna(rivi) // @virhe
    }
}

fun main() {
    System.setOut(java.io.PrintStream(System.out, true, Charsets.UTF_8))
    println("lokissa ${loki.size} riviä")
}
