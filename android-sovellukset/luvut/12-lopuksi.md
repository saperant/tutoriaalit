# Lopuksi {.runko-kaytannot .runko-lahteet}

## Nyrkkisäännöt

1. **Prosessi kuolee.** Kaikki, mitä käyttäjä ei saa menettää,
   tallennetaan heti pysyvästi; Bundle on vain käyttöliittymän tilaa
   varten (luku 2).
2. **Yksi Activity, ruudut composableina.** Navigointi hoitaa
   siirtymät ja ViewModelien elinajan (luvut 2 ja 6).
3. **Tilaton komponentti, tilallinen ruutu.** Tila virtaa alas,
   tapahtumat ylös (luvut 3 ja 5).
4. **Ei sivuvaikutuksia composablen rungossa.** Efekti valitaan sen
   mukaan, milloin työn pitää alkaa ja loppua (luku 5).
5. **Ruudun tila yhtenä muuttumattomana arvona** `StateFlow`ssa;
   kertaluonteinen tapahtuma on tilaa, joka kuitataan (luku 5).
6. **Tietokanta on totuuden lähde.** Käyttöliittymä lukee
   tietokantaa, verkko synkronoi sitä (luvut 7 ja 8).
7. **Kapea virheenkäsittely korutiineissa.** Siepataan odotetut
   virheet, ei peruutusta (luku 8).
8. **Taustatyö WorkManagerilla, ehdoin ja nimellä.** Työn on
   kestettävä toisto (luku 9).
9. **Testattava arkkitehtuuri.** Riippuvuudet muodostimeen,
   väärennökset rajapinnoille, suurin osa testeistä JVM:llä
   (luvut 5 ja 10).
10. **Varoitukset virheinä, mittaus ennen optimointia** (luku 11).

## Mallitaulukko

| Malli | Ongelma, jonka se ratkaisee | Luku |
|-------|-----------------------------|------|
| tilan nostaminen | uudelleenkäytettävä ja testattava komponentti | 3 |
| yksisuuntainen datavirta (UDF) | tila muuttuu vain yhdessä paikassa | 3, 5 |
| UI-tila data-luokkana | ristiriidattomat välitilat | 5 |
| tapahtuma tilana | viesti ei katoa eikä toistu | 5 |
| repository | tietolähteet piilossa käyttöliittymältä | 5, 8 |
| yksi totuuden lähde | kopiot eivät vanhene | 5, 7 |
| offline first | sovellus toimii ilman verkkoa | 8 |
| DTO–entiteetti–malli | rajapinta, skeema ja käyttöliittymä muuttuvat erikseen | 7, 8 |
| riippuvuuksien injektointi | vaihdettavat toteutukset ja testattavuus | 5 |
| väärennös (fake) | testit tarkistavat tuloksen, eivät kutsuja | 5, 10 |
| idempotentti taustatyö | toisto ei vahingoita | 9 |

## Hintoja

| Asia | Hinta | Keino |
|------|-------|-------|
| uudelleenkoostaminen | rungon suoritus joka kerta | tila luetaan alhaalla, `remember`, vakaat tyypit |
| epävakaa parametri | lapsi koostetaan aina | muuttumaton data-luokka, muistettu olio |
| I/O pääsäikeessä | nykiminen, ANR | suspend-funktiot, Room, DataStore |
| tietokannan avaus | kymmeniä ms | yksi instanssi säiliössä |
| radion herätys | akku | harvat, isot synkronoinnit WorkManagerilla |
| Flow taustalla | turhat kyselyt ja akku | `WhileSubscribed`, `collectAsStateWithLifecycle` |
| laitetesti | minuutteja, epävakaus | pyramidi: JVM-testit ensin |

## Jatkotaidot

- *Taustapalvelut*: sovelluksen palvelinpuoli, rajapintojen
  suunnittelu, todennus ja idempotenssiavain, jota synkronointi
  tarvitsee.
- *Tietoturvan perusteet* ja *Web-sovellusten tietoturva*: todennus,
  tokenien säilytys ja rajapinnan suojaaminen. Sovelluspaketin
  analysointia käsittelee *Takaisinmallinnus*.
- *Suorituskyvyn analyysi ja optimointi*: mittaamisen periaatteet
  luvun 11 työkalujen taustaksi.
- *Jatkuva integraatio ja toimitus*: käännös, testit ja julkaisu
  putkessa.

Tämän kokoelman ulkopuolella seuraavia aiheita ovat **Kotlin
Multiplatform ja Compose Multiplatform**, jotka jakavat logiikan (ja
halutessa käyttöliittymän) iOS:n, työpöydän ja verkon kanssa (Room,
DataStore ja Ktor toimivat jo monialustaisesti), sekä **suuret
näytöt, kellot ja autot**: adaptiiviset asettelut, Wear OS ja Android
Auto käyttävät samaa arkkitehtuuria.

## Lähteet

Teksti ja esimerkit on kirjoitettu tätä tutoriaalia varten.
Seuraavat lähteet ovat lisenssiltään avoimia tai vapaasti luettavia,
ja ne syventävät aiheita:

- **Android Developers -dokumentaatio**:
  <https://developer.android.com/> – *Guide to app architecture*,
  *Jetpack Compose*, *Room*, *DataStore*, *WorkManager*, *Navigation*,
  *Testing*. Teksti CC BY 4.0, koodiesimerkit Apache 2.0.
- **Now in Android** -esimerkkisovellus:
  <https://github.com/android/nowinandroid> – arkkitehtuurin,
  modularisoinnin ja testauksen malli (Apache 2.0).
- **Compose-dokumentaation syventävät osat**: *Thinking in Compose*,
  *Lifecycle of composables*, *Stability in Compose*, *Side-effects*.
- **Kotlin-dokumentaatio**: <https://kotlinlang.org/docs/> –
  korutiinit ja Flow (Apache 2.0).
- **Ktor**: <https://ktor.io/docs/client-create-new-application.html>
  ja **kotlinx.serialization**:
  <https://github.com/Kotlin/kotlinx.serialization> (Apache 2.0).
- **Robolectric**: <https://robolectric.org/> (MIT).
- **Roborazzi**: <https://github.com/takahirom/roborazzi>
  (Apache 2.0).
- **Turbine**: <https://github.com/cashapp/turbine> (Apache 2.0).
- **WCAG 2.2** ja Androidin saavutettavuusohjeet:
  <https://www.w3.org/TR/WCAG22/>,
  <https://developer.android.com/guide/topics/ui/accessibility>.

Kirjoja:

- Josh Skeen, David Greenhalgh, Bryan Sills: *Kotlin Programming: The
  Big Nerd Ranch Guide*, 2. painos. Big Nerd Ranch, 2021.
- Bryan Sills, Brian Gardner, Kristin Marsicano, Chris Stewart:
  *Android Programming: The Big Nerd Ranch Guide*, 5. painos. Big Nerd
  Ranch, 2022. Compose ja moderni arkkitehtuuri.
- Jorge Castillo: *Jetpack Compose Internals*. Leanpub, 2021–.
  Kääntäjälaajennus, koostumus ja uudelleenkoostaminen syvältä.

## Lisenssi

Tämä teos on lisensoitu Creative Commons Nimeä–JaaSamoin 4.0
Kansainvälinen -lisenssillä (CC BY-SA 4.0). Android on Google LLC:n
tavaramerkki.
