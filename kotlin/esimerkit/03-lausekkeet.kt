// if, when ja try lausekkeina: HTTP-vastauksen luokittelu.

fun luokka(koodi: Int): String = when (koodi) {
    in 200..299 -> "onnistui"
    301, 302, 307, 308 -> "uudelleenohjaus"
    in 400..499 -> "asiakkaan virhe"
    in 500..599 -> "palvelimen virhe"
    else -> "tuntematon"
}

fun main() {
    for (rivi in listOf("200", "302", "404", "503", "abc", "99")) {
        // try lausekkeena; syötteelle toIntOrNull() olisi tiiviimpi.
        val koodi = try {
            rivi.toInt()
        } catch (e: NumberFormatException) {
            -1
        }
        val teksti = if (koodi < 0) "ei koodi: $rivi" else luokka(koodi)
        println("${rivi.padEnd(4)} $teksti")
    }
}
