// Mitä suspend tarkoittaa: pieni yksisäikeinen suorittaja pelkillä
// kotlin.coroutines-perusrakenteilla. Kääntäjä muuntaa suspend-funktion
// tilakoneeksi, joka saa jatkon (Continuation); suorittaja päättää,
// milloin jatko ajetaan. kotlinx.coroutines toteuttaa saman isommin.

import kotlin.coroutines.Continuation
import kotlin.coroutines.EmptyCoroutineContext
import kotlin.coroutines.resume
import kotlin.coroutines.startCoroutine
import kotlin.coroutines.suspendCoroutine

class Suorittaja {
    private val valmiina = ArrayDeque<() -> Unit>()

    // Käynnistää korutiinin; se ajetaan ensimmäiseen keskeytykseen asti
    // vasta, kun aja() käsittelee jonon.
    fun kaynnista(nimi: String, lohko: suspend Suorittaja.() -> Unit) {
        val valmis = Continuation<Unit>(EmptyCoroutineContext) { tulos ->
            println("[$nimi valmis: ${tulos.isSuccess}]")
        }
        valmiina += { lohko.startCoroutine(this, valmis) }
    }

    // Luovuttaa vuoron: jatko jonon perälle.
    suspend fun vuoro() = suspendCoroutine { jatko ->
        valmiina += { jatko.resume(Unit) }
    }

    fun aja() {
        while (valmiina.isNotEmpty()) valmiina.removeFirst()()
    }
}

fun main() {
    val s = Suorittaja()
    s.kaynnista("lataaja") {
        for (osa in 1..3) {
            println("lataaja: osa $osa")
            vuoro()
        }
    }
    s.kaynnista("tallentaja") {
        repeat(2) {
            println("tallentaja: kirjoitus ${it + 1}")
            vuoro()
        }
    }
    s.aja()
}
