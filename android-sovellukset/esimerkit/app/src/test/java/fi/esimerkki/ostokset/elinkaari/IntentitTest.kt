package fi.esimerkki.ostokset.elinkaari

import android.content.Context
import android.content.Intent
import androidx.activity.ComponentActivity
import androidx.test.core.app.ActivityScenario
import androidx.test.core.app.ApplicationProvider
import androidx.test.ext.junit.runners.AndroidJUnit4
import fi.esimerkki.ostokset.MainActivity
import fi.esimerkki.ostokset.malli.Tuote
import org.junit.Assert.assertEquals
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.Shadows.shadowOf

@RunWith(AndroidJUnit4::class)
class IntentitTest {
    // @alku jako
    @Test fun jakaminenKaynnistaaValitsimen() {
        val lista = listOf(
            Tuote(1, "maito", 2), Tuote(2, "kahvi", ostettu = true),
        )
        ActivityScenario.launch(ComponentActivity::class.java).use { s ->
            s.onActivity { activity ->
                activity.startActivity(jakoIntent(lista))

                // Robolectric tallentaa käynnistyksen sen sijaan, että
                // avaisi toisen sovelluksen.
                val valitsin = shadowOf(activity).nextStartedActivity
                assertEquals(Intent.ACTION_CHOOSER, valitsin.action)
                @Suppress("DEPRECATION")   // tyypitetty haku vasta API 33:ssa
                val laheta: Intent =
                    valitsin.getParcelableExtra(Intent.EXTRA_INTENT)!!
                assertEquals(Intent.ACTION_SEND, laheta.action)
                assertEquals("text/plain", laheta.type)
                assertEquals("maito × 2",
                             laheta.getStringExtra(Intent.EXTRA_TEXT))
            }
        }
    }
    // @loppu jako

    // @alku vastaanotto
    @Test fun jaettuTekstiJasennetaanJaRajataan() {
        val jaettu = Intent(Intent.ACTION_SEND).apply {
            type = "text/plain"
            putExtra(Intent.EXTRA_TEXT,
                     "maito\n\n  leipä  \n" + "x".repeat(500))
        }
        assertEquals(
            listOf("maito", "leipä", "x".repeat(100)),
            jaetutNimet(jaettu),
        )
        // Väärä toiminto tai tyyppi: ei tulkita lainkaan.
        val katselu = Intent(Intent.ACTION_VIEW)
        assertEquals(emptyList<String>(), jaetutNimet(katselu))
        val kuva = Intent(Intent.ACTION_SEND).apply { type = "image/png" }
        assertEquals(emptyList<String>(), jaetutNimet(kuva))
    }
    // @loppu vastaanotto

    // @alku eksplisiittinen
    @Test fun eksplisiittinenIntentNimeaaKomponentin() {
        val konteksti = ApplicationProvider.getApplicationContext<Context>()
        val intent = Intent(konteksti, MainActivity::class.java)
        assertEquals(MainActivity::class.java.name,
                     intent.component?.className)
    }
    // @loppu eksplisiittinen
}
