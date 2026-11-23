// Javan metodin paluutyyppi on Kotlinille alustatyyppi (String!):
// kääntäjä ei tiedä, voiko se olla null. Ilmoitettu ei-null-tyyppi
// siirtää tarkistuksen ajonaikaiseksi.

fun main() {
    // System.getProperty palauttaa null, jos ominaisuutta ei ole.
    val hakemisto: String = System.getProperty("sovellus.hakemisto")
    println("hakemisto: $hakemisto")
}
