// Geneerisyys: varianssi esittelypaikassa (out/in), rajoitteet ja
// tyyppiturvallinen tapahtumaväylä.

// out: Tuottaja<Kissa> on Tuottaja<Elain> (kovarianssi).
interface Lahde<out T> {
    fun seuraava(): T?
}

// in: Kasittelija<Elain> kelpaa Kasittelija<Kissa>:ksi (kontravarianssi).
fun interface Kasittelija<in T> {
    fun kasittele(arvo: T)
}

open class Tapahtuma(val nimi: String)
class Kirjautuminen(val kayttaja: String) : Tapahtuma("kirjautuminen")
class Maksu(val sentit: Long) : Tapahtuma("maksu")

class Jono<T>(vararg alkiot: T) : Lahde<T> {
    private val jono = ArrayDeque(alkiot.toList())
    override fun seuraava(): T? = jono.removeFirstOrNull()
}

// Kuluttaa minkä tahansa T:n lähteen ja ohjaa yhteiselle käsittelijälle.
fun <T> tyhjenna(lahde: Lahde<T>, kasittelija: Kasittelija<T>) {
    while (true) kasittelija.kasittele(lahde.seuraava() ?: return)
}

// Ylärajoite: T:n on oltava vertailtava.
fun <T : Comparable<T>> suurin(a: T, b: T): T = if (a >= b) a else b

fun main() {
    val kirjaaja = Kasittelija<Tapahtuma> { println("loki: ${it.nimi}") }
    val maksut = Jono(Maksu(1_200), Maksu(80))
    // Kasittelija<Tapahtuma> kelpaa Kasittelija<Maksu>:n paikalle.
    tyhjenna(maksut, kirjaaja)

    // Lahde<Kirjautuminen> kelpaa Lahde<Tapahtuma>:n paikalle.
    val lahde: Lahde<Tapahtuma> = Jono(Kirjautuminen("aino"))
    println(lahde.seuraava()?.nimi)

    println(suurin("kotlin", "java"))
    println(suurin(3.5, 2.0))

    // List<out E> on kovariantti, MutableList<E> invariantti.
    val luvut: List<Number> = listOf(1, 2.5)
    println(luvut.sumOf { it.toDouble() })
}
