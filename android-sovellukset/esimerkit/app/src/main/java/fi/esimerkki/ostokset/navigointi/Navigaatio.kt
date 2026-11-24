package fi.esimerkki.ostokset.navigointi

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.toRoute
import fi.esimerkki.ostokset.lista.ListaRuutu
import fi.esimerkki.ostokset.lista.ListaViewModel
import kotlinx.serialization.Serializable

// @alku reitit
/** Reitit tyyppeinä: kääntäjä tarkistaa argumentit. */
@Serializable data object ListaReitti
@Serializable data class TuoteReitti(val id: Long, val nimi: String)
// @loppu reitit

// @alku navhost
@Composable
fun OstosNavigaatio(
    navController: NavHostController,
    luoListaViewModel: () -> ListaViewModel,
) {
    NavHost(navController, startDestination = ListaReitti) {
        composable<ListaReitti> {
            // ViewModel elää niin kauan kuin reitti on pinossa.
            val vm = viewModel { luoListaViewModel() }
            ListaRuutu(vm, onAvaa = { tuote ->
                navController.navigate(TuoteReitti(tuote.id, tuote.nimi))
            })
        }
        composable<TuoteReitti> { merkinta ->
            val reitti = merkinta.toRoute<TuoteReitti>()
            TuoteRuutu(reitti, onTakaisin = { navController.popBackStack() })
        }
    }
}
// @loppu navhost

@Composable
fun TuoteRuutu(reitti: TuoteReitti, onTakaisin: () -> Unit) {
    Column(Modifier.padding(16.dp)) {
        Text("Tuote ${reitti.nimi} (#${reitti.id})")
        Button(onClick = onTakaisin) { Text("Takaisin") }
    }
}
