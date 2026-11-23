// Merkkijonojen käsittely: jäsennys, normalisointi ja kokoaminen.

fun normalisoiPuhelin(numero: String): String? {
    val numerot = numero.filter { it.isDigit() || it == '+' }
    return when {
        numerot.startsWith("+358") -> numerot
        numerot.startsWith("0") -> "+358" + numerot.drop(1)
        else -> null
    }?.takeIf { it.length in 10..13 }
}

fun main() {
    val rivi = "  Nimi: Virtanen, Aino ; Puh: 040-123 4567  "
    val kentat = rivi.trim()
        .split(';')
        .associate { kentta ->
            kentta.substringBefore(':').trim() to
                kentta.substringAfter(':').trim()
        }
    println(kentat)
    val (suku, etu) = kentat.getValue("Nimi").split(", ")
    println("$etu $suku")
    println(normalisoiPuhelin(kentat.getValue("Puh")))
    println(normalisoiPuhelin("12"))

    // buildString kokoaa ilman välimerkkijonoja (StringBuilder).
    val taulukko = buildString {
        appendLine("| tuote | kpl |")
        for ((tuote, kpl) in listOf("kahvi" to 3, "tee" to 12)) {
            append("| ").append(tuote.padEnd(5)).append(" | ")
            appendLine(kpl.toString().padStart(3) + " |")
        }
    }
    print(taulukko)

    // Merkkijonot ovat muuttumattomia; vertailu == vertaa sisältöä.
    val a = "kot" + "lin"
    println(a == "kotlin")
    println("Äiti".equals("äiti", ignoreCase = true))
    println("ö".compareTo("z") > 0)   // Unicode-järjestys, ei suomen
}
