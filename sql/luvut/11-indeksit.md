# Indeksit ja suorituskyky

Tähän asti kyselyiltä on vaadittu vain oikeaa tulosta. Kun rivejä on
satoja tuhansia, ratkaisee myös se, miten tietokanta tuloksen löytää.
Ilman indeksiä se löytää ehdon täyttävät rivit vain käymällä koko
taulun läpi. Indeksi on erillinen, järjestetty tietorakenne (yleensä
B-puu), joka sisältää indeksoidut sarakkeet ja viittauksen riviin. Haku
indeksistä maksaa O(log n): sadasta tuhannesta rivistä löydetään oikea
muutamalla sivun luvulla.

```{.dot otsikko="B-puuindeksi sarakkeelle asiakas_id. Haku etenee juuresta lehteen, ja lehti kertoo, mistä taulun rivit löytyvät. Lehdet on linkitetty, joten väli luetaan seuraamalla linkkejä."}
digraph {
  rankdir=TB; nodesep=0.3; ranksep=0.5;
  node [fontsize=9];
  juuri [label="juuri: asiakas_id\n< 700  |  700–1399  |  ≥ 1400"];
  l1 [label="lehti\n…  41  42  42  42  43  …"];
  l2 [label="lehti\n700  700  701  …"];
  l3 [label="lehti\n1400  1401  …"];
  taulu [label="taulun rivit (pääavaimen mukaan)\n…  rivi 17  …  rivi 5311  …  rivi 90210  …", width=4.6];
  juuri -> l1 [penwidth=1.8, label="  42 < 700"];
  juuri -> l2; juuri -> l3;
  { rank=same; l1 -> l2 -> l3 [style=dashed, arrowsize=0.5]; }
  l1 -> taulu [penwidth=1.8, label="  asiakkaan 42 rivien tunnisteet"];
}
```

Puu on matala, koska jokaisessa solmussa on satoja avaimia: kolme
tasoa riittää miljooniin riveihin. Koska avaimet ovat järjestyksessä,
sama rakenne palvelee yhtäsuuruutta (`asiakas_id = 42`), välejä
(`paiva >= ...`) ja järjestämistä (`ORDER BY`). B-puun toteutus on
taidossa *Edistyneet algoritmit ja tietorakenteet*.

Luvun esimerkit luovat taulun, jossa on 100 000 tilausta 2 000
asiakkaalle:

```{.sql tiedosto="esimerkit/11-explain.sql" osa="data"}
```

`ANALYZE` kerää tilastot arvojen jakaumasta, ja optimoija käyttää niitä
suunnitelman valintaan.

## Kyselysuunnitelma

`EXPLAIN QUERY PLAN` näyttää, miten SQLite aikoo suorittaa kyselyn.
Ilman indeksiä tulos on `SCAN`, koko taulun läpikäynti:

```{.sql tiedosto="esimerkit/11-explain.sql" osa="ennen"}
```

Indeksin jälkeen suunnitelma on `SEARCH`, haku indeksistä:

```{.sql tiedosto="esimerkit/11-explain.sql" osa="jalkeen"}
```

Indeksi auttaa vain, jos ehto kohdistuu sarakkeeseen sellaisenaan.
Sarakkeeseen kohdistuva funktio piilottaa arvon indeksiltä:

```{.sql tiedosto="esimerkit/11-explain.sql" osa="funktio"}
```

```{.tuloste tiedosto="esimerkit/11-explain.odotettu"}
```

Kolmas suunnitelma käy läpi koko indeksin (`SCAN ... USING COVERING
INDEX`) ja laskee funktion jokaiselle riville. Neljäs hakee vain välin
(`SEARCH ... paiva>? AND paiva<?`). Indeksiä käyttävää ehtoa kutsutaan
englanniksi termillä *sargable*. Jos funktiota ei voi välttää, sille voi
tehdä *lausekeindeksin*: `CREATE INDEX ... ON tilaus (strftime('%m',
paiva))`.

PostgreSQL:ssä vastaava komento on `EXPLAIN`, ja `EXPLAIN ANALYZE`
myös suorittaa kyselyn ja näyttää todelliset rivimäärät ja ajat.

## Yhdistelmäindeksi ja kattava indeksi

Yhdistelmäindeksi järjestää rivit ensin ensimmäisen sarakkeen ja sen
sisällä seuraavan mukaan, kuten puhelinluettelo sukunimen ja etunimen
mukaan. Sitä voi käyttää, kun ehto koskee sarakkeita vasemmalta alkaen
(*vasemman etuliitteen sääntö*):

