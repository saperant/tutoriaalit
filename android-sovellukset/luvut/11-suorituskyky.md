# Suorituskyky, laatu ja julkaisu

Puhelimessa on rajallinen suoritin, muisti ja akku, ja näytön on
päivityttävä 60–120 kertaa sekunnissa. Ruudunpäivitykseen on siis
8–16 ms. Tämä luku käsittelee Compose-kohtaiset hinnat, pääsäikeen
suojaamisen, koodin laadun tarkistukset ja julkaisuversion.
Yleiset periaatteet ovat taidossa *Suorituskyvyn analyysi ja
optimointi*.

## Uudelleenkoostaminen ja vakaus

Compose ohittaa composable-funktion, jos sen parametrit eivät
muuttuneet. Se, miten "ei muuttunut" päätellään, riippuu parametrin
tyypin **vakaudesta** (*stability*):

- **Vakaa tyyppi** (primitiivit, `String`, funktiotyypit, data-luokat,
  joiden kaikki ominaisuudet ovat `val` ja vakaita, sekä Kotlinin
  `List`) verrataan `equals`illa.
- **Epävakaa tyyppi** (luokka, jolla on `var`-ominaisuus tai
  epävakaa kenttä, sekä tyypit moduuleista, joita Compose-kääntäjä ei
  ole käsitellyt) verrataan identiteetillä (`===`). Tämä on
  *strong skipping* -tila, joka on oletus Kotlin 2.0.20:stä alkaen.

Kokeilu: sama lapsi kolmella eri tavalla kutsuttuna, ja vanhempi
koostetaan uudelleen kolmesti.

```{.kotlin tiedosto="esimerkit/app/src/main/java/fi/esimerkki/ostokset/ui/Rekompositio.kt" osa="tyypit"}
```

```{.kotlin tiedosto="esimerkit/app/src/main/java/fi/esimerkki/ostokset/ui/Rekompositio.kt" osa="huono"}
```

```{.kotlin tiedosto="esimerkit/app/src/main/java/fi/esimerkki/ostokset/ui/Rekompositio.kt" osa="hyva"}
```

```{.kotlin tiedosto="esimerkit/app/src/main/java/fi/esimerkki/ostokset/ui/Rekompositio.kt" osa="vakaa"}
```

```{.kotlin tiedosto="esimerkit/app/src/test/java/fi/esimerkki/ostokset/ui/RekompositioTest.kt" osa="testi"}
```

Tulokset:

1. **Uusi epävakaa olio** joka koostamisella: lapsi koostetaan joka
   kerta (1 + 3).
2. **Muistettu olio**: sama identiteetti, lapsi ohitetaan.
3. **Uusi mutta yhtä suuri lista**: `List<Tuote>` on vakaa, joten
   `equals` ratkaisee ja lapsi ohitetaan. Suodatus tehdään silti joka
   kerta, ja vertailu käy listan läpi; `remember(tuotteet)` poistaisi
   molemmat.

Testin kommentti osoittaa vielä yhden sudenkuopan: lambda, joka
kaappaa `var`-muuttujan, ei muistu, joten se on joka kerta uusi.

Korjauskeinot järjestyksessä: tee tilaluokista muuttumattomia
data-luokkia; muista koostumuksen aikana luodut oliot (`remember`);
merkitse ulkoisen moduulin tyyppi vakaaksi
**vakausasetustiedostolla** (`stabilityConfigurationFiles`) tai
`@Immutable`/`@Stable`-merkinnällä, jos se todella on muuttumaton.
Compose-kääntäjän raportit (`reportsDestination`) kertovat jokaisen
funktion ja tyypin vakauden, ja Android Studion *Layout Inspector*
näyttää koostamiskerrat.

## Pääsäie ja ANR

Pääsäie piirtää käyttöliittymän ja käsittelee syötteen. Jos se on
varattuna yli viisi sekuntia, järjestelmä näyttää *Application Not
Responding* -dialogin (ANR). Jo 16 ms ylitys näkyy nykimisenä.

- **I/O ja raskas laskenta pois pääsäikeestä.** Room, DataStore ja
  Ktor vaihtavat säiettä itse; oma raskas työ `withContext(Dispatchers.
  Default)`.
- **StrictMode** kehitysversiossa ilmoittaa levy- ja verkko-
  operaatioista pääsäikeessä (`StrictMode.setThreadPolicy`).
