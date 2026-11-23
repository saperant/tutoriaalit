// require-ehdon rikkominen kaataa ohjelman, jos poikkeusta ei käsitellä:
// virheilmoitus kertoo, mikä sopimus rikkoutui ja missä.

fun alennus(hinta: Long, prosentti: Int): Long {
    require(prosentti in 0..100) {
        "alennusprosentti $prosentti ei ole 0..100"
    }
    return hinta * (100 - prosentti) / 100
}

fun main() {
    println(alennus(2_000, 15))
    println(alennus(2_000, 150))
}
