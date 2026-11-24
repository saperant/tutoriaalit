package fi.esimerkki.ostokset

import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.LifecycleEventObserver
import androidx.lifecycle.ViewModel
import androidx.lifecycle.compose.LocalLifecycleOwner
import androidx.lifecycle.viewModelScope
import fi.esimerkki.ostokset.data.OstosRepository
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.flow.stateIn

// @alku nostettu
@Composable
fun Kentta(arvo: String, onArvo: (String) -> Unit,
           modifier: Modifier = Modifier) {
    OutlinedTextField(arvo, onArvo, modifier, label = { Text("Nimi") })
}

@Composable
fun KenttaTilalla() {
    var arvo by rememberSaveable { mutableStateOf("") }
    Kentta(arvo, onArvo = { arvo = it })
}
// @loppu nostettu

// @alku viewmodel
class MaaraViewModel(repository: OstosRepository) : ViewModel() {
    val ostamatta: StateFlow<Int> = repository.tuotteet
        .map { lista -> lista.count { !it.ostettu } }
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), 0)
}
// @loppu viewmodel

// @alku efekti
@Composable
fun KunNakyvissa(onNakyvissa: () -> Unit, onPiilossa: () -> Unit) {
    val omistaja = LocalLifecycleOwner.current
    DisposableEffect(omistaja) {
        val tarkkailija = LifecycleEventObserver { _, tapahtuma ->
            when (tapahtuma) {
                Lifecycle.Event.ON_START -> onNakyvissa()
                Lifecycle.Event.ON_STOP -> onPiilossa()
                else -> Unit
            }
        }
        omistaja.lifecycle.addObserver(tarkkailija)
        onDispose { omistaja.lifecycle.removeObserver(tarkkailija) }
    }
}
// @loppu efekti
