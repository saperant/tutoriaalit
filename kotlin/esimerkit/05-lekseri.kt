// Laskulausekkeen lekseri: when, merkkivälit ja silmukat.

sealed interface Merkki {
    data class Luku(val arvo: Long) : Merkki {
        override fun toString() = "L$arvo"
    }
    data class Operaattori(val merkki: Char) : Merkki {
        override fun toString() = "O$merkki"
    }
    data object Vasen : Merkki
    data object Oikea : Merkki
}

class LeksausVirhe(viesti: String) : Exception(viesti)

fun leksaa(syote: String): List<Merkki> {
    val tulos = mutableListOf<Merkki>()
    var i = 0
    while (i < syote.length) {
        val c = syote[i]
        when {
            c.isWhitespace() -> i++
            c in '0'..'9' -> {
                val alku = i
                while (i < syote.length && syote[i].isDigit()) i++
                tulos += Merkki.Luku(syote.substring(alku, i).toLong())
            }
            else -> {
                tulos += when (c) {
                    '+', '-', '*', '/' -> Merkki.Operaattori(c)
                    '(' -> Merkki.Vasen
                    ')' -> Merkki.Oikea
                    else -> throw LeksausVirhe("odottamaton '$c' ($i)")
                }
                i++
            }
        }
    }
    return tulos
}

fun main() {
    System.setOut(java.io.PrintStream(System.out, true, Charsets.UTF_8))
    for (lauseke in listOf("12 + 3*(40 - 2)", "7 % 2")) {
        try {
            println(leksaa(lauseke).joinToString(" "))
        } catch (e: LeksausVirhe) {
            println("virhe: ${e.message}")
        }
    }
    // Välit: .. (suljettu), ..< (puoliavoin), downTo ja step.
    println((1..10 step 3).toList())
    println((0..<4).map { it * it })
    println((10 downTo 0 step 5).joinToString())

    // Nimetty break poistuu ulommasta silmukasta.
    ulompi@ for (rivi in 1..3) {
        for (sarake in 1..3) {
            if (rivi * sarake == 4) {
                println("ensimmäinen tulo 4: ($rivi, $sarake)")
                break@ulompi
            }
        }
    }
}
