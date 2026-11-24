package fi.esimerkki.ostokset.ui

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

// @alku jarjestys
/** Sama teksti, sama reunus, eri järjestys. */
@Composable
fun ReunusNapautusalassa(onClick: () -> Unit) {
    Text("Lisää", Modifier.clickable(onClick = onClick).padding(16.dp)
        .size(40.dp))
}

@Composable
fun ReunusNapautusalanUlkona(onClick: () -> Unit) {
    Text("Lisää", Modifier.padding(16.dp).clickable(onClick = onClick)
        .size(40.dp))
}
// @loppu jarjestys
