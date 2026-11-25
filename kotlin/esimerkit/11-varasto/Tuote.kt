// Paketti varasto.malli: tietotyypit ilman riippuvuuksia.
package varasto.malli

/**
 * Tuotekoodi muodossa `ABC-123`.
 *
 * @property arvo koodi merkkijonona
 * @throws IllegalArgumentException jos [arvo] ei ole oikeaa muotoa
 */
@JvmInline
value class Koodi(val arvo: String) {
    init {
        require(arvo.matches(Regex("[A-Z]{3}-\\d{3}"))) { "koodi: $arvo" }
    }
}

/**
 * Varastossa oleva tuote.
 *
 * @property koodi tuotteen yksilöivä koodi
 * @property nimi näytettävä nimi
 * @property hyllyssa kappalemäärä varastossa
 */
data class Tuote(val koodi: Koodi, val nimi: String, val hyllyssa: Int)
