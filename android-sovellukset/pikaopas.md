---
title: Android-sovellukset
subtitle: Pikaopas · Kotlin, Jetpack Compose ja testattava arkkitehtuuri
---

# Komennot

| Komento | Tehtävä |
|---------|---------|
| `./gradlew assembleDebug` | kehitysversion APK |
| `./gradlew testDebugUnitTest` | JVM-testit (myös Robolectric) |
| `./gradlew lintDebug` | Android Lint |
| `./gradlew connectedDebugAndroidTest` | laitetestit |
| `./gradlew bundleRelease` | julkaisu-AAB (R8, allekirjoitus) |
| `adb shell am kill <paketti>` | prosessin kuolema (sovellus taustalla) |

# SDK-versiot

| Asetus | Merkitys |
|--------|----------|
| `compileSdk` | rajapinnat, joita vasten käännetään; uusin vakaa |
| `targetSdk` | käyttäytymis-muutokset, joihin on sitouduttu |
| `minSdk` | vanhin tuettu; uudempi API vaatii `SDK_INT`-tarkistuksen |

# Tila

| Säilyy | `remember` | `...Saveable` | ViewModel | Room, DataStore |
|--------|:-:|:-:|:-:|:-:|
| uudelleenkoostaminen | kyllä | kyllä | kyllä | kyllä |
| konfiguraatiomuutos | ei | kyllä | kyllä | kyllä |
| prosessin kuolema | ei | kyllä | ei | kyllä |
| sovelluksen sulkeminen | ei | ei | ei | kyllä |

Tilan nostaminen: arvo sisään, muutos ulos.

```{.kotlin tiedosto="esimerkit/app/src/main/java/fi/esimerkki/ostokset/Pikaopas.kt" osa="nostettu"}
```

# ViewModel

```{.kotlin tiedosto="esimerkit/app/src/main/java/fi/esimerkki/ostokset/Pikaopas.kt" osa="viewmodel"}
```

Käyttöliittymässä
`val n by vm.ostamatta.collectAsStateWithLifecycle()`.
Ei Contextia eikä merkkijonoja ViewModeliin; viestit tyyppeinä.

# Efektit

| Efekti | Käyttö |
|--------|--------|
| `LaunchedEffect(avain)` | korutiini; uudelleen avaimen muuttuessa |
| `DisposableEffect(avain)` | rekisteröinti + `onDispose` |
| `SideEffect` | jokaisen onnistuneen koostamisen jälkeen |
| `rememberCoroutineScope()` | korutiini tapahtumankäsittelijästä |
| `rememberUpdatedState(x)` | uusin arvo pitkässä efektissä |
| `derivedStateOf { }` | harvemmin muuttuva johdettu tila |

```{.kotlin tiedosto="esimerkit/app/src/main/java/fi/esimerkki/ostokset/Pikaopas.kt" osa="efekti"}
```

# Listat ja saavutettavuus

- `LazyColumn { items(lista, key = { it.id }) { ... } }`: avain aina.
- `Modifier.semantics(mergeDescendants = true) { stateDescription = .. }`
- Kuvakepainikkeelle `contentDescription`, koristeelle `null`.
- Kosketusalue vähintään 48 dp; reunus *ennen* `clickable` pienentää aluetta.

# Navigointi

```{.kotlin tiedosto="esimerkit/app/src/main/java/fi/esimerkki/ostokset/navigointi/Navigaatio.kt" osa="reitit"}
```

`navigate(TuoteReitti(4, "maito"))`,
`entry.toRoute<TuoteReitti>()`,
`savedStateHandle.toRoute<TuoteReitti>()`. Argumentteina tunnisteita.

# Room

```{.kotlin tiedosto="esimerkit/app/src/main/java/fi/esimerkki/ostokset/data/Tietokanta.kt" osa="tietokanta"}
```

DAO: `Flow<List<T>>` havaittaville kyselyille, `suspend` muille,
`@Upsert`. Skeema versionhallintaan, migraatiot testattuina.

# Taustatyö

| Työ | Väline |
|-----|--------|
| ruudun ajan | `viewModelScope` |
| pitää valmistua | WorkManager + `Constraints` |
| näkyvä, pitkä | etualan palvelu |
| tarkka aika | `AlarmManager` |

`enqueueUniquePeriodicWork(nimi, KEEP, pyynto)`; `Result.retry()`
takaisinvedolla; työn on kestettävä toisto.

# Testaus

| Kohde | Väline |
|-------|--------|
| ViewModel | `MainDispatcherRule`, väärennös, Turbine |
| composable | `v2.createComposeRule`, `onNodeWithText`, `StateRestorationTester` |
| Room, WorkManager | Robolectric, `inMemoryDatabaseBuilder`, `TestListenableWorkerBuilder` |
| verkko | Ktor `MockEngine` |
| navigointi | `TestNavHostController` |
| intent | `shadowOf(activity).nextStartedActivity` |
| kuvakaappaus | `@GraphicsMode(NATIVE)`, Roborazzi `captureRoboImage` |
| koko sovellus | `src/androidTest`, emulaattori |

`robolectric.properties`: `application=android.app.Application`,
`sdk=36`.

# Sudenkuopat

- Tila Activityssä tai staattisessa kentässä → katoaa tai vuotaa.
- `collectAsState` ilman elinkaarta → keruu jatkuu taustalla.
- `runCatching` korutiinissa → sieppaa peruutuksen.
- Avaimeton lista → rivien tila siirtyy väärille riveille.
- Uusi epävakaa olio composablessa → lapsi koostetaan aina.
- Verkko tai levy pääsäikeessä → nykiminen, ANR.
- `fallbackToDestructiveMigration` käyttäjän datalle → data katoaa.
- Vastaanotettu intent ilman tarkistusta → vieras sovellus syöttää dataa.
