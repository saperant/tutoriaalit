# Jetpack Compose

Compose on **deklaratiivinen** käyttöliittymäkirjasto: käyttöliittymä
kuvataan funktiona tilasta, `UI = f(tila)`. Kun tila muuttuu, Compose
kutsuu tilaa lukevat funktiot uudelleen ja päivittää näytön. Näkymiä
ei muokata käsin (`textView.text = ...`), joten näkymä ja tila eivät
voi joutua ristiriitaan.

## Composable-funktiot ja koostaminen

Composable-funktio on Kotlin-funktio, jolla on `@Composable`-merkintä.
Se ei palauta näkymää vaan *lisää* käyttöliittymän osia
koostumukseen (*composition*). Compose-kääntäjälaajennus muuntaa
funktion niin, että ajonaikainen kirjasto voi seurata, mitä tilaa
funktio luki, ja kutsua sen uudelleen, kun tila muuttuu. Tätä
uudelleenkutsua kutsutaan **uudelleenkoostamiseksi** (*recomposition*).

Composable-funktioista seuraa muutama sääntö:

- **Funktio voi suorittua milloin tahansa ja useita kertoja**, jopa
  jokaisella ruudunpäivityksellä animaation aikana. Siksi se ei saa
  tehdä sivuvaikutuksia (verkko, tietokanta, lokitus) suoraan
  rungossaan (luku 4).
- **Järjestystä ei taata.** Compose voi ohittaa funktion, jonka
  parametrit eivät muuttuneet, ja koostaa vain muuttuneen osan.
- **Funktio on nopea.** Raskas laskenta tehdään muualla tai muistetaan
  (`remember`).

## Tila ja tilan nostaminen

Tila, jota Compose seuraa, on `State`-olio (`mutableStateOf`,
`mutableIntStateOf`). Kun composable lukee arvon, se tilaa muutokset.
`remember` säilyttää olion uudelleenkoostamisten yli; ilman sitä tila
luotaisiin joka kutsulla alusta.

Uudelleenkäytettävä komponentti kirjoitetaan **tilattomaksi**: arvo
tulee parametrina ja muutos lähtee takaisinkutsuna. Tämä on **tilan
nostaminen** (*state hoisting*): tila nostetaan lähimpään yhteiseen
omistajaan, joka sitä tarvitsee.

```{.kotlin tiedosto="esimerkit/app/src/main/java/fi/esimerkki/ostokset/ui/MaaraValitsin.kt" osa="tilaton"}
```

Tilaton komponentti on helppo esikatsella, testata ja käyttää eri
tilanteissa: sama valitsin voi näyttää ViewModelin, tietokannan tai
lomakkeen arvoa. Tilallinen kääre on ohut:

```{.kotlin tiedosto="esimerkit/app/src/main/java/fi/esimerkki/ostokset/ui/MaaraValitsin.kt" osa="tilallinen"}
```

`by`-delegointi purkaa `State`-olion: `maara` on tavallinen `Int`, ja
sijoitus päivittää tilan. `mutableIntStateOf` välttää `Int`-arvon
paketoinnin, mikä on pieni mutta ilmainen säästö.

## Asettelu ja Modifier

Perusasettelut ovat `Column` (allekkain), `Row` (rinnakkain) ja `Box`
(päällekkäin). Kokoa, reunuksia, taustaa, kosketusta ja
saavutettavuutta säädetään **Modifier**-ketjulla. Ketjun järjestys
merkitsee: se luetaan ulkoa sisään.

```{.kotlin tiedosto="esimerkit/app/src/main/java/fi/esimerkki/ostokset/ui/Modifierit.kt" osa="jarjestys"}
```

```{.kotlin tiedosto="esimerkit/app/src/test/java/fi/esimerkki/ostokset/ui/ModifieritTest.kt" osa="testi"}
```

Ensimmäisessä reunus on napautusalan sisällä, jolloin painike täyttää
48 dp:n vähimmäiskoon, jota saavutettavuusohjeet suosittelevat.
Toisessa reunus jää napautusalan ulkopuolelle.

