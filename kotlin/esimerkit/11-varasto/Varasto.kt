// Paketti varasto: julkinen rajapinta ja moduulin sisäinen toteutus.
package varasto

import varasto.malli.Koodi
import varasto.malli.Tuote

sealed interface Otto {
    data class Ok(val jaljella: Int) : Otto
    data class EiRiita(val saatavilla: Int) : Otto
    data object Tuntematon : Otto
}

// Julkinen rajapinta: kutsuja ei näe tallennustapaa.
interface Varasto {
    fun lisaa(tuote: Tuote)
    fun ota(koodi: Koodi, maara: Int): Otto
    fun hyllyssa(): List<Tuote>
}

// Tehdasfunktio paketin tasolla: ei luokkaa staattisille metodeille.
fun muistivarasto(): Varasto = Muistivarasto()

// internal: näkyy vain saman moduulin (käännösyksikön) koodille.
internal class Muistivarasto : Varasto {
    private val tuotteet = linkedMapOf<Koodi, Tuote>()

    override fun lisaa(tuote: Tuote) {
        val vanha = tuotteet[tuote.koodi]
        tuotteet[tuote.koodi] = vanha?.copy(
            hyllyssa = vanha.hyllyssa + tuote.hyllyssa,
        ) ?: tuote
    }

    override fun ota(koodi: Koodi, maara: Int): Otto {
        val tuote = tuotteet[koodi] ?: return Otto.Tuntematon
        if (tuote.hyllyssa < maara) return Otto.EiRiita(tuote.hyllyssa)
        tuotteet[koodi] = tuote.copy(hyllyssa = tuote.hyllyssa - maara)
        return Otto.Ok(tuote.hyllyssa - maara)
    }

    override fun hyllyssa() = tuotteet.values.toList()
}
