package fi.esimerkki.ostokset.ui

import androidx.compose.foundation.layout.Column
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.SideEffect
import androidx.compose.runtime.remember
import fi.esimerkki.ostokset.malli.Tuote

// @alku tyypit
/** Epävakaa: var-ominaisuus voi muuttua Composen huomaamatta, joten
 *  Compose vertaa olioita vain identiteetin (===) perusteella. */
class Rajaus(var vainOstamattomat: Boolean)

/** Laskee, montako kertaa komponentti koostettiin. */
@Composable
fun Yhteenveto(
    tuotteet: List<Tuote>,
    rajaus: Rajaus,
    onKoostettu: () -> Unit,
) {
    SideEffect { onKoostettu() }
    val n = tuotteet.count { !rajaus.vainOstamattomat || !it.ostettu }
    Text("Näytetään $n")
}
// @loppu tyypit

// @alku huono
@Composable
fun NakymaHuono(tuotteet: List<Tuote>, otsikko: String,
                onKoostettu: () -> Unit) {
    Column {
        Text(otsikko)
        // Uusi epävakaa olio joka koostamisella: lasta ei voi ohittaa.
        Yhteenveto(tuotteet, Rajaus(true), onKoostettu)
    }
}
// @loppu huono

// @alku hyva
@Composable
fun NakymaHyva(tuotteet: List<Tuote>, otsikko: String,
               onKoostettu: () -> Unit) {
    val rajaus = remember { Rajaus(true) }   // sama olio joka kerta
    Column {
        Text(otsikko)
        Yhteenveto(tuotteet, rajaus, onKoostettu)
    }
}
// @loppu hyva

// @alku vakaa
@Composable
fun NakymaVakaa(tuotteet: List<Tuote>, otsikko: String,
                onKoostettu: () -> Unit) {
    val rajaus = remember { Rajaus(false) }
    Column {
        Text(otsikko)
        // Uusi lista joka kerta, mutta List<Tuote> on vakaa tyyppi:
        // Compose vertaa sisältöä equalsilla ja ohittaa lapsen.
        Yhteenveto(tuotteet.filter { !it.ostettu }, rajaus, onKoostettu)
    }
}
// @loppu vakaa
