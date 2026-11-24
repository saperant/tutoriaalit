# MongoDB: dokumenttimalli

Dokumenttitietokanta tallentaa kokonaisuuksia, jotka luetaan yhdessä:
tilauksen riveineen, tuotteen ominaisuuksineen, käyttäjäprofiilin
asetuksineen. Dokumentti on sisäkkäinen rakenne kuten JSON, ja
kyselyt kohdistuvat myös sisäkkäisiin kenttiin ja taulukoihin.
MongoDB on tunnetuin dokumenttitietokanta; Couchbase ja Amazon
DocumentDB ovat saman perheen jäseniä, ja PostgreSQLin JSONB-sarake
tekee saman relaatiotietokannan sisällä (luku 6).

MongoDB tallentaa dokumentit BSON-muodossa, joka on JSON:n binäärinen
sukulainen: siinä on lisäksi päivämäärät, kokonaisluvut, desimaaliluvut
ja binääridata. Dokumentit ovat *kokoelmissa* (*collection*), ja
kokoelmat *tietokannoissa*. Jokaisella dokumentilla on yksilöllinen
`_id`; jos sitä ei anna, MongoDB luo `ObjectId`:n, jossa on luontiaika.

## Lisääminen ja haku

Tuotteet ovat dokumentteja, joiden `ominaisuudet` vaihtelevat
tuotteittain – juuri se, mikä relaatiomallissa vaatisi joko monta
tyhjää saraketta tai erillisen ominaisuustaulun:

```{.python tiedosto="esimerkit/nosql/data.py" osa="tuotteet"}
```

```{.python tiedosto="esimerkit/luku05/dokumentit.py" osa="lisays"}
```

Haku annetaan esimerkkidokumenttina, jonka kentät ovat ehtoja.
Operaattorit alkavat dollarimerkillä, ja sisäkkäiseen kenttään
viitataan pisteellä:

```{.python tiedosto="esimerkit/luku05/dokumentit.py" osa="haku"}
```

Toinen argumentti on *projektio*: mitkä kentät palautetaan. Kuten
SQL:ssä, palauta vain tarvittavat kentät.

## Päivitykset

Päivitys ei korvaa dokumenttia vaan muuttaa sitä operaattoreilla:
`$set` asettaa kentän, `$inc` kasvattaa lukua, `$push` lisää taulukkoon.
Jokainen yksittäisen dokumentin päivitys on atominen, joten
`$inc` ei kadota päivityksiä luvun 4 tapaan. *Upsert* lisää dokumentin,
jos ehtoa vastaavaa ei ole:

```{.python tiedosto="esimerkit/luku05/dokumentit.py" osa="paivitys"}
```

```{.tuloste tiedosto="esimerkit/luku05/dokumentit.odotettu"}
```

## Upotus vai viittaus

Dokumenttimallinnuksen tärkein päätös on, upotetaanko liittyvä tieto
dokumentin sisään vai viitataanko siihen tunnisteella. Tilauksen rivit
upotetaan, koska ne luetaan aina tilauksen kanssa, niitä on vähän
eivätkä ne muutu tilauksen jälkeen. Tuotteeseen viitataan, koska
tuote on oma kokonaisuutensa, jota muutetaan ja luetaan muutenkin:

```{.python tiedosto="esimerkit/luku05/upotus.py" osa="upotettu"}
```

Kun viitatun tiedon tarvitsee, `$lookup` tekee liitoksen
aggregaatioputkessa (luku 6). Se on hitaampi kuin relaatiotietokannan
liitos, eikä sitä ole tarkoitettu jokaisen haun perusosaksi:

```{.python tiedosto="esimerkit/luku05/upotus.py" osa="lookup"}
```

| Upota, kun | Viittaa, kun |
|------------|--------------|
| tieto luetaan aina yhdessä | tieto luetaan myös erikseen |
| suhde on yksi–muutama | suhde on yksi–moni tai moni–moni |
| upotettu tieto ei muutu tai muuttuu vain yhdessä paikassa | samaa tietoa käyttää moni dokumentti |
| dokumentti pysyy pienenä | upotettu osa kasvaa rajatta |

Dokumentin enimmäiskoko on 16 megatavua, mutta ongelmat alkavat paljon
aiemmin: koko dokumentti luetaan ja kirjoitetaan joka kerta. Rajatta
kasvava taulukko, kuten kaikki tuotteen arviot, kuuluu omaan
kokoelmaansa. Tilausten koko kannattaa siksi tarkistaa:

```{.python tiedosto="esimerkit/luku05/upotus.py" osa="kasvu"}
```

```{.tuloste tiedosto="esimerkit/luku05/upotus.odotettu"}
```

Upotettu tieto on kopio. Tilausriveihin on tallennettu hinta
tilaushetkellä, mikä on oikein: tilauksen hinta ei saa muuttua, vaikka
tuotteen hinta muuttuu. Tuotteen nimeä ei kopioitu, koska sen kuuluu
näkyä uusimpana. Tämä päätös tehdään kenttä kerrallaan.

