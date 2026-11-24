package fi.esimerkki.ostokset

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.navigation.compose.rememberNavController
import fi.esimerkki.ostokset.navigointi.OstosNavigaatio
import fi.esimerkki.ostokset.ui.OstoksetTeema

// @alku aktiviteetti
/** Ainoa Activity: Compose-sisältö ja navigointi tekevät loput. */
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        val sailio = (application as OstoksetSovellus).sailio
        setContent {
            OstoksetTeema {
                OstosNavigaatio(
                    navController = rememberNavController(),
                    luoListaViewModel = sailio::listaViewModel,
                )
            }
        }
    }
}
// @loppu aktiviteetti
