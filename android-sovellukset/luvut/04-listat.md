# Listat ja saavutettavuus

Lähes jokaisessa sovelluksessa on vieritettävä lista. Tämä luku
rakentaa ostoslistan rivin ja listan, jotka näkyivät luvun 1 kuvassa,
ja käy läpi, miten käyttöliittymä näkyy ruudunlukijalle. Lista on
samalla ensimmäinen komponentti, joka näyttää sovelluksen omaa dataa,
tyyppiä `Tuote`:

```{.kotlin tiedosto="esimerkit/app/src/main/java/fi/esimerkki/ostokset/malli/Tuote.kt" osa="tuote"}
```

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
- **Tilaton rivi, tapahtumat ylös.** Rivi ei tiedä, mitä valinta tai
  napautus aiheuttaa; lista välittää tapahtumat omistajalleen. Sama
  rivi kelpaa esikatseluun, testiin ja toiseen listaan.
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
- Osaat selittää, miksi laiska lista on nopea ja milloin `contentType`
  auttaa.
- Osaat testata listan rivin tapahtumat erikseen.
- Osaat täydentää oman komponentin semantiikan niin, että
  ruudunlukija ja testit tunnistavat sen.