```{.sql tiedosto="esimerkit/11-yhdistelma.sql" osa="yhdistelma"}
```

Ensimmäinen kysely hakee yhdellä haulla asiakkaan 42 rivit kesäkuusta
alkaen. Toisessa ehto koskee vain toista saraketta. SQLite käyttää
silti indeksiä *skip scan* -tekniikalla, koska tilastojen mukaan
asiakkaita on vähän: se tekee erillisen haun jokaiselle
`asiakas_id`:n arvolle, eli 2 000 hakua. Se on parempi kuin taulun
läpikäynti mutta selvästi huonompi kuin oma indeksi sarakkeelle `paiva`.

Kun kaikki kyselyn tarvitsemat sarakkeet ovat indeksissä, taulua ei
tarvitse lukea lainkaan (*kattava indeksi*). Tässä `SELECT *` maksaa:

```{.sql tiedosto="esimerkit/11-yhdistelma.sql" osa="kattava"}
```

```{.tuloste tiedosto="esimerkit/11-yhdistelma.odotettu"}
```

`SELECT *` hakee jokaiselle osumalle rivin taulusta, kun nimetyt
sarakkeet saadaan suoraan indeksistä. Molemmissa järjestys tulee
indeksistä ilman erillistä järjestämistä. PostgreSQL:ssä kattavuutta
voi lisätä määreellä `INCLUDE (sarake)`.

## Liitoksen suunnitelma

Usean taulun kyselyssä optimoija valitsee myös *liitosjärjestyksen* ja
*liitosalgoritmin*. SQLite käyttää aina sisäkkäisiä silmukoita
(*nested loop*): ulompi taulu käydään läpi, ja jokaiselle sen riville
haetaan sisemmän taulun osumat indeksistä. Kolmen taulun kysely:

```{.sql tiedosto="esimerkit/11-liitossuunnitelma.sql" osa="kysely"}
```

Suunnitelman askeleet luetaan ylhäältä alas ulommasta silmukasta
sisimpään. Sama kuvana, tuotettuna suoraan suunnitelman tulosteesta:

```{.dot tiedosto="kaaviot/11-liitossuunnitelma.dot" otsikko="Kolmen taulun liitos sisäkkäisinä silmukoina: asiakkaat käydään läpi, kunkin tilaukset haetaan indeksistä ja kunkin tilauksen rivit pääavaimen indeksistä. Tulos järjestetään lopuksi."}
```

Ulommaksi valittiin `asiakas`, koska ehto `kaupunki = ...` rajaa sen
sataan riviin, ja sisemmille tauluille on indeksit liitossarakkeilla.
Ilman indeksiä `tilaus (asiakas_id)` sisempi silmukka kävisi jokaisen
asiakkaan kohdalla koko tilaustaulun läpi. Viimeinen askel, `USE TEMP
B-TREE FOR ORDER BY`, on erillinen järjestäminen: summan mukaista
järjestystä ei saa mistään indeksistä.

PostgreSQL ja MariaDB tuntevat sisäkkäisten silmukoiden lisäksi
*hajautusliitoksen* (*hash join*: pienemmästä taulusta rakennetaan
hajautustaulu, ja toinen käydään kerran läpi) ja *lomitusliitoksen*
(*merge join*: kaksi valmiiksi järjestettyä syötettä lomitetaan).
Sisäkkäiset silmukat ovat parhaat, kun ulompia rivejä on vähän ja
sisemmällä on indeksi; hajautusliitos, kun liitetään suuria joukkoja
kokonaan. Optimoija valitsee näiden välillä tilastojen perusteella,
minkä vuoksi vanhentuneet tilastot (`ANALYZE`) tuottavat huonoja
suunnitelmia.

## Osittainen indeksi

Kun haetaan harvinaista arvoa, kuten avoimia tilauksia, riittää
indeksoida vain ne rivit:

```{.sql tiedosto="esimerkit/11-osittainen.sql" osa="osittainen"}
```

```{.tuloste tiedosto="esimerkit/11-osittainen.odotettu"}
```

Indeksissä on 2 000 riviä 100 000:n sijaan. Se on pieni, ja
kirjoituksen hinta koskee vain avoimia tilauksia. Osittainen
yksikäsitteinen indeksi ilmaisee myös sääntöjä, kuten "asiakkaalla on
enintään yksi oletusosoite".

## Sivutus: OFFSET vai avain

