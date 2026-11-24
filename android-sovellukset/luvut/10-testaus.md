# Testaus

Aiemmat luvut testasivat jokaisen kerroksen. Tämä luku kokoaa
testauksen kokonaisuudeksi: mitä testataan millä tasolla, miten
Robolectric toimii ja mitä jää laitteelle.

## Testipyramidi Androidissa

| Taso | Mitä | Missä | Nopeus | Esimerkit |
|------|------|-------|--------|-----------|
| yksikkö | ViewModel, repository, muunnokset, DataStore | JVM | ms | `ListaViewModelTest`, `AsetuksetTest`, `OstosApiTest` |
| integraatio JVM:llä | Room, WorkManager, Compose, navigointi | JVM + Robolectric | 0,1–1 s | `TuoteDaoTest`, `SynkronointiTyoTest`, `NavigaatioTest` |
| laite | koko sovellus, laitteisto, järjestelmän dialogit | emulaattori tai laite | sekunteja | `OstoksetLaitteellaTest` |

Suurin osa testeistä on alimmilla tasoilla. Ne ovat nopeita,
luotettavia ja ajettavissa jokaisessa CI-ajossa. Laitetestejä on
vähän, ja ne kattavat tärkeimmät käyttäjäpolut.

Pyramidi toimii vain, jos arkkitehtuuri sallii sen: ViewModel ilman
Androidia (luku 5), tilattomat composablet (luku 3), riippuvuudet
muodostimissa (luku 5) ja vaihdettava verkkomoottori (luku 8).
Testattavuus on suunnittelun tulos, ei testaajan taito.

## Robolectric

Robolectric korvaa Androidin kirjastot JVM:llä toimivilla
toteutuksilla (*shadows*) ja käyttää oikeaa Android-koodia siltä osin
kuin se on mahdollista. Asetukset annetaan tiedostossa
`src/test/resources/robolectric.properties`:

```{.ini tiedosto="esimerkit/app/src/test/resources/robolectric.properties" osa="robolectric"}
```

- **Testisovellus.** Robolectric luo manifestin `Application`-luokan
  jokaisessa testissä. Tämän sovelluksen `onCreate` ajastaa
  WorkManager-työn, mikä ei kuulu testeihin, joten testit käyttävät
  tavallista `Application`ia. Testikohtaisesti saman voi tehdä
  `@Config(application = ...)`-merkinnällä.
- **SDK-versio kiinnitetään.** Robolectric tukee uusimpia Android-
  versioita viiveellä, ja tulos ei saa riippua siitä.
- **Resurssit.** `unitTests.isIncludeAndroidResources = true`
  (luku 1) antaa testeille manifestin ja resurssit.

Robolectric ei ole laite: grafiikka piirretään yksinkertaistetusti,
laitteistoa (kamera, Bluetooth) ei ole, ja järjestelmän sovellukset
puuttuvat. Asettelun mitat ja semantiikka ovat kuitenkin oikeat, joten
Compose-testit toimivat (luvut 3–4).

## Väärennökset, ei mokkeja

Esimerkkien testit käyttävät **väärennöksiä**: `VaarennosRepository`
(luku 5), `MockEngine` verkolle (luku 8), muistitietokanta (luku 7).
Mokkauskirjastot (MockK, Mockito) tarkistavat kutsuja, mikä sitoo testin
toteutukseen: refaktorointi rikkoo testit, vaikka käytös ei muutu.
Väärennös toteuttaa saman rajapinnan yksinkertaisesti, ja testi
tarkistaa tuloksen.

## Laitetestit

Laitetestit ovat hakemistossa `src/androidTest`, ja ne ajetaan
emulaattorilla tai laitteella:

```{.kotlin tiedosto="esimerkit/app/src/androidTest/java/fi/esimerkki/ostokset/OstoksetLaitteellaTest.kt" osa="testi"}
```

