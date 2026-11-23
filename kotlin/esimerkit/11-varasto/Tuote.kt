// Paketti varasto.malli: tietotyypit ilman riippuvuuksia.
package varasto.malli

@JvmInline
value class Koodi(val arvo: String) {
    init {
        require(arvo.matches(Regex("[A-Z]{3}-\\d{3}"))) { "koodi: $arvo" }
    }
}

data class Tuote(val koodi: Koodi, val nimi: String, val hyllyssa: Int)