- **Käynnistysaika** mitataan Macrobenchmarkilla, ja **Baseline
  Profile** kertoo ART-ajoympäristölle, mitkä metodit käännetään
  valmiiksi asennuksessa. Profiili nopeuttaa käynnistystä ja
  ensimmäisiä ruutuja tyypillisesti kymmeniä prosentteja.

## Lint ja varoitukset virheinä

Android Lint tuntee Androidin sudenkuopat: puuttuvat
versiotarkistukset, saavutettavuus, tietoturva (esim. `exported`),
suorituskyky ja resurssit. Esimerkeissä varoitukset ovat virheitä:

```{.kotlin tiedosto="esimerkit/app/build.gradle.kts" osa="lint"}
```

Lint löysi tämän sovelluksen kehityksessä puuttuvan versiotarkistuksen
(`InlinedApi`, luku 2) ja puuttuvan sovelluskuvakkeen. Ajan myötä
vanhenevat tarkistukset (uudempi kirjastoversio, uudempi `targetSdk`)
on poistettu, jotta käännös ei rikkoudu itsestään; päivityksistä
huolehtii erillinen työkalu. Kotlin-kääntäjän varoitukset ovat myös
virheitä (`allWarningsAsErrors`, luku 1), mikä paljasti esimerkiksi
vanhentuneen Compose-testirajapinnan (luku 3).

## Julkaisuversio

Julkaisuversio (`release`) eroaa kehitysversiosta:

- **R8** pienentää ja hämärtää koodin (`isMinifyEnabled = true`) ja
  poistaa käyttämättömät resurssit (`isShrinkResources = true`).
  Heijastuksella käytetyt luokat säilytetään sääntötiedostolla
  (`proguard-rules.pro`). Julkaisuversio testataan erikseen, koska R8:n
  virheet näkyvät vain siinä.
- **Allekirjoitus.** Jokainen APK ja App Bundle allekirjoitetaan.
  *Play App Signing* säilyttää julkaisuavaimen Googlella, ja
  kehittäjä allekirjoittaa latausavaimella. Avaimia ei tallenneta
  versionhallintaan; CI saa ne salaisuuksina.
- **App Bundle** (`.aab`) on Google Playn julkaisumuoto: Play tuottaa
  siitä kullekin laitteelle sopivan APK:n.
- **Versionumerot.** `versionCode` kasvaa jokaisessa julkaisussa;
  `versionName` on käyttäjälle näkyvä.
- **Vaiheittainen julkaisu.** Sisäinen testaus, suljettu ja avoin
  testaus, sitten tuotanto prosentti kerrallaan. Kaatumisraportit
  (Play Console, Firebase Crashlytics) kertovat, pitääkö julkaisu
  pysäyttää.

## Käytännössä

- **Mittaa ennen optimointia.** Layout Inspector, kääntäjän
  vakausraportit, Perfetto ja Macrobenchmark kertovat, missä aika
  kuluu. Vakauden optimointi ilman mittausta lisää monimutkaisuutta
  turhaan.
- **Muuttumaton tila.** Data-luokat, `val`-ominaisuudet ja Kotlinin
  vain luku -kokoelmat tekevät tyypeistä vakaita ilman merkintöjä.
- **Ei raskasta työtä composablessa.** Suodatus, lajittelu ja muotoilu
  ViewModeliin tai `remember`iin.
- **Varoitukset virheinä alusta asti.** Myöhemmin käyttöön otettuna
  varoituksia on satoja, ja ne jäävät korjaamatta.
- **Julkaisuversio CI:ssä.** R8, allekirjoitus ja Baseline Profile
  tuotetaan automaattisesti, ja julkaisuversiolle ajetaan savutesti.
- **Hinnat:** uudelleenkoostaminen on halpaa, mutta asettelu ja
  piirto eivät; animaatio, joka lukee tilaa koostamisvaiheessa,
  koostaa joka ruudunpäivityksellä. Lue nopeasti muuttuva tila
  asettelu- tai piirtovaiheessa (`Modifier.offset { }`,
  `drawBehind { }`), jolloin koostamisvaihe ohitetaan.

## Itsearviointi

- Osaat selittää, miten tyypin vakaus vaikuttaa uudelleenkoostamisen
  ohittamiseen, ja korjata epävakaan parametrin.
- Osaat suojata pääsäikeen ja kuvata ANR:n syyt ja StrictModen
  käytön.
- Osaat ottaa Lintin ja kääntäjän varoitukset käyttöön virheinä ja
  perustella poistetut tarkistukset.
- Osaat kuvata julkaisuversion tuottamisen: R8, allekirjoitus, App
  Bundle ja vaiheittainen julkaisu.
