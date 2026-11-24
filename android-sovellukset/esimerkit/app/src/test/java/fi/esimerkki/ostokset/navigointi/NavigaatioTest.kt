package fi.esimerkki.ostokset.navigointi

import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.test.junit4.v2.createComposeRule
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.performClick
import androidx.navigation.NavDestination.Companion.hasRoute
import androidx.navigation.compose.ComposeNavigator
import androidx.navigation.testing.TestNavHostController
import androidx.navigation.toRoute
import androidx.test.ext.junit.runners.AndroidJUnit4
import fi.esimerkki.ostokset.lista.ListaViewModel
import fi.esimerkki.ostokset.malli.Tuote
import fi.esimerkki.ostokset.testi.VaarennosRepository
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

// @alku testi
@RunWith(AndroidJUnit4::class)
class NavigaatioTest {
    @get:Rule val compose = createComposeRule()
    private lateinit var nav: TestNavHostController

    @Test fun riviAvaaTuotteenJaTakaisinPalaaListaan() {
        val repo = VaarennosRepository(listOf(Tuote(4, "maito")))
        compose.setContent {
            nav = TestNavHostController(LocalContext.current).apply {
                navigatorProvider.addNavigator(ComposeNavigator())
            }
            OstosNavigaatio(nav, luoListaViewModel = { ListaViewModel(repo) })
        }
        compose.onNodeWithText("maito × 1").performClick()
        val reitti = nav.currentBackStackEntry!!.toRoute<TuoteReitti>()
        assertEquals(TuoteReitti(4, "maito"), reitti)

        compose.onNodeWithText("Takaisin").performClick()
        assertTrue(nav.currentBackStackEntry!!.destination
                       .hasRoute(ListaReitti::class))
    }
}
// @loppu testi
