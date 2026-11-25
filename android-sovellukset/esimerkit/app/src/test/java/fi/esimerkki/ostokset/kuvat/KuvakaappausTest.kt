package fi.esimerkki.ostokset.kuvat

import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.Surface
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.test.junit4.v2.createComposeRule
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.onRoot
import androidx.test.ext.junit.runners.AndroidJUnit4
import com.github.takahirom.roborazzi.captureRoboImage
import fi.esimerkki.ostokset.lista.ListaSisalto
import fi.esimerkki.ostokset.lista.ListaUiState
import fi.esimerkki.ostokset.lista.Viesti
import fi.esimerkki.ostokset.malli.Tuote
import fi.esimerkki.ostokset.navigointi.TuoteReitti
import fi.esimerkki.ostokset.navigointi.TuoteRuutu
import fi.esimerkki.ostokset.ui.MaaraValitsinTilalla
import fi.esimerkki.ostokset.ui.OstoksetTeema
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.annotation.Config
import org.robolectric.annotation.GraphicsMode

// @alku kuvat
/** Tämän tutoriaalin kuvat sovelluksesta: Robolectric piirtää ruudun
 *  JVM:llä oikealla grafiikkakirjastolla, Roborazzi tallentaa sen. */
@RunWith(AndroidJUnit4::class)
@GraphicsMode(GraphicsMode.Mode.NATIVE)
@Config(qualifiers = "w360dp-h640dp-xhdpi")     // pieni puhelin
class KuvakaappausTest {
    @get:Rule val compose = createComposeRule()

    private val tila = ListaUiState(
        tuotteet = listOf(
            Tuote(1, "maito", 2), Tuote(2, "leipä"),
            Tuote(3, "kahvi", ostettu = true),
        ),
        ladataan = false,
    )

    @Test fun listaVaaleanaJaTummana() {
        var tumma by mutableStateOf(false)
        compose.setContent { OstoksetTeema(tumma) { Lista(tila) } }
        compose.onRoot().captureRoboImage("build/kuvat/lista.png")
        tumma = true
        compose.onRoot().captureRoboImage("build/kuvat/lista-tumma.png")
    }

    @Test fun viesti() {
        compose.setContent {
            OstoksetTeema(tumma = false) {
                Lista(tila.copy(viesti = Viesti.Lahetetty(2)))
            }
        }
        compose.onNodeWithText("Lähetetty 2 muutosta").assertExists()
        compose.onRoot().captureRoboImage("build/kuvat/lista-viesti.png")
    }
    // @loppu kuvat

    @Test fun tuoteruutu() {
        compose.setContent {
            OstoksetTeema(tumma = false) {
                Surface(Modifier.fillMaxSize()) {
                    TuoteRuutu(TuoteReitti(1, "maito"), onTakaisin = {})
                }
            }
        }
        compose.onRoot().captureRoboImage("build/kuvat/tuote.png")
    }

    @Test fun maaravalitsin() {
        compose.setContent {
            OstoksetTeema(tumma = false) {
                Surface { MaaraValitsinTilalla(alku = 3) }
            }
        }
        compose.onRoot().captureRoboImage("build/kuvat/maaravalitsin.png")
    }

    @Composable
    private fun Lista(tila: ListaUiState) {
        Surface {
            ListaSisalto(tila, {}, {}, { _, _ -> }, {}, {}, {})
        }
    }
}