Sivutus `LIMIT ... OFFSET` on yksinkertainen, mutta tietokannan on
käytävä läpi ja hylättävä kaikki ohitettavat rivit:

```{.sql tiedosto="esimerkit/11-sivutus.sql" osa="offset"}
```

*Avainsivutus* (*keyset pagination*) jatkaa edellisen sivun viimeisestä
rivistä. Järjestysavaimen on oltava yksikäsitteinen, siksi mukana on
`id`:

```{.sql tiedosto="esimerkit/11-sivutus.sql" osa="avain"}
```

```{.sql tiedosto="esimerkit/11-sivutus.sql" osa="suunnitelma"}
```

```{.tuloste tiedosto="esimerkit/11-sivutus.odotettu"}
```

Tulos on sama, mutta avainsivutus hakee indeksistä suoraan oikean
kohdan, joten jokainen sivu maksaa saman. OFFSET-sivun hinta kasvaa
lineaarisesti sivunumeron mukana. Lisäksi OFFSET-sivutus näyttää rivin
kahdesti tai ohittaa sen, jos edelliselle sivulle lisätään rivi
selaamisen aikana. Avainsivutuksessa ei voi hypätä suoraan sivulle 500,
mikä sopii äärettömään vieritykseen ja rajapintoihin.

## Käytännössä

- **Indeksoi kyselyjen, ei taulujen perusteella.** Indeksi lisätään,
  kun tunnetaan kysely, joka sitä tarvitsee, ja tulos tarkistetaan
  kyselysuunnitelmasta. Tyypilliset kohteet: viiteavaimet, usein
  suodatetut sarakkeet ja järjestysavaimet.
- **Yhdistelmäindeksin sarakejärjestys**: yhtäsuuruusehdot ensin,
  väliehto tai järjestys viimeisenä. Indeksi `(asiakas_id, paiva)`
  palvelee sekä ehtoa `asiakas_id = ?` että ehtoa
  `asiakas_id = ? AND paiva > ?`, joten erillistä indeksiä
  `(asiakas_id)` ei tarvita.
- **Ei funktioita indeksoitujen sarakkeiden ympärille.** Välit
  päivämäärille, lausekeindeksi muulloin. Sama koskee tyyppimuunnoksia:
  tekstisarakkeen vertaaminen lukuun voi estää indeksin käytön.
- **Avainsivutus** suurille tai jatkuvasti kasvaville joukoille,
  OFFSET-sivutus vain pienille ja harvoin muuttuville listoille.
- **Hinnat**: jokainen indeksi hidastaa jokaista lisäystä, poistoa ja
  indeksoitujen sarakkeiden päivitystä sekä vie levytilaa. Kymmenen
  indeksin taulu kirjoittaa jokaisella lisäyksellä yksitoista
  B-puuta. Indeksi, jota mikään kysely ei käytä, on puhdasta kulua;
  PostgreSQL:n `pg_stat_user_indexes` kertoo käyttämättömät.
- **Pienet taulut ja huono valikoivuus.** Muutaman sadan rivin taulun
  läpikäynti on halvempaa kuin indeksihaku, ja sarake, jonka arvo on
  puolessa riveistä sama, ei hyödy tavallisesta indeksistä.
- **Mittaa.** `.timer on` SQLitessä ja `EXPLAIN ANALYZE` PostgreSQL:ssä
  kertovat todellisen hinnan; tuotannon hitaat kyselyt löytyvät
  PostgreSQL:n `pg_stat_statements`-laajennoksella.

## Itsearviointi

- Osaat kuvata B-puuindeksin rakenteen ja selittää, miksi se palvelee
  yhtäsuuruutta, välejä ja järjestystä.
- Osaat lukea `EXPLAIN QUERY PLAN` -tulosteen ja erottaa toisistaan
  taulun läpikäynnin, indeksihaun ja kattavan indeksin.
- Osaat lukea liitoksen suunnitelmasta liitosjärjestyksen ja kertoa,
  milloin sisäkkäiset silmukat ja milloin hajautusliitos on sopiva.
- Osaat suunnitella yhdistelmäindeksin sarakejärjestyksen
  kyselyjen ehtojen perusteella.
- Osaat kirjoittaa ehdon niin, että se voi käyttää indeksiä, ja tehdä
  tarvittaessa lauseke- tai osittaisen indeksin.
- Osaat toteuttaa avainsivutuksen ja perustella sen OFFSET-sivutusta
  vastaan.
- Osaat arvioida indeksin hinnan kirjoituksissa ja tilassa.
