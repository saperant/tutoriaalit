# Aikasarjat

Aikasarja on aikaleimattujen mittausten jono: anturien lukemat,
palvelimien metriikat, pörssikurssit, sähkönkulutus tai sovelluksen
tapahtumat. Data on tavallista liiketoimintadataa yksinkertaisempaa,
mutta sitä on paljon, ja sen käyttö on toisenlaista:

- **Vain lisäyksiä.** Mittausta ei päivitetä; uusi arvo on uusi rivi.
- **Kirjoitustahti on korkea ja tasainen**: tuhat anturia kerran
  sekunnissa on 86 miljoonaa riviä vuorokaudessa.
- **Kyselyt rajaavat aikavälin** ja koostavat: keskiarvo viiden
  minuutin väleittäin, viimeisin arvo, muutos edelliseen.
- **Tarkkuutta harvennetaan** iän mukaan (*downsampling*): viikon ajan
  sekuntidata, vuoden ajan tuntikeskiarvot.
- **Säilytysaika** (*retention*) on rajattu, ja vanha data poistetaan
  kokonaisina aikaväleinä.

Luku näyttää ensin, miten aikasarja tallennetaan ja kysellään
tavallisessa relaatiotietokannassa (PostgreSQL), ja sitten, mitä
erikoistuneet aikasarjatietokannat tekevät toisin.

## Aikasarja relaatiotaulussa

Taulun avain on (anturi, aika), jolloin saman anturin rivit ovat
indeksissä aikajärjestyksessä:

```{.sql tiedosto="esimerkit/palvelimet/14-aikasarja.pg" osa="taulu"}
```

Esimerkki lisää kolmen tunnin minuuttidatan kahdelta anturilta;
anturilta b puuttuu 20 minuuttia. Koosteet lasketaan aikaväleittäin
funktiolla `date_bin`, joka pyöristää aikaleiman alaspäin annetun
välin alkuun (`date_trunc` toimii vain kalenteriyksiköillä, kuten
tunneilla):

```{.sql tiedosto="esimerkit/palvelimet/14-aikasarja.pg" osa="kooste"}
```

Liukuva keskiarvo on ikkunafunktio, jonka kehys on viisi riviä
(luku 8):

```{.sql tiedosto="esimerkit/palvelimet/14-aikasarja.pg" osa="liukuva"}
```

Koosteesta puuttuvat ne välit, joilla ei ole yhtään mittausta. Ne
saadaan näkyviin liittämällä mittaukset välien sarjaan, joka tuotetaan
funktiolla `generate_series` (vrt. SQLiten rekursiivinen sarja,
luku 7):

```{.sql tiedosto="esimerkit/palvelimet/14-aikasarja.pg" osa="aukot"}
```

Kunkin anturin viimeisin arvo on yleinen kysely kojelaudoille.
PostgreSQL:n `DISTINCT ON` valitsee kustakin ryhmästä järjestyksen
ensimmäisen rivin; muissa järjestelmissä sama tehdään ikkunafunktiolla
`row_number` (luku 8):

```{.sql tiedosto="esimerkit/palvelimet/14-aikasarja.pg" osa="viimeisin"}
```

```{.tuloste tiedosto="esimerkit/palvelimet/14-aikasarja.pg.odotettu"}
```

## Osiointi ja BRIN-indeksi

Kun taulussa on miljardeja rivejä, kaksi asiaa korostuu: kyselyn on
löydettävä aikaväli lukematta muuta, ja vanhan datan poiston on oltava
halpa. Molempiin auttaa **osiointi aikavälin mukaan**: looginen taulu
koostuu osioista, esimerkiksi yksi kuukautta kohden.

```{.sql tiedosto="esimerkit/palvelimet/14-osiot.pg" osa="osiot"}
```

Esimerkki lisää 90 vuorokautta minuuttidataa. Kysely, joka rajaa
aikaväliä, käy läpi vain ne osiot, joihin väli osuu (*partition
pruning*):

```{.sql tiedosto="esimerkit/palvelimet/14-osiot.pg" osa="karsinta"}
```

Aikasarjan rivit ovat levyllä valmiiksi aikajärjestyksessä, koska ne
lisätään järjestyksessä. Silloin tavallista B-puuta paljon pienempi
**BRIN-indeksi** (*block range index*) riittää: se tallentaa kustakin
sivualueesta vain pienimmän ja suurimman arvon.

```{.sql tiedosto="esimerkit/palvelimet/14-osiot.pg" osa="brin"}
```

Säilytysaika toteutetaan irrottamalla ja poistamalla vanhin osio. Se
on yksi nopea metatietomuutos, kun taas `DELETE` kävisi läpi
miljoonia rivejä ja jättäisi jälkeensä siivottavaa:

```{.sql tiedosto="esimerkit/palvelimet/14-osiot.pg" osa="sailytys"}
```

```{.tuloste tiedosto="esimerkit/palvelimet/14-osiot.pg.odotettu"}
```

Kyselysuunnitelma käy läpi vain marraskuun osion. BRIN-indeksi vie
3 sivua, B-puu 117. Kahden kuukauden rivit jäävät jäljelle.
Tuotannossa osiot luodaan etukäteen ajastetusti, esimerkiksi
laajennuksella pg_partman.

## Aikasarjatietokannat

Erikoistuneet aikasarjatietokannat automatisoivat edellä käsin tehdyt
asiat ja tallentavat datan tiiviimmin.

