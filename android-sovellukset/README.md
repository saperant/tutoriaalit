# Android-sovellukset

Tiivis suomenkielinen tutoriaali Android-sovellusten kehityksestä
Kotlinilla ja Jetpack Composella. Esitieto: taito
[Kotlin](../kotlin/). Valmiit dokumentit:
[android-sovellukset.pdf](https://saperant.github.io/tutoriaalit/materiaalit/android-sovellukset.pdf) ja pikaopas
[android-sovellukset-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/android-sovellukset-pikaopas.pdf).

## Sisältö

1. Johdanto – alusta ja historia, työkalut, projektin rakenne,
   versioluettelo, SDK-versiot
2. Sovelluksen rakenne ja elinkaari – manifesti, resurssit, Activity,
   konfiguraatiomuutos, prosessin kuolema, intentit, ajonaikaiset
   oikeudet
3. Jetpack Compose – koostaminen, tila ja sen nostaminen, Modifier,
   Material 3 -teema, Compose-testit
4. Listat ja saavutettavuus – `LazyColumn` ja avaimet, semantiikka
5. Arkkitehtuuri – UI-tila, ViewModel ja `StateFlow`,
   sivuvaikutukset ja efektit, repository, riippuvuuksien
   injektointi, ViewModel-testit
6. Navigointi – tyypitetyt reitit, `NavHost`, testaus
7. Tallennus – Room, migraatiot, DataStore
8. Verkko ja offline first – Ktor, kotlinx.serialization,
   synkronointi, ristiriidat
9. Taustatyöt – WorkManager, ehdot, uudelleenyritys
10. Testaus – testipyramidi, Robolectric, kuvakaappaukset,
    laitetestit
11. Suorituskyky, laatu ja julkaisu – vakaus ja uudelleenkoostaminen,
    ANR, Lint, R8 ja julkaisu
12. Lopuksi – nyrkkisäännöt, mallit, hinnat, jatkotaidot ja lähteet

## Esimerkit ja testaus

Esimerkit ovat yksi Gradle-projekti hakemistossa `esimerkit/`: pieni
offline first -ostoslistasovellus (AGP 9.5, Kotlin 2.4, Compose BOM
2026.11, `compileSdk` 37.2). Kaikki tekstissä näkyvä koodi on
projektin tiedostoista.

```text
make -C esimerkit   # käännös (myös laitetestit), Lint, JVM-testit
make testaa              # lisäksi tekstin viittausten tarkistus
make pdf                 # PDF:t
make kuvat               # kuvakaappaukset testeistä hakemistoon kuvat/
```

Testit ajetaan JVM:llä Robolectricin avulla, joten emulaattoria ei
tarvita. Laitetestit (`src/androidTest`) käännetään mutta ajetaan vain
laitteella: `./gradlew connectedDebugAndroidTest`.

Tarvitaan JDK 21 ja Android SDK (`ANDROID_HOME`). Kehityskontti
(`.devcontainer/android-sovellukset`) asentaa molemmat; sen
rakentaminen hyväksyy Android SDK:n lisenssiehdot.
Esimerkkien avaaminen kehityskontissa ja ajaminen: ks. [Kehitysympäristöt ja Dev Containers](../kehitysymparistot/), luku 2.

## Lisenssi

CC BY-SA 4.0.
