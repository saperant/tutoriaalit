package fi.esimerkki.ostokset.ui

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Checkbox
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.semantics.stateDescription
import androidx.compose.ui.text.style.TextDecoration
import androidx.compose.ui.unit.dp
import fi.esimerkki.ostokset.malli.Tuote

// @alku rivi
@Composable
fun TuoteRivi(
    tuote: Tuote,
    onOstettu: (Boolean) -> Unit,
    onAvaa: () -> Unit,
    modifier: Modifier = Modifier,
) {
    Row(
        modifier = modifier
            .fillMaxWidth()
            .clickable(onClickLabel = "Avaa tuote", onClick = onAvaa)
            .padding(horizontal = 16.dp, vertical = 8.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        Checkbox(
            checked = tuote.ostettu,
            onCheckedChange = onOstettu,
            modifier = Modifier.semantics {
                stateDescription =
                    if (tuote.ostettu) "ostettu" else "ostamatta"
            },
        )
        Text(
            text = "${tuote.nimi} × ${tuote.maara}",
            style = MaterialTheme.typography.bodyLarge,
            textDecoration =
                if (tuote.ostettu) TextDecoration.LineThrough else null,
        )
    }
}
// @loppu rivi

// @alku lista
@Composable
fun TuoteLista(
    tuotteet: List<Tuote>,
    onOstettu: (Tuote, Boolean) -> Unit,
    onAvaa: (Tuote) -> Unit,
    modifier: Modifier = Modifier,
) {
    LazyColumn(modifier = modifier) {
        items(tuotteet, key = { it.id }, contentType = { "tuote" }) {
            TuoteRivi(
                tuote = it,
                onOstettu = { ostettu -> onOstettu(it, ostettu) },
                onAvaa = { onAvaa(it) },
                modifier = Modifier.animateItem(),
            )
        }
    }
}
// @loppu lista

