// MutableList on invariantti: muuten Double voitaisiin lisätä
// Int-listaan. Vain luku -List on kovariantti ja siksi turvallinen.

fun lisaaPuolikas(luvut: MutableList<Number>) {
    luvut += 0.5
}

fun summa(luvut: List<Number>) = luvut.sumOf { it.toDouble() }

fun main() {
    val kokonaisluvut = mutableListOf(1, 2, 3)
    lisaaPuolikas(kokonaisluvut) // @virhe
    println(summa(kokonaisluvut))
}
