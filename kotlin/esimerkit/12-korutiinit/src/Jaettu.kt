// Jaettu muuttuva tila ja kanavat. Korutiinit ajetaan usean säikeen
// altaassa (Dispatchers.Default), joten suojaamaton muuttuja menettäisi
// päivityksiä samalla tavalla kuin säikeillä.

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.launch
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import kotlinx.coroutines.withContext
import java.util.concurrent.atomic.AtomicInteger

// Tuhat korutiinia, joista jokainen tekee askeleen sata kertaa.
suspend fun rinnakkain(askel: suspend () -> Unit) =
    withContext(Dispatchers.Default) {
        repeat(1_000) { launch { repeat(100) { askel() } } }
    }

suspend fun laskurit() {
    // 1. Atominen arvo: yksi muuttuja, ei lukkoa.
    val atominen = AtomicInteger()
    rinnakkain { atominen.incrementAndGet() }

    // 2. Mutex: odottava korutiini keskeytyy eikä varaa säiettä.
    val lukko = Mutex()
    var lukittu = 0
    rinnakkain { lukko.withLock { lukittu++ } }

    println("atominen $atominen, lukittu $lukittu")
}

// Kanava: tuottaja lähettää, kaksi kuluttajaa jakaa työt. Rajattu
// puskuri antaa vastapainetta: send keskeytyy, kun puskuri on täynnä.
suspend fun tyojono() = coroutineScope {
    val tilaukset = Channel<Int>(capacity = 2)
    val tulokset = Channel<Pair<String, Int>>(Channel.UNLIMITED)

    launch {
        for (numero in 1..6) tilaukset.send(numero)
        tilaukset.close()               // kuluttajien silmukat päättyvät
    }
    val kuluttajat = listOf("A", "B").map { nimi ->
        launch {
            for (numero in tilaukset) tulokset.send(nimi to numero * 10)
        }
    }
    kuluttajat.forEach { it.join() }
    tulokset.close()

    var kasitelty = 0
    var summa = 0
    for ((_, arvo) in tulokset) {
        kasitelty++
        summa += arvo
    }
    println("käsitelty $kasitelty tilausta, summa $summa")
}

fun main() = runBlocking {
    System.setOut(java.io.PrintStream(System.out, true, Charsets.UTF_8))
    laskurit()
    tyojono()
}
