// Uusi alatyyppi suljettuun hierarkiaan: kääntäjä löytää jokaisen
// when-lausekkeen, joka ei enää ole kattava.

sealed interface Tila {
    data object Luonnos : Tila
    data object Julkaistu : Tila
    data class Arkistoitu(val syy: String) : Tila
    data object Poistettu : Tila // @virhe
}

fun merkki(tila: Tila): String = when (tila) {
    Tila.Luonnos -> "L"
    Tila.Julkaistu -> "J"
    is Tila.Arkistoitu -> "A"
}

fun main() {
    println(listOf(Tila.Luonnos, Tila.Arkistoitu("vanha")).map(::merkki))
}
