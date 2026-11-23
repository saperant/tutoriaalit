// Yksikkötestit kotlin.test-väitteillä. Oikeassa projektissa
// testifunktiot merkitään @Test-annotaatiolla ja Gradle ajaa ne
// JUnit 5:llä; tässä pieni ajuri ajaa saman listan ilman Gradlea.
package hinnoittelu

import kotlin.test.assertEquals
import kotlin.test.assertFailsWith
import kotlin.test.assertTrue

private val kori = listOf(Rivi("kahvi", 650, 2), Rivi("pulla", 220, 3))

val testit: List<Pair<String, () -> Unit>> = listOf(
    "välisumma kertoo määrällä" to {
        assertEquals(1_960, valisumma(kori))
    },
    "ilman alennusta hinta on välisumma" to {
        assertEquals(valisumma(kori), yhteensa(kori))
    },
    "prosenttialennus pyöristää alaspäin" to {
        assertEquals(1_666, yhteensa(kori, Alennus.Prosentti(15)))
    },
    "kynnysalennus vain rajan ylittyessä" to {
        val alennus = Alennus.Kynnys(raja = 2_000, vahennys = 300)
        assertEquals(1_960, yhteensa(kori, alennus))
        assertEquals(1_880, yhteensa(kori + Rivi("tee", 220, 1), alennus))
    },
    "tyhjä kori maksaa nolla" to {
        assertEquals(0, yhteensa(emptyList(), Alennus.Prosentti(50)))
    },
    "virheelliset arvot hylätään" to {
        val virhe = assertFailsWith<IllegalArgumentException> {
            Rivi("kahvi", 650, 0)
        }
        assertTrue("määrä" in virhe.message.orEmpty())
        assertFailsWith<IllegalArgumentException> { Alennus.Prosentti(101) }
    },
)

fun main() {
    var epaonnistui = 0
    for ((nimi, testi) in testit) {
        val tulos = runCatching(testi)
        if (tulos.isFailure) epaonnistui++
        val tila = if (tulos.isSuccess) "ok" else "EPÄONNISTUI"
        println("$tila  $nimi")
        tulos.exceptionOrNull()?.let { println("      ${it.message}") }
    }
    println("${testit.size - epaonnistui}/${testit.size} testiä läpi")
    if (epaonnistui > 0) kotlin.system.exitProcess(1)
}
