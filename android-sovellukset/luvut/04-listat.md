# Listat, sivuvaikutukset ja saavutettavuus

Lähes jokaisessa sovelluksessa on vieritettävä lista, ja lähes
jokaisessa ruudussa tehdään jotain, mikä ei ole piirtämistä: näytetään
ilmoitus, käynnistetään animaatio, rekisteröidään kuuntelija. Tämä luku
käsittelee molemmat sekä sen, miten käyttöliittymä näkyy
ruudunlukijalle.

## Rivi ja laiska lista

Ostoslistan rivi on tilaton komponentti, jolla on kaksi tapahtumaa:

```{.kotlin tiedosto="esimerkit/app/src/main/java/fi/esimerkki/ostokset/ui/TuoteRivi.kt" osa="rivi"}
```

`LazyColumn` koostaa vain näkyvät rivit, joten tuhannen rivin lista on
yhtä nopea kuin kymmenen:

```{.kotlin tiedosto="esimerkit/app/src/main/java/fi/esimerkki/ostokset/ui/TuoteRivi.kt" osa="lista"}
```

- **`key`** sitoo rivin tilan (`remember` rivin sisällä, vierityksen
  ankkuri, animaatio) tuotteen tunnisteeseen eikä paikkaan listassa.
  Ilman avainta rivin lisääminen alkuun siirtäisi jokaisen rivin tilan
  väärälle riville, ja `animateItem` ei tietäisi, mikä rivi liikkui.
  Avaimen on oltava vakaa ja yksilöllinen; listan indeksi ei kelpaa.
- **`contentType`** kertoo, mitkä rivit ovat samanlaisia, jotta
  Compose voi kierrättää niitä. Se on hyödyllinen, kun listassa on
  otsikoita ja eri tyyppisiä rivejä.
- Tavallinen `Column` ja `forEach` sopivat vain lyhyisiin listoihin,
  koska ne koostavat kaikki rivit.

Testissä rivin napautus ja valintaruudun napautus ovat eri tapahtumia:

```{.kotlin tiedosto="esimerkit/app/src/test/java/fi/esimerkki/ostokset/ui/TuoteListaTest.kt" osa="testi"}
```

## Sivuvaikutukset

Composable-funktion runko voi suorittua milloin tahansa, joten
toiminnot, jotka muuttavat jotain funktion ulkopuolella, tehdään
**efekteissä**. Efekti on sidottu koostumukseen: se alkaa, kun
composable tulee näkyviin, ja peruuntuu, kun se poistuu.

| Efekti | Käyttö |
|--------|--------|
| `LaunchedEffect(avain)` | korutiini, joka käynnistyy uudelleen avaimen muuttuessa: ilmoitus, animaatio, kertaluonteinen haku |
| `DisposableEffect(avain)` | rekisteröinti ja purku (`onDispose`): kuuntelija, sensori, elinkaaritarkkailija |
| `SideEffect` | suoritetaan jokaisen onnistuneen koostamisen jälkeen; tilan välitys koodille, jota Compose ei hallitse |
| `rememberCoroutineScope()` | korutiini tapahtumankäsittelijästä, esim. vieritys napin painalluksesta |
| `rememberUpdatedState(arvo)` | pitkäkestoinen efekti näkee uusimman arvon ilman uudelleenkäynnistystä |
| `derivedStateOf` | tila, joka lasketaan toisesta tilasta ja muuttuu harvemmin (esim. "vieritetty alas") |

Ostoslistan ruutu näyttää ViewModelin viestin ilmoituksena
(*snackbar*) ja kuittaa sen:

```{.kotlin tiedosto="esimerkit/app/src/main/java/fi/esimerkki/ostokset/lista/ListaRuutu.kt" osa="tilaton"}
```

`LaunchedEffect(tila.viesti)` käynnistyy aina, kun viesti vaihtuu, ja
`showSnackbar` odottaa, kunnes ilmoitus suljetaan. Jos ruutu poistuu
kesken, korutiini peruuntuu, eikä viestiä kuitata. Testi kelaa
Composen kelloa, jotta ilmoituksen aikakatkaisu kuluu heti:

