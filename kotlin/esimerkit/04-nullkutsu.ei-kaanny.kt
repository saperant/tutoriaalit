// Nullable-tyypin jäseniin ei pääse ilman tarkistusta.

fun lyhenne(nimi: String?): String {
    return nimi.take(3) // @virhe
    return nimi?.take(3) ?: "???"
}

fun main() {
    println(lyhenne("Kotlin"))
    println(lyhenne(null))
}
