# Johdanto {.runko-johdanto}

Android on maailman yleisin käyttöjärjestelmä: sitä käyttävät
puhelimet, tabletit, kellot, autojen viihdejärjestelmät, televisiot ja
monet teollisuuden päätelaitteet. Tämä tutoriaali opettaa kirjoittamaan
Android-sovelluksia nykyisellä tavalla: **Kotlinilla**, käyttöliittymä
**Jetpack Composella** ja arkkitehtuuri niin, että lähes kaikki
logiikka voidaan testata ilman laitetta.

## Esitiedot ja rajaus

Lukijan oletetaan osaavan taidon *Kotlin*, myös korutiinit ja Flow'n.
Kieltä ei opeteta tässä uudelleen; kun luvussa tarvitaan kielen
piirrettä, viitataan siihen taitoon. Android-kehityksestä ei oleteta
aiempaa kokemusta.

Tutoriaali rajautuu yhteen sovellukseen puhelimella:

- Sovelluksen palvelinpuoli (rajapinnat, todennus, idempotenssi) on
  taidossa *Taustapalvelut*, ja SQL:n perusteet taidossa *SQL ja
  relaatiotietokannat*.
- Vanhaa näkymäjärjestelmää (XML-asettelut, Fragmentit) ei opeteta,
  ei myöskään Kotlin Multiplatformia, Wear OS:ää tai Android Autoa.
- Suorituskyvyn mittaamisen yleiset periaatteet ovat taidossa
  *Suorituskyvyn analyysi ja optimointi*; luku 11 käsittelee vain
  Androidin omat välineet.

## Lyhyt historia

| Vuosi | Tapahtuma |
|-------|-----------|
| 2008 | Ensimmäinen Android-puhelin; sovellukset Javalla, käyttöliittymä XML-asetteluina |
| 2014 | Android Studio ja Gradle-pohjainen käännös korvaavat Eclipse-työkalut |
| 2017 | Kotlin virallisesti tuettu kieli; Architecture Components (ViewModel, LiveData, Room) |
| 2018 | Jetpack kokoaa tukikirjastot; AndroidX korvaa support-kirjastot |
| 2019 | *Kotlin first*: uudet rajapinnat suunnitellaan Kotlinille |
| 2021 | Jetpack Compose 1.0: deklaratiivinen käyttöliittymä |
| 2024– | Compose on suositeltu tapa; Kotlin Multiplatform jakaa logiikkaa iOS:n kanssa |

Vanha *näkymäjärjestelmä* (View, XML-asettelut, `findViewById`,
Fragmentit) on yhä laajasti käytössä vanhoissa sovelluksissa, ja sen
perusteet kannattaa tunnistaa. Uusi koodi kirjoitetaan Composella, ja
molemmat voivat elää samassa sovelluksessa (`ComposeView` ja
`AndroidView`).

## Sovelluksen palaset

Android-sovellus ei ole yksi `main`-funktio vaan joukko
**komponentteja**, joita järjestelmä käynnistää tarpeen mukaan:

- **Activity** on yksi käyttäjälle näkyvä ikkuna. Compose-sovelluksessa
  on yleensä vain yksi Activity, ja ruudut ovat composable-funktioita.
- **Service** tekee pitkäkestoista työtä ilman käyttöliittymää.
  Ajastettu ja lykättävä työ tehdään nykyään WorkManagerilla (luku 9).
- **BroadcastReceiver** reagoi järjestelmän tapahtumiin.
- **ContentProvider** jakaa dataa sovellusten välillä.

Komponentit ilmoitetaan **manifestissa** (`AndroidManifest.xml`), josta
järjestelmä tietää, mitä sovellus sisältää ja mitä oikeuksia se
tarvitsee. Järjestelmä hallitsee **prosessia**: se voi lopettaa
taustalla olevan sovelluksen milloin tahansa muistin vapauttamiseksi ja
käynnistää sen myöhemmin uudelleen. Tämä yksi tosiasia selittää suuren
osan Android-arkkitehtuurista (luku 2).

## Työkalut

| Työkalu | Tehtävä |
|---------|---------|
| Android Studio | IntelliJ-pohjainen IDE: editori, esikatselu, debuggeri, profiloijat, emulaattori |
| Android SDK | alustan kirjastot (`platforms`), käännöstyökalut (`build-tools`), `adb` (`platform-tools`) |
| Gradle ja Android Gradle Plugin (AGP) | käännös, riippuvuudet, testit, julkaisupaketit |
| Kotlin-kääntäjä ja Compose-kääntäjälaajennus | Kotlin-koodi ja composable-funktioiden muunnos |
| Emulaattori, `adb` | sovelluksen ajo ja virheenjäljitys laitteella |
| Lint | Android-kohtainen staattinen analyysi |

Esimerkkien versiot ovat AGP 9.5, Kotlin 2.4, Compose BOM 2026.11
ja `compileSdk` 37.2. Versiot on kiinnitetty versioluetteloon, joten
esimerkit kääntyvät samoin myöhemminkin.

## Projektin rakenne

Esimerkit ovat yksi Gradle-projekti, pieni **ostoslistasovellus**, joka
kasvaa luku luvulta. Valmis sovellus näyttää tältä:

