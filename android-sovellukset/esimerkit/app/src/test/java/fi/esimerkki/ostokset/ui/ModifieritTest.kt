package fi.esimerkki.ostokset.ui

import androidx.compose.ui.test.getBoundsInRoot
import androidx.compose.ui.test.hasClickAction
import androidx.compose.ui.test.junit4.v2.createComposeRule
import androidx.compose.ui.unit.dp
import androidx.test.ext.junit.runners.AndroidJUnit4
import org.junit.Assert.assertEquals
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

// @alku testi
@RunWith(AndroidJUnit4::class)
class ModifieritTest {
    @get:Rule val compose = createComposeRule()

    private fun napautusalanLeveys() =
        compose.onNode(hasClickAction()).getBoundsInRoot().let {
            it.right - it.left
        }

    @Test fun reunusKasvattaaNapautusalaa() {
        compose.setContent { ReunusNapautusalassa {} }
        assertEquals(72.dp, napautusalanLeveys())   // 16 + 40 + 16
    }

    @Test fun reunusUlkonaEiKasvata() {
        compose.setContent { ReunusNapautusalanUlkona {} }
        assertEquals(40.dp, napautusalanLeveys())
    }
}
// @loppu testi
