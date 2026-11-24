package fi.esimerkki.ostokset.ui

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

// @alku teema
private val Vaalea = lightColorScheme(
    primary = Color(0xFF2E6B30),
    secondary = Color(0xFF52634F),
)
private val Tumma = darkColorScheme(
    primary = Color(0xFF94D88F),
    secondary = Color(0xFFB9CCB4),
)

/** Sovelluksen teema: värit tulevat MaterialThemesta, eivät
 *  komponenteista, joten tumma tila vaihtuu yhdestä kohdasta. */
@Composable
fun OstoksetTeema(
    tumma: Boolean = isSystemInDarkTheme(),
    sisalto: @Composable () -> Unit,
) {
    MaterialTheme(
        colorScheme = if (tumma) Tumma else Vaalea,
        content = sisalto,
    )
}
// @loppu teema
