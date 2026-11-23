// JVM:n rinnakkaisuus Kotlinista: virtuaalisäikeet (JDK 21),
// säieturvalliset rakenteet ja lukot inline-apufunktioilla.

import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.Executors
import java.util.concurrent.atomic.AtomicLong
import java.util.concurrent.locks.ReentrantLock
import kotlin.concurrent.thread
import kotlin.concurrent.withLock

class Tilasto {
    private val lukko = ReentrantLock()
    private var pisin = 0

    fun havainto(pituus: Int) = lukko.withLock {   // inline: ei lambdaa
        if (pituus > pisin) pisin = pituus
    }

    fun pisin() = lukko.withLock { pisin }
}

fun main() {
    System.setOut(java.io.PrintStream(System.out, true, Charsets.UTF_8))
    val sanat = "kotlin on tiivis kieli ja kotlin toimii jvm:ssä"
        .split(" ")
    val esiintymat = ConcurrentHashMap<String, Int>()
    val merkkeja = AtomicLong()
    val tilasto = Tilasto()

    // Virtuaalisäie per tehtävä; use sulkee ja odottaa kaikki.
    Executors.newVirtualThreadPerTaskExecutor().use { suorittaja ->
        repeat(1_000) { i ->
            suorittaja.submit {
                val sana = sanat[i % sanat.size]
                esiintymat.merge(sana, 1, Int::plus)
                merkkeja.addAndGet(sana.length.toLong())
                tilasto.havainto(sana.length)
            }
        }
    }
    println(esiintymat.toSortedMap())
    println("merkkejä ${merkkeja.get()}, pisin ${tilasto.pisin()}")

    // thread { } luo ja käynnistää alustasäikeen; join odottaa.
    val tulokset = IntArray(4)
    val saikeet = (0..3).map { n ->
        thread(name = "laskija-$n") { tulokset[n] = (1..n * 1000).sum() }
    }
    saikeet.forEach { it.join() }
    println(tulokset.toList())
}