Testi käyttää samaa Compose-testirajapintaa kuin JVM-testit, mutta
käynnistää oikean `MainActivity`n oikeassa sovelluksessa. Tämän
tutoriaalin automaattinen testaus kääntää laitetestit
(`assembleDebugAndroidTest`) mutta ei aja niitä, koska testiympäristössä
ei ole emulaattoria. Laitetestien ajamiseen:

```text
# emulaattori ilman ikkunaa (esim. CI:ssä)
KUVA="system-images;android-36;google_apis;x86_64"
sdkmanager "$KUVA" "emulator"
avdmanager create avd -n testi -k "$KUVA"
emulator -avd testi -no-window -no-audio &
adb wait-for-device
./gradlew connectedDebugAndroidTest
```

Gradlen **hallitut laitteet** (*Gradle Managed Devices*) määrittelevät
emulaattorin `build.gradle.kts`-tiedostossa ja käynnistävät sen
testejä varten (`./gradlew pixel6Api36DebugAndroidTest`). Firebase
Test Lab ja vastaavat palvelut ajavat testit oikeilla laitteilla.

Laitteella testataan vain se, mikä vaatii laitteen: järjestelmän
dialogit, laitteisto, suorituskyky, valmistajakohtaiset erot ja koko
sovelluksen käynnistys. Tämän sovelluksen lupadialogi (luku 2) ja
taustatyön ajoitus (luku 9) ovat hyviä ehdokkaita.

## Kuvakaappaustestit

Kuvakaappaustesti (*screenshot test*) piirtää composablen kuvaksi ja
vertaa sitä tallennettuun. Se havaitsee asettelun ja teeman
regressiot, joita semantiikkatestit eivät näe. Työkaluja ovat
Androidin *Compose Preview Screenshot Testing*, Paparazzi ja Roborazzi
(Robolectricin päällä). Kuvakaappaukset ovat herkkiä fonteille ja
renderöinnille, joten ne ajetaan kiinteässä ympäristössä.

## Testit CI:ssä

Esimerkkien `make` ajaa saman, mitä CI:n kannattaa ajaa jokaisessa
muutoksessa:

```{.makefile tiedosto="esimerkit/Makefile"}
```

Lint (`lintDebug`) on osa samaa ajoa, ja sen varoitukset ovat virheitä
(luku 11). Laitetestit ajetaan harvemmin, esimerkiksi ennen julkaisua
tai yöllä, koska emulaattorin käynnistys kestää minuutteja.

## Käytännössä

- **Testattava arkkitehtuuri ensin.** Jos testi vaatii laitteen,
  syy on yleensä koodissa: logiikka on Activityssä, riippuvuus luodaan
  sisällä tai composable lukee ViewModelia suoraan.
- **Pyramidi, ei jäätelötötterö.** Paljon nopeita JVM-testejä, vähän
  laitetestejä. Hitaat ja epävakaat laitetestit jätetään helposti
  ajamatta, jolloin niistä ei ole hyötyä.
- **Väärennökset rajapinnoille.** Repositorio, verkko ja kello
  vaihdetaan väärennöksiin; tietokanta testataan oikeana muistissa.
- **Testi ei saa riippua ajasta tai järjestyksestä.** Testidispatcher
  ja Composen testikello tekevät ajasta ohjattavaa (luvut 4–5).
- **Hinnat:** Robolectric-testiluokan ensimmäinen ajo lataa
  Android-kirjastot ja kestää sekunteja; seuraavat ovat nopeita. Ryhmittele
  testit niin, että samaa ympäristöä käytetään uudelleen, ja aja
  puhtaat JVM-testit ilman `@RunWith(AndroidJUnit4::class)`.

## Itsearviointi

- Osaat sijoittaa testin oikealle pyramidin tasolle ja perustella
  valinnan.
- Osaat määrittää Robolectricin testisovelluksen ja SDK-version.
- Osaat kirjoittaa laitetestin ja kertoa, miten se ajetaan
  emulaattorilla tai hallitulla laitteella.
- Osaat perustella väärennösten käytön mokkien sijaan.