```{.kotlin tiedosto="esimerkit/app/src/test/java/fi/esimerkki/ostokset/lista/ListaSisaltoTest.kt" osa="testi"}
```

Ensimmäinen testi näyttää tilan nostamisen arvon: tilaton ruutu
testataan antamalla sille tila, ilman ViewModelia, tietokantaa tai
verkkoa.

## Saavutettavuus semantiikalla

Compose rakentaa käyttöliittymästä **semantiikkapuun**, jonka
TalkBack, Switch Access ja testit lukevat. Material-komponentit
tuottavat oikean semantiikan valmiiksi: `Button` on painike,
`Checkbox` valintaruutu tilatietoineen, `TextField` muokattava kenttä
nimiöineen. Omissa komponenteissa semantiikka täydennetään
`Modifier.semantics`-lohkolla:

- **`contentDescription`** antaa nimen elementille, jolla ei ole
  näkyvää tekstiä, kuten kuvakepainikkeelle ("Vähennä"). Koristekuvan
  kuvaus on `null`, jotta ruudunlukija ohittaa sen.
- **`stateDescription`** kertoo tilan ihmisen kielellä ("3 kpl",
  "ostettu").
- **`mergeDescendants = true`** yhdistää lapset yhdeksi solmuksi:
  määrävalitsin luetaan "3 kpl" eikä kolmena erillisenä elementtinä.
- **`clickable(onClickLabel = ...)`** kertoo toiminnon ("kaksoisnapauta
  avataksesi tuotteen").
- **Kosketusalue** on vähintään 48 × 48 dp. Material-komponentit
  laajentavat napautusalan automaattisesti (`minimumInteractiveComponentSize`).

Saavutettavuus kannattaa tarkistaa laitteella TalkBackilla ja
*Accessibility Scanner* -sovelluksella sekä testeissä etsimällä
solmuja niiden nimillä ja tiloilla, kuten tämän tutoriaalin testit
tekevät.

## Käytännössä

- **Avain jokaiselle listan riville.** Tietokannan pääavain on luonteva
  valinta. Avaimeton lista toimii, kunnes rivejä lisätään, poistetaan
  tai järjestetään.
- **Ei sivuvaikutuksia rungossa.** Lokitus, analytiikka, verkkopyyntö
  tai tilan kirjoittaminen rungossa toistuu jokaisella koostamisella.
  Valitse efekti sen mukaan, milloin työn pitää alkaa ja loppua.
- **Kertaluonteinen tapahtuma on tilaa, joka kuitataan.** Viesti tai
  siirtymä mallinnetaan tilaan (`viesti: Viesti?`), käyttöliittymä
  käsittelee sen efektissä ja kuittaa. Näin tapahtuma ei katoa
  konfiguraatiomuutoksessa eikä toistu.
- **Testaa saavutettavuusnimillä.** Testi, joka etsii "Vähennä"-nimeä,
  epäonnistuu, jos nimi puuttuu, eli testit valvovat samalla
  saavutettavuutta.
- **Hinnat:** jokainen listan rivi koostetaan, kun se vieritetään
  näkyviin. Raskas rivi (iso kuva, monimutkainen asettelu) näkyy
  nykimisenä. Kuvat ladataan kirjastolla, joka skaalaa ja tallentaa
  välimuistiin (esim. Coil).

## Itsearviointi

- Osaat tehdä laiskan listan, jossa riveillä on vakaat avaimet, ja
  selittää, mitä avaimen puuttuminen rikkoo.
- Osaat valita oikean efektin (`LaunchedEffect`, `DisposableEffect`,
  `rememberCoroutineScope`) tilanteen mukaan.
- Osaat mallintaa kertaluonteisen tapahtuman tilana ja kuitata sen.
- Osaat täydentää oman komponentin semantiikan niin, että
  ruudunlukija ja testit tunnistavat sen.
