// Paketti varasto: julkinen rajapinta ja moduulin sisäinen toteutus.
package varasto

import varasto.malli.Koodi
import varasto.malli.Tuote

/** Oton tulos. Suljettu tyyppi: `when` käsittelee kaikki tapaukset. */
sealed interface Otto {
    /** Otto onnistui, ja hyllyyn jäi [jaljella] kappaletta. */
    data class Ok(val jaljella: Int) : Otto

    /** Tuotetta oli vain [saatavilla] kappaletta; mitään ei otettu. */
    data class EiRiita(val saatavilla: Int) : Otto

    /** Koodilla ei ole tuotetta. */
    data object Tuntematon : Otto
}

/**
 * Tuotevarasto. Kutsuja ei näe tallennustapaa; toteutus luodaan
 * funktiolla [muistivarasto].
 */
interface Varasto {
    /**
     * Lisää tuotteen varastoon. Jos [Tuote.koodi] on jo varastossa,
     * kappalemäärät lasketaan yhteen.
     */
    fun lisaa(tuote: Tuote)

    /**
     * Ottaa varastosta tuotetta.
     *
     * @param koodi otettavan tuotteen koodi
     * @param maara otettava kappalemäärä
     * @return [Otto.Ok], jos määrä riitti, muuten [Otto.EiRiita] tai
     *   [Otto.Tuntematon]. Epäonnistunut otto ei muuta varastoa.
     */
    fun ota(koodi: Koodi, maara: Int): Otto

    /** Varaston tuotteet lisäysjärjestyksessä. */
    fun hyllyssa(): List<Tuote>
}

/** Luo tyhjän varaston, joka säilyttää tuotteet muistissa. */
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
