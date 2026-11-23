// Rakenteinen rinnakkaisuus kotlinx.coroutinesilla: lapsikorutiinit
// elävät vanhempansa näkyvyysalueessa (scope). Vanhempi odottaa lapset,
// virhe peruu sisarukset, ja peruutus etenee alaspäin.

import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.async
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.withTimeoutOrNull
import kotlin.time.measureTime

data class Tuote(val id: Int, val nimi: String)

// Simuloidut verkkokutsut: delay keskeyttää, ei varaa säiettä.
suspend fun haeTuote(id: Int): Tuote {
    delay(400)
    return Tuote(id, "tuote $id")
}

suspend fun haeHinta(id: Int): Long {
    delay(600)
    return id * 1_000L
}

// Kaksi kutsua rinnakkain; funktio palaa vasta, kun molemmat ovat
// valmiita tai jompikumpi epäonnistuu.
suspend fun tuotesivu(id: Int): String = coroutineScope {
    val tuote = async { haeTuote(id) }
    val hinta = async { haeHinta(id) }
    "${tuote.await().nimi}: ${hinta.await()} snt"
}

suspend fun epaonnistuva() = coroutineScope {
    launch {
        try {
            delay(10_000)
        } catch (e: CancellationException) {
            println("  hidas haku peruttiin")
            throw e        // peruutusta ei saa niellä
        }
    }
    launch {
        delay(50)
        error("varastopalvelu ei vastaa")
    }
}

fun main() = runBlocking {
    val kesto = measureTime { println(tuotesivu(7)) }
    // 400 ms ja 600 ms rinnakkain: noin 600 ms, ei 1000 ms.
    println("rinnakkain: ${kesto.inWholeMilliseconds < 900}")

    try {
        epaonnistuva()
    } catch (e: IllegalStateException) {
        println("virhe: ${e.message}")
    }

    val tulos = withTimeoutOrNull(100) { haeHinta(1) }
    println("aikakatkaisu: $tulos")
}
