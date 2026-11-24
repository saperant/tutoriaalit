package fi.esimerkki.ostokset.tyo

import android.content.Context
import androidx.work.BackoffPolicy
import androidx.work.Constraints
import androidx.work.CoroutineWorker
import androidx.work.ExistingPeriodicWorkPolicy
import androidx.work.NetworkType
import androidx.work.PeriodicWorkRequestBuilder
import androidx.work.WorkManager
import androidx.work.WorkerParameters
import fi.esimerkki.ostokset.OstoksetSovellus
import fi.esimerkki.ostokset.data.OstosRepository
import java.util.concurrent.TimeUnit

// @alku tyo
/** Taustatyö, joka synkronoi listan. WorkManager ajaa sen, vaikka
 *  sovellus suljettaisiin tai laite käynnistettäisiin uudelleen. */
class SynkronointiTyo(
    konteksti: Context,
    parametrit: WorkerParameters,
    private val repository: OstosRepository,
) : CoroutineWorker(konteksti, parametrit) {

    /** WorkManager luo työn tällä muodostimella heijastuksen avulla. */
    constructor(konteksti: Context, parametrit: WorkerParameters) : this(
        konteksti, parametrit,
        (konteksti.applicationContext as OstoksetSovellus).sailio.repository,
    )

    override suspend fun doWork(): Result =
        repository.synkronoi().fold(
            onSuccess = { Result.success() },
            // Uusi yritys myöhemmin, eksponentiaalisesti harvenevin välein.
            onFailure = {
                if (runAttemptCount < 5) Result.retry() else Result.failure()
            },
        )

    companion object {
        const val NIMI = "synkronointi"
    }
}
// @loppu tyo

// @alku ajastus
/** Ajastaa synkronoinnin kerran tunnissa, kun verkko on käytettävissä
 *  eikä akku ole vähissä. Ainutkertainen nimi estää päällekkäiset
 *  ajastukset. */
fun ajastaSynkronointi(workManager: WorkManager) {
    val ehdot = Constraints.Builder()
        .setRequiredNetworkType(NetworkType.CONNECTED)
        .setRequiresBatteryNotLow(true)
        .build()
    val pyynto = PeriodicWorkRequestBuilder<SynkronointiTyo>(
        repeatInterval = 1, repeatIntervalTimeUnit = TimeUnit.HOURS,
    )
        .setConstraints(ehdot)
        .setBackoffCriteria(BackoffPolicy.EXPONENTIAL, 30, TimeUnit.SECONDS)
        .build()
    workManager.enqueueUniquePeriodicWork(
        SynkronointiTyo.NIMI,
        ExistingPeriodicWorkPolicy.KEEP,
        pyynto,
    )
}
// @loppu ajastus
