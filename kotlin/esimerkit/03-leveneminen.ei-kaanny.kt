// Kotlin ei levennä Intiä Longiksi automaattisesti edes silloin, kun
// muunnos olisi turvallinen. Muunnos kirjoitetaan näkyviin.

fun tiedostojenKoko(koot: List<Long>): Long = koot.sum()

fun main() {
    val liite: Int = 4096
    println(tiedostojenKoko(listOf(liite, 1024L))) // @virhe
    println(tiedostojenKoko(listOf(liite.toLong(), 1024L)))
}