- **TimescaleDB** on PostgreSQL-laajennus. *Hypertaulu* näyttää
  tavalliselta taululta, mutta jakautuu automaattisesti aikaväleittäin
  osioihin (*chunk*). *Jatkuvat koosteet* (*continuous aggregates*)
  päivittävät aikaväleittäiset koosteet taustalla, ja vanhat osiot
  pakataan sarakemuotoon ja poistetaan säilytysajan mukaan. Kyselykieli
  on tavallinen SQL, ja relaatiotaulut ovat samassa kannassa.
- **InfluxDB** on alusta asti aikasarjoille tehty tietokanta. Piste on
  mittaus (*measurement*), tagit (indeksoidut metatiedot, kuten anturin
  sijainti), kentät (mitatut arvot) ja aikaleima. Kyselykieliä ovat
  InfluxQL ja SQL; versio 2 käytti Flux-kieltä. Säilytysaika asetetaan
  tietokannalle.
- **Prometheus** kerää palvelimien ja sovellusten metriikoita
  hakemalla ne itse (*pull*) ja tallentaa ne omaan TSDB:hensä.
  Kyselykieli PromQL on tehty nopeuksiin ja koosteisiin:
  `rate(http_pyynnot_total[5m])`. Pitkäaikainen tallennus hoidetaan
  erillisillä järjestelmillä (Thanos, Mimir).
- **QuestDB** ja **ClickHouse** ovat sarakepohjaisia tietokantoja,
  joissa SQL:ää on laajennettu aikasarjoille (esim. `SAMPLE BY`,
  `ASOF JOIN`).

### Sarakepohjainen tallennus ja pakkaus

Rivitietokanta tallentaa rivin sarakkeet peräkkäin, aikasarjatietokanta
yleensä sarakkeen arvot peräkkäin. Peräkkäiset aikaleimat ja arvot ovat
lähellä toisiaan, joten niistä tallennetaan vain muutos. Facebookin
Gorilla-artikkelin (2015) menetelmät ovat käytössä esimerkiksi
Prometheuksessa:

- **Aikaleimoista** tallennetaan erojen erot (*delta-of-delta*).
  Tasaisella näytteenotolla ero on aina 60 sekuntia, joten sen muutos on
  nolla, ja nolla koodataan yhdellä bitillä.
- **Liukulukuarvoista** tallennetaan XOR edelliseen. Samat arvot
  maksavat yhden bitin ja lähekkäiset vähän.

```{.python tiedosto="esimerkit/14-pakkaus.py" osa="aikaleimat"}
```

```{.python tiedosto="esimerkit/14-pakkaus.py" osa="arvot"}
```

```{.tuloste tiedosto="esimerkit/14-pakkaus.odotettu"}
```

Aikaleimat pakkautuvat 64 bitistä alle kahteen. Arvot pakkautuvat
huonosti, koska desimaaliluku kuten 20,3 ei ole binäärisenä tarkka, ja
lähekkäisten arvojen bitit eroavat silti paljon (luku *Liukuluvut*
taidossa *Tietokonearitmetiikka*). Kun sama data tallennetaan
kokonaislukuina kymmenyksinä, delta-of-delta-koodi pakkaa senkin alle
kuuteen bittiin. Siksi mittauksen tarkkuus kannattaa kertoa
tietokannalle, esimerkiksi tyypillä `numeric(4,1)` tai skaalattuna
kokonaislukuna.

## Käytännössä

- **Aloita relaatiotietokannasta.** Kymmenet miljoonat rivit ja
  muutaman tuhannen rivin kirjoitukset sekunnissa sujuvat
  PostgreSQL:ltä hyvällä avaimella, osioinnilla ja BRIN-indeksillä.
  Liiketoimintadata ja aikasarjat samassa kannassa yksinkertaistavat
  liitoksia ja varmuuskopiointia.
- **TimescaleDB, kun PostgreSQL ei käsin riitä**: automaattinen
  osiointi, jatkuvat koosteet ja pakkaus samalla SQL:llä.
- **Prometheus metriikoille, ei liiketoimintadatalle.** Se on tehty
  valvontaan; yksittäisen mittauksen katoaminen on siinä hyväksyttyä.
- **Aikaleimat UTC:nä aikavyöhykkeellisellä tyypillä** (luku 13), ja
  aikavälit puoliavoimina `>= alku AND < loppu` (luku 3).
- **Päätä harvennus ja säilytysaika etukäteen.** Ne määräävät
  tallennustilan paremmin kuin mikään pakkaus.
- **Älä pidä tagien arvoina rajattomia joukkoja**, kuten käyttäjä- tai
  pyyntötunnisteita. Jokainen tagiyhdistelmä on oma sarjansa, ja
  sarjojen määrä (*kardinaliteetti*) kaataa aikasarjatietokannan.

## Itsearviointi

- Osaat kuvata aikasarjadatan erityispiirteet ja kertoa, miten ne
  vaikuttavat tallennukseen.
- Osaat koostaa aikasarjan aikaväleittäin, laskea liukuvan keskiarvon ja
  täyttää puuttuvat välit SQL:llä.
- Osaat osioida taulun aikavälin mukaan, käyttää BRIN-indeksiä ja
  toteuttaa säilytysajan osioilla.
- Osaat kertoa, miten TimescaleDB, InfluxDB ja Prometheus eroavat
  relaatiotietokannasta ja toisistaan, ja selittää delta-of-delta- ja
  XOR-pakkauksen periaatteen.
