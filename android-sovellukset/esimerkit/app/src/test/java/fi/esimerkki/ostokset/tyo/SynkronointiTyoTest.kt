package fi.esimerkki.ostokset.tyo

import android.content.Context
import androidx.test.core.app.ApplicationProvider
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.work.ListenableWorker
import androidx.work.ListenableWorker.Result
import androidx.work.WorkerFactory
import androidx.work.WorkerParameters
import androidx.work.testing.TestListenableWorkerBuilder
import fi.esimerkki.ostokset.testi.VaarennosRepository
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Test
import org.junit.runner.RunWith

// @alku testi
@RunWith(AndroidJUnit4::class)
class SynkronointiTyoTest {
    private val konteksti: Context =
        ApplicationProvider.getApplicationContext()

    /** Tehdas antaa työlle väärennetyn repositoryn. */
    private fun tyo(repo: VaarennosRepository, yritys: Int = 0) =
        TestListenableWorkerBuilder<SynkronointiTyo>(konteksti)
            .setRunAttemptCount(yritys)
            .setWorkerFactory(object : WorkerFactory() {
                override fun createWorker(
                    appContext: Context,
                    workerClassName: String,
                    workerParameters: WorkerParameters,
                ): ListenableWorker =
                    SynkronointiTyo(appContext, workerParameters, repo)
            })
            .build()

    @Test fun onnistuuKunVerkkoToimii() = runTest {
        assertEquals(Result.success(), tyo(VaarennosRepository()).doWork())
    }

    @Test fun yrittaaUudelleenJaLopultaLuovuttaa() = runTest {
        val repo = VaarennosRepository(verkkoToimii = false)
        assertEquals(Result.retry(), tyo(repo, yritys = 0).doWork())
        assertEquals(Result.failure(), tyo(repo, yritys = 5).doWork())
    }
}
// @loppu testi
