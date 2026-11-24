package fi.esimerkki.ostokset

import android.app.Application
import androidx.work.WorkManager
import fi.esimerkki.ostokset.tyo.ajastaSynkronointi

// @alku sovellus
/** Application-olio elää koko prosessin ajan, joten se omistaa
 *  sovelluksenlaajuiset riippuvuudet. */
class OstoksetSovellus : Application() {
    val sailio: Sailio by lazy { Sailio(this) }

    override fun onCreate() {
        super.onCreate()
        ajastaSynkronointi(WorkManager.getInstance(this))
    }
}
// @loppu sovellus
