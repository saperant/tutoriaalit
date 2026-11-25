package fi.esimerkki.ostokset.elinkaari

import android.content.Intent
import fi.esimerkki.ostokset.malli.Tuote

// @alku jako
/** Implisiittinen intent: kohdetta ei nimetä. Järjestelmä etsii
 *  sovellukset, jotka ottavat vastaan tekstiä, ja näyttää valitsimen. */
fun jakoIntent(tuotteet: List<Tuote>): Intent {
    val laheta = Intent(Intent.ACTION_SEND).apply {
        type = "text/plain"
        putExtra(
            Intent.EXTRA_TEXT,
            tuotteet.filterNot { it.ostettu }
                .joinToString("\n") { "${it.nimi} × ${it.maara}" },
        )
    }
    return Intent.createChooser(laheta, "Jaa ostoslista")
}
// @loppu jako

// @alku vastaanotto
/** Toisen sovelluksen jakama teksti tuotenimiksi, rivi kerrallaan.
 *  Intentin sisältö tulee sovelluksen ulkopuolelta, joten se
 *  tarkistetaan ja rajataan kuten mikä tahansa syöte. */
fun jaetutNimet(intent: Intent): List<String> {
    if (intent.action != Intent.ACTION_SEND) return emptyList()
    if (intent.type != "text/plain") return emptyList()
    return intent.getStringExtra(Intent.EXTRA_TEXT).orEmpty()
        .lineSequence()
        .map { it.trim().take(NIMEN_ENIMMAISPITUUS) }
        .filter { it.isNotEmpty() }
        .take(RIVEJA_ENINTAAN)
        .toList()
}

private const val NIMEN_ENIMMAISPITUUS = 100
private const val RIVEJA_ENINTAAN = 50
// @loppu vastaanotto