Komponentin ensimmäinen valinnainen parametri on aina
`modifier: Modifier = Modifier`, ja se annetaan komponentin
uloimmalle elementille. Näin kutsuja voi asetella komponentin ilman,
että komponentin tarvitsee tietää ympäristöstään.

## Material 3 ja teema

Material 3 -komponentit (`Button`, `TextField`, `Scaffold`,
`TopAppBar`) lukevat värit, typografian ja muodot `MaterialTheme`stä.
Sovelluksen teema asetetaan kerran ylimmälle tasolle:

```{.kotlin tiedosto="esimerkit/app/src/main/java/fi/esimerkki/ostokset/ui/Teema.kt" osa="teema"}
```

Komponentit käyttävät rooleja (`MaterialTheme.colorScheme.primary`,
`MaterialTheme.typography.bodyLarge`) eivätkä kiinteitä värejä, joten
tumma tila, käyttäjän fonttikoko ja Android 12:n dynaamiset värit
(`dynamicLightColorScheme`) toimivat ilman muutoksia komponentteihin.
Värit ja mitat ovat *suunnittelutokeneita*, kuten CSS:n mukautetut
ominaisuudet (tutoriaali *HTML ja CSS*).

## Esikatselu ja testaus

`@Preview`-merkitty composable näkyy Android Studion esikatselussa.
Tilattomalle komponentille esikatselu on yksinkertainen, koska tilan
voi antaa parametrina. Compose-testi koostaa komponentin, etsii
solmuja **semantiikkapuusta** ja tekee toimintoja kuten käyttäjä:

```{.kotlin tiedosto="esimerkit/app/src/test/java/fi/esimerkki/ostokset/ui/MaaraValitsinTest.kt" osa="testi"}
```

Testi etsii painikkeita niiden saavutettavuusnimellä
(`contentDescription`) eikä sisäisillä tunnisteilla. Sama puu, jota
testi käyttää, on se, jonka ruudunlukija TalkBack näkee (luku 4).
Testiä, joka löytää solmut nimillä, on vaikea kirjoittaa
saavuttamattomalle käyttöliittymälle.

`createComposeRule` tulee paketista `junit4.v2`, joka käyttää
korutiinitestien tavallista `StandardTestDispatcher`ia: tehtävät
jonotetaan eivätkä suoritu heti. Testin kello etenee, kun testi odottaa
(`waitForIdle`) tai kelaa sitä (`mainClock`).

## Käytännössä

- **Tilaton komponentti, tilallinen ruutu.** Komponentit saavat arvot
  ja takaisinkutsut. Tila asuu ruudun tasolla tai ViewModelissa.
  Tämä on **yksisuuntainen datavirta** (*unidirectional data flow*,
  UDF): tila virtaa alas, tapahtumat ylös.
- **Lue tila mahdollisimman alhaalla.** Uudelleenkoostaminen alkaa
  siitä funktiosta, joka luki muuttuneen tilan. Mitä syvemmällä tilaa
  luetaan, sitä pienempi osa koostetaan uudelleen.
- **`Modifier` parametrina, ei kiinteitä mittoja.** Komponentti, joka
  päättää oman leveytensä ja reunuksensa, on vaikea käyttää muualla.
- **Teeman roolit, ei värikoodeja.** Kiinteä väri komponentissa rikkoo
  tumman tilan ja dynaamiset värit.
- **Hinnat:** composable-funktio on halpa kutsua, mutta sen runko
  suoritetaan usein. Allokointi, lajittelu tai muotoilu rungossa
  toistuu jokaisella koostamisella; `remember` laskee sen vain
  avainten muuttuessa (luku 11).

## Itsearviointi

- Osaat selittää koostamisen ja uudelleenkoostamisen sekä sen, miksi
  composable-funktion rungossa ei tehdä sivuvaikutuksia.
- Osaat kirjoittaa tilattoman komponentin ja nostaa sen tilan
  omistajalle.
- Osaat käyttää `remember`- ja `rememberSaveable`-funktioita ja
  Modifier-ketjua oikeassa järjestyksessä.
- Osaat testata komponentin semantiikkapuun kautta Compose-testillä.
