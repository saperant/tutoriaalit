// Kokoelman muuttaminen sitä läpikäydessä: Javan tapaan
// ConcurrentModificationException. Oikein: removeAll { ... } tai
// filter uudeksi listaksi.

fun main() {
    val tehtavat = mutableListOf("valmis: A", "kesken: B", "valmis: C")
    for (t in tehtavat) {
        if (t.startsWith("valmis")) tehtavat.remove(t)
    }
    println(tehtavat)
}
