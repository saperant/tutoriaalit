package fi.esimerkki.ostokset.lista

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import fi.esimerkki.ostokset.data.OstosRepository
import fi.esimerkki.ostokset.malli.Tuote
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

// @alku tila
/** Käyttäjälle näytettävä viesti. ViewModel kertoo, mitä tapahtui;
 *  käyttöliittymä päättää sanamuodon ja kielen. */
sealed interface Viesti {
    data class Lahetetty(val muutoksia: Int) : Viesti
    data object EiYhteytta : Viesti
}

/** Koko ruudun tila yhtenä muuttumattomana arvona. */
data class ListaUiState(
    val tuotteet: List<Tuote> = emptyList(),
    val uusiNimi: String = "",
    val synkronoidaan: Boolean = false,
    val viesti: Viesti? = null,
    val ladataan: Boolean = true,
) {
    val voiLisata: Boolean get() = uusiNimi.isNotBlank()
    val ostamatta: Int get() = tuotteet.count { !it.ostettu }
}
// @loppu tila

// @alku viewmodel
class ListaViewModel(
    private val repository: OstosRepository,
) : ViewModel() {
    /** Ruudun oma tila, joka ei tule tietokannasta. */
    private val paikallinen = MutableStateFlow(ListaUiState())

    val tila: StateFlow<ListaUiState> =
        combine(repository.tuotteet, paikallinen) { tuotteet, oma ->
            oma.copy(tuotteet = tuotteet, ladataan = false)
        }.stateIn(
            scope = viewModelScope,
            // Lopettaa keräämisen 5 s viimeisen tilaajan jälkeen, mutta
            // ei konfiguraatiomuutoksen ajaksi.
            started = SharingStarted.WhileSubscribed(5_000),
            initialValue = ListaUiState(),
        )

    fun nimiMuuttui(nimi: String) {
        paikallinen.update { it.copy(uusiNimi = nimi) }
    }

    fun lisaa() {
        val nimi = paikallinen.value.uusiNimi
        if (nimi.isBlank()) return
        paikallinen.update { it.copy(uusiNimi = "") }
        viewModelScope.launch { repository.lisaa(nimi, 1) }
    }

    fun merkitse(tuote: Tuote, ostettu: Boolean) {
        viewModelScope.launch { repository.merkitse(tuote.id, ostettu) }
    }

    fun synkronoi() {
        if (paikallinen.value.synkronoidaan) return
        paikallinen.update { it.copy(synkronoidaan = true) }
        viewModelScope.launch {
            val tulos = repository.synkronoi()
            paikallinen.update {
                it.copy(
                    synkronoidaan = false,
                    viesti = tulos.fold(
                        onSuccess = { n -> Viesti.Lahetetty(n) },
                        onFailure = { Viesti.EiYhteytta },
                    ),
                )
            }
        }
    }

    /** Käyttöliittymä kuittaa näyttämänsä viestin: tapahtuma on tilaa,
     *  joka poistetaan, kun se on käsitelty. */
    fun viestiNaytetty() {
        paikallinen.update { it.copy(viesti = null) }
    }
}
// @loppu viewmodel
