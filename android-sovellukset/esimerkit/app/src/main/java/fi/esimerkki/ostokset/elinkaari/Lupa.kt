package fi.esimerkki.ostokset.elinkaari

import android.Manifest
import android.os.Build
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.material3.Button
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable

// @alku lupa
/** Pyytää ilmoitusluvan ajonaikaisesti (Android 13+). Tulos tulee
 *  takaisinkutsuna, koska järjestelmä näyttää oman valintaikkunansa. */
@Composable
fun IlmoitusLupaPainike(onTulos: (Boolean) -> Unit) {
    val pyyda = rememberLauncherForActivityResult(
        ActivityResultContracts.RequestPermission(),
        onTulos,
    )
    Button(onClick = {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            pyyda.launch(Manifest.permission.POST_NOTIFICATIONS)
        } else {
            onTulos(true)   // vanhemmissa versioissa lupa on valmiiksi
        }
    }) {
        Text("Salli muistutukset")
    }
}
// @loppu lupa
