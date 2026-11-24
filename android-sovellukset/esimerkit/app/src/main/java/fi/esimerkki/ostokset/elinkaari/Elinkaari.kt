package fi.esimerkki.ostokset.elinkaari

import androidx.compose.foundation.layout.Column
import androidx.compose.material3.Button
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.lifecycle.DefaultLifecycleObserver
import androidx.lifecycle.LifecycleOwner

// @alku tarkkailija
/** Kirjaa elinkaaren siirtymät. Tarkkailija on erillinen olio, joten
 *  Activityn ei tarvitse ylikirjoittaa jokaista takaisinkutsua. */
class ElinkaariLoki(private val loki: MutableList<String>) :
    DefaultLifecycleObserver {
    override fun onCreate(owner: LifecycleOwner) { loki += "onCreate" }
    override fun onStart(owner: LifecycleOwner) { loki += "onStart" }
    override fun onResume(owner: LifecycleOwner) { loki += "onResume" }
    override fun onPause(owner: LifecycleOwner) { loki += "onPause" }
    override fun onStop(owner: LifecycleOwner) { loki += "onStop" }
    override fun onDestroy(owner: LifecycleOwner) { loki += "onDestroy" }
}
// @loppu tarkkailija

// @alku laskurit
/** Kaksi laskuria: remember katoaa, kun Activity luodaan uudelleen,
 *  rememberSaveable säilyy Bundlessa. */
@Composable
fun KaksiLaskuria() {
    var muisti by remember { mutableIntStateOf(0) }
    var tallessa by rememberSaveable { mutableIntStateOf(0) }
    Column {
        Text("remember: $muisti")
        Text("rememberSaveable: $tallessa")
        Button(onClick = { muisti++; tallessa++ }) { Text("Lisää") }
    }
}
// @loppu laskurit
