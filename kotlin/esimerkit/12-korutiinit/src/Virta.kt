// Flow: asynkroninen, laiska arvovirta. Virta on kylmä: tuottaja
// käynnistyy jokaiselle keräilijälle erikseen.

import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.filter
import kotlinx.coroutines.flow.flow
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.flow.onCompletion
import kotlinx.coroutines.flow.take
import kotlinx.coroutines.flow.toList
import kotlinx.coroutines.runBlocking

// Anturi tuottaa lukemia, kunnes keräilijä lopettaa.
fun lukemat(anturi: String): Flow<Double> = flow {
    println("  $anturi käynnistyy")
    var arvo = 20.0
    while (true) {
        delay(10)
        emit(arvo)
        arvo += 0.75
    }
}

fun main() = runBlocking {
    val halytykset = lukemat("A1")
        .map { Math.round((it * 1.8 + 32) * 10) / 10.0 }   // °F
        .filter { it > 70.0 }
        .take(3)                               // peruu tuottajan
        .onCompletion { println("  virta päättyi") }
        .toList()
    println(halytykset)

    // Uusi keräys käynnistää tuottajan uudelleen.
    println(lukemat("A1").take(2).toList())
}