## Mallinnusmalleja

Dokumenttimallinnukseen on vakiintunut nimettyjä malleja, joita kannattaa
tunnistaa:

- **Ämpäri** (*bucket*): aikasarjan mittaukset ryhmitellään
  dokumentteihin esimerkiksi tunneittain. Yksi dokumentti sisältää
  taulukon mittauksia ja valmiiksi lasketun keskiarvon. Dokumenttien
  määrä pienenee, ja indeksi pysyy pienenä. MongoDB:ssä on lisäksi
  erityiset aikasarjakokoelmat, jotka tekevät tämän automaattisesti.
- **Osajoukko** (*subset*): tuotteen dokumenttiin upotetaan vain kymmenen
  uusinta arviota, ja kaikki arviot ovat omassa kokoelmassaan.
  Tavallinen näkymä saadaan yhdellä haulla, eikä dokumentti kasva
  rajatta.
- **Laskettu kenttä** (*computed*): arvioiden lukumäärä ja keskiarvo
  päivitetään tuotteeseen jokaisen uuden arvion yhteydessä `$inc`-
  ja `$set`-operaatioilla, jotta niitä ei lasketa joka luvulla.
- **Laajennettu viittaus** (*extended reference*): tilaukseen kopioidaan
  asiakkaasta vain toimitukseen tarvittavat kentät (nimi, osoite).
  Kopio on tietoinen: tilauksen osoite ei saa muuttua jälkikäteen.
- **Skeeman versio** (*schema versioning*): jokaisessa dokumentissa on
  `versio`-kenttä, ja sovellus osaa lukea kaikki käytössä olevat
  versiot. Vanhat dokumentit päivitetään taustalla tai luettaessa.

Kaikissa malleissa toistuu sama kauppa: lukujen nopeus maksetaan
kirjoitusten monimutkaisuudella ja kopioiden ylläpidolla.

## Indeksit ja kyselysuunnitelma

Ilman indeksiä MongoDB lukee koko kokoelman (*COLLSCAN*).
`explain()` näyttää valitun suunnitelman ja kuinka monta dokumenttia
luettiin palautettujen saamiseksi:

```{.python tiedosto="esimerkit/luku05/indeksit.py" osa="explain"}
```

Yhdistelmäindeksi kaupungin ja summan mukaan muuttaa haun
indeksihauksi (*IXSCAN*), joka lukee vain osuvat dokumentit.

Yhdistelmäindeksin kenttien järjestykselle on MongoDB:ssä nyrkkisääntö
*ESR*: ensin yhtäsuuruusehdot (*equality*), sitten järjestys (*sort*),
sitten väliehdot (*range*). Seuraava kysely suodattaa kaupungin
yhtäsuuruudella ja päivän välillä ja järjestää summan mukaan:

```{.python tiedosto="esimerkit/luku05/indeksit.py" osa="esr"}
```

```{.tuloste tiedosto="esimerkit/luku05/indeksit.odotettu"}
```

Ensimmäinen indeksi (kaupunki, summa) antoi järjestyksen valmiina,
mutta päivän ehto tarkistettiin vasta dokumentista: 2000 luettua,
334 palautettua. Kun päivä lisättiin indeksin loppuun, ehto
tarkistetaan indeksistä, ja vain palautettavat dokumentit luetaan.
Sama periaate pätee relaatiotietokantojen yhdistelmäindekseihin.

Indeksin voi tehdä myös taulukon alkioille (*multikey*), tekstille
ja paikkatiedolle. Jokainen indeksi hidastaa kirjoituksia ja vie
muistia, joten indeksit valitaan todellisten kyselyjen mukaan.

## Käytännössä

- Mallinna dokumentit sen mukaan, mitä luetaan yhdessä. Kirjoita
  sovelluksen tärkeimmät kyselyt ylös ennen mallia.
- Upota pientä ja muuttumatonta, viittaa suureen ja jaettuun. Älä
  anna taulukoiden kasvaa rajatta dokumentin sisällä.
- Käytä päivitysoperaattoreita (`$set`, `$inc`, `$push`). Koko
  dokumentin lukeminen ja takaisin kirjoittaminen kadottaa
  samanaikaiset päivitykset.
- Anna `_id` itse, kun luonnollinen tunniste on olemassa; se on ilmainen
  yksilöllinen indeksi.
- Tarkista tärkeiden kyselyjen `explain()` ja järjestä
  yhdistelmäindeksin kentät ESR-säännön mukaan.

## Itsearviointi

- Osaat lisätä, hakea ja päivittää dokumentteja MongoDB:ssä ja käyttää
  sisäkkäisiä kenttiä ehdoissa.
- Osaat perustella, upotetaanko tieto vai viitataanko siihen.
- Osaat lukea `explain()`-tuloksesta, käytettiinkö indeksiä ja kuinka
  paljon turhaa luettiin.
- Osaat järjestää yhdistelmäindeksin kentät ESR-säännön mukaan.
