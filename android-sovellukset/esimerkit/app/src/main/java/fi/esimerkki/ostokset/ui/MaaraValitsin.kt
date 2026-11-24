package fi.esimerkki.ostokset.ui

import androidx.compose.foundation.layout.Row
import androidx.compose.material3.IconButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.semantics.stateDescription

// @alku tilaton
/** Tilaton komponentti: arvo tulee sisään, muutokset lähtevät ulos. */
@Composable
fun MaaraValitsin(
    maara: Int,
    onMuutos: (Int) -> Unit,
    modifier: Modifier = Modifier,
    rajat: IntRange = 1..99,
) {
    Row(
        modifier = modifier.semantics(mergeDescendants = true) {
            stateDescription = "$maara kpl"
        },
        verticalAlignment = Alignment.CenterVertically,
    ) {
        IconButton(
            onClick = { onMuutos(maara - 1) },
            enabled = maara > rajat.first,
            modifier = Modifier.semantics {
                contentDescription = "Vähennä"
            },
        ) { Text("−") }
        Text("$maara")
        IconButton(
            onClick = { onMuutos(maara + 1) },
            enabled = maara < rajat.last,
            modifier = Modifier.semantics {
                contentDescription = "Lisää"
            },
        ) { Text("+") }
    }
}
// @loppu tilaton

// @alku tilallinen
/** Tilallinen kääre esimerkkiä varten: tila säilyy myös
 *  konfiguraatiomuutoksessa ja prosessin kuolemassa. */
@Composable
fun MaaraValitsinTilalla(alku: Int = 1) {
    var maara by rememberSaveable { mutableIntStateOf(alku) }
    MaaraValitsin(maara = maara, onMuutos = { maara = it })
}
// @loppu tilallinen
