package fi.esimerkki.ostokset.lista

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.pluralStringResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import fi.esimerkki.ostokset.R
import fi.esimerkki.ostokset.malli.Tuote
import fi.esimerkki.ostokset.ui.TuoteLista

// @alku tilallinen
/** Tilallinen ruutu: kytkee ViewModelin tilaan ja tapahtumiin. */
@Composable
fun ListaRuutu(
    viewModel: ListaViewModel,
    onAvaa: (Tuote) -> Unit,
) {
    // Kerää vain, kun ruutu on vähintään STARTED-tilassa.
    val tila by viewModel.tila.collectAsStateWithLifecycle()
    ListaSisalto(
        tila = tila,
        onNimi = viewModel::nimiMuuttui,
        onLisaa = viewModel::lisaa,
        onOstettu = viewModel::merkitse,
        onAvaa = onAvaa,
        onSynkronoi = viewModel::synkronoi,
        onViestiNaytetty = viewModel::viestiNaytetty,
    )
}
// @loppu tilallinen

// @alku tilaton
/** Tilaton sisältö: helppo esikatsella ja testata ilman ViewModelia. */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ListaSisalto(
    tila: ListaUiState,
    onNimi: (String) -> Unit,
    onLisaa: () -> Unit,
    onOstettu: (Tuote, Boolean) -> Unit,
    onAvaa: (Tuote) -> Unit,
    onSynkronoi: () -> Unit,
    onViestiNaytetty: () -> Unit,
) {
    val snackbar = remember { SnackbarHostState() }
    val viesti = tila.viesti?.let { teksti(it) }
    // Sivuvaikutus: näytä viesti kerran ja kuittaa se.
    LaunchedEffect(viesti) {
        if (viesti == null) return@LaunchedEffect
        snackbar.showSnackbar(viesti)
        onViestiNaytetty()
    }
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Ostokset (${tila.ostamatta})") },
                actions = {
                    TextButton(
                        onClick = onSynkronoi,
                        enabled = !tila.synkronoidaan,
                    ) { Text("Synkronoi") }
                },
            )
        },
        snackbarHost = { SnackbarHost(snackbar) },
    ) { reunat ->
        Column(Modifier.padding(reunat).fillMaxSize()) {
            Row(
                Modifier.padding(16.dp),
                horizontalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                OutlinedTextField(
                    value = tila.uusiNimi,
                    onValueChange = onNimi,
                    label = { Text("Uusi tuote") },
                    singleLine = true,
                    keyboardOptions =
                        KeyboardOptions(imeAction = ImeAction.Done),
                    keyboardActions = KeyboardActions(onDone = { onLisaa() }),
                    modifier = Modifier.weight(1f),
                )
                Button(onClick = onLisaa, enabled = tila.voiLisata) {
                    Text("Lisää")
                }
            }
            if (tila.ladataan) {
                CircularProgressIndicator(Modifier.padding(16.dp))
            } else {
                TuoteLista(tila.tuotteet, onOstettu, onAvaa)
            }
        }
    }
}
// @loppu tilaton

// @alku teksti
/** Viestin sanamuoto resursseista: teksti voidaan kääntää, ja
 *  monikkomuoto valitaan kielen sääntöjen mukaan. */
@Composable
fun teksti(viesti: Viesti): String = when (viesti) {
    is Viesti.Lahetetty -> pluralStringResource(
        R.plurals.lahetetty_muutoksia, viesti.muutoksia, viesti.muutoksia,
    )
    Viesti.EiYhteytta -> stringResource(R.string.ei_yhteytta)
}
// @loppu teksti