![Ostoslistan päänäkymä. Tämän tutoriaalin kuvat sovelluksesta ovat
kuvakaappauksia, jotka testit tuottavat ilman laitetta (luku
10).](kuvat/lista.png){width=32%}

Hakemistorakenne:

```text
esimerkit/
├── settings.gradle.kts        projektin moduulit ja varastot
├── build.gradle.kts           juuriprojekti: liitännäisten versiot
├── gradle/libs.versions.toml  versioluettelo
├── gradlew, gradle/wrapper/   Gradle Wrapper (kiinnitetty Gradle)
└── app/
    ├── build.gradle.kts       sovellusmoduulin asetukset
    └── src/
        ├── main/              sovelluksen koodi, manifesti, resurssit
        └── test/              JVM-testit (JUnit, Robolectric)
```

`settings.gradle.kts` kertoo, mistä liitännäiset ja kirjastot haetaan
ja mitä moduuleja projektissa on:

```{.kotlin tiedosto="esimerkit/settings.gradle.kts" osa="asetukset"}
```

`FAIL_ON_PROJECT_REPOS` kieltää moduuleja lisäämästä omia
varastojaan, joten riippuvuudet tulevat vain luetelluista lähteistä.
Isommassa sovelluksessa moduuleja on useita (`:core:data`,
`:feature:lista`), mikä nopeuttaa käännöstä ja pakottaa rajapinnat
näkyviksi.

**Versioluettelo** (`gradle/libs.versions.toml`) kokoaa kaikkien
riippuvuuksien versiot yhteen paikkaan:

```{.toml tiedosto="esimerkit/gradle/libs.versions.toml" osa="versiot"}
```

Kirjastot nimetään luettelossa, ja Gradle tuottaa niille tyypitetyt
viittaukset (`libs.room.runtime`):

```{.toml tiedosto="esimerkit/gradle/libs.versions.toml" osa="kirjastot"}
```

Pitkät rivit voi kirjoittaa taulukkomuodossa:

```{.toml tiedosto="esimerkit/gradle/libs.versions.toml" osa="taulukko"}
```

Sovellusmoduulin `build.gradle.kts` ottaa liitännäiset käyttöön ja
määrittelee Android-asetukset:

```{.kotlin tiedosto="esimerkit/app/build.gradle.kts" osa="liitannaiset"}
```

```{.kotlin tiedosto="esimerkit/app/build.gradle.kts" osa="android"}
```

Kolme SDK-versiota tarkoittavat eri asioita:

- **`compileSdk`**: minkä Android-version rajapintoja vasten käännetään.
  Uusin vakaa versio; muuttaminen ei muuta sovelluksen käytöstä.
- **`targetSdk`**: minkä version käyttäytymiseen sovellus on
  sitoutunut. Uudet versiot muuttavat oletuksia (oikeudet, taustatyöt,
  reunasta reunaan -näyttö) vasta, kun `targetSdk` nostetaan. Google
  Play vaatii tuoreen arvon.
- **`minSdk`**: vanhin tuettu versio. Tätä vanhemmille laitteille
  sovellusta ei voi asentaa, ja uudempien rajapintojen käyttö vaatii
  versiotarkistuksen (luku 2). Versio 26 (Android 8) kattaa lähes
  kaikki käytössä olevat laitteet.

Kotlin-asetukset ja riippuvuudet:

```{.kotlin tiedosto="esimerkit/app/build.gradle.kts" osa="kotlin"}
```

```{.kotlin tiedosto="esimerkit/app/build.gradle.kts" osa="riippuvuudet"}
```

`platform(libs.compose.bom)` tuo *Bill of Materials* -luettelon, joka
valitsee yhteensopivat versiot kaikille Compose-kirjastoille, joten
niille ei kirjoiteta versioita erikseen. `ksp` ajaa Roomin
koodigeneraattorin käännöksen aikana (luku 7). `debugImplementation`
tulee vain kehitysversioon, `testImplementation` vain testeihin.

## Esimerkkien ajaminen ja testaus

Kaikki esimerkit käännetään ja testataan komentoriviltä Gradle
Wrapperilla, joka lataa projektiin kiinnitetyn Gradle-version:

```text
./gradlew assembleDebug          # kehitysversion APK
./gradlew lintDebug              # Android Lint
./gradlew testDebugUnitTest      # JVM-testit, myös Robolectric
./gradlew installDebug           # asennus laitteelle tai emulaattoriin
```

Esimerkkihakemiston `make` ajaa kolme ensimmäistä. Testit ajetaan
JVM:llä **Robolectricin** avulla: se tarjoaa Androidin kirjastot
tietokoneella, joten Activityt, Compose-käyttöliittymä, Room ja
WorkManager voidaan testata ilman emulaattoria. Kehityskontissa on
Android SDK valmiina; kontin avaaminen neuvotaan oppaassa
*Kehitysympäristöt ja Dev Containers*. Laitteella ajettavat testit
esitellään luvussa 10.

Useimmat käyttöliittymän merkkijonot on kirjoitettu suoraan koodiin
lyhyyden vuoksi. Oikeassa sovelluksessa ne ovat resursseissa
(`res/values/strings.xml`), jotta ne voidaan kääntää. Esimerkin
viestit tehdään näin (luku 2).
