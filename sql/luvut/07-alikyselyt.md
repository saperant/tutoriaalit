# Alikyselyt, CTE:t ja näkymät

Kyselyn tulos on taulu, joten sitä voi käyttää toisen kyselyn osana.
Tämä luku käsittelee neljä tapaa koota kyselyitä osista: alikyselyt,
joukko-operaatiot, yhteiset taulukkolausekkeet (*common table
expression*, CTE) ja näkymät. Alikyselyitä on jo käytetty ehdoissa
`IN` ja `EXISTS` (luvut 4 ja 5); nyt ne käydään läpi järjestyksessä.

## Alikyselyt

*Skalaarialikysely* palauttaa yhden arvon ja käy minkä tahansa
lausekkeen paikalle:

```{.sql tiedosto="esimerkit/07-alikyselyt.sql" osa="skalaari"}
```

*Korreloitu* alikysely viittaa ulomman kyselyn riviin ja lasketaan
loogisesti jokaiselle riville erikseen:

```{.sql tiedosto="esimerkit/07-alikyselyt.sql" osa="korreloitu"}
```

```{.tuloste tiedosto="esimerkit/07-alikyselyt.odotettu"}
```

Sarin viimeisin tilaus on NULL, joka näkyy tyhjänä. Korreloitu
alikysely on luettava ja oikein, mutta sen hinta riippuu indeksistä:
ilman indeksiä sarakkeella `tilaus.asiakas_id` jokainen asiakas käy koko
tilaustaulun läpi. Sama tulos saadaan liitoksella ja ryhmittelyllä, ja
optimoija muuttaa usein alikyselyn liitokseksi itse.

Alikysely käy myös `FROM`-osaan taulun paikalle, jolloin sitä
kutsutaan *johdetuksi tauluksi*.

## Joukko-operaatiot

Kahden kyselyn tulokset voi yhdistää joukkoina, kun niissä on yhtä
monta saraketta ja tyypit sopivat yhteen. `UNION` on yhdiste,
`INTERSECT` leikkaus ja `EXCEPT` erotus. Sarakkeiden nimet tulevat
ensimmäisestä kyselystä, ja `ORDER BY` koskee koko tulosta:

```{.sql tiedosto="esimerkit/07-joukot.sql" osa="union"}
```

```{.sql tiedosto="esimerkit/07-joukot.sql" osa="intersect"}
```

```{.sql tiedosto="esimerkit/07-joukot.sql" osa="except"}
```

Joukko-operaatiot poistavat toistot, koska tulos on joukko. `UNION
ALL` säilyttää kaikki rivit eikä siksi tarvitse järjestämistä tai
hajautusta toistojen etsimiseen:

```{.sql tiedosto="esimerkit/07-joukot.sql" osa="all"}
```

```{.tuloste tiedosto="esimerkit/07-joukot.odotettu"}
```

Asiakkailla on kolme eri kaupunkia ja yksi NULL. Toisin kuin
vertailussa (luku 4), joukko-operaatioissa, `DISTINCT`-määreessä ja
ryhmittelyssä kaksi NULLia ovat *sama* arvo. Leikkauksen ja erotuksen
voi kirjoittaa myös `EXISTS`- ja `NOT EXISTS` -ehdoilla; joukkomuoto on
luettavampi, kun verrataan kokonaisia rivejä. Oraclessa `EXCEPT` on
nimeltään `MINUS`.

## CTE: kysely vaiheittain

`WITH` nimeää välitulokset ja jakaa monimutkaisen kyselyn vaiheisiin,
jotka luetaan ylhäältä alas:

```{.sql tiedosto="esimerkit/07-cte.sql" osa="cte"}
```

```{.tuloste tiedosto="esimerkit/07-cte.odotettu"}
```

Jokainen vaihe on yksinään ymmärrettävä ja testattava: vaiheen voi ajaa
erikseen vaihtamalla viimeisen `SELECT`-lauseen. Vaiheistus on myös
luvun 5 moninkertaistumisongelman ratkaisu: kukin kooste lasketaan omalla
tasollaan.

CTE ei ole automaattisesti välitaulu. PostgreSQL 12+ ja SQLite
sisällyttävät kertaalleen käytetyn CTE:n pääkyselyyn, jolloin
optimoija näkee koko kyselyn. Laskennan voi pakottaa kertaalleen
määreellä `AS MATERIALIZED`, kun CTE:tä käytetään monesti.

## Rekursiiviset kyselyt

Rekursiivinen CTE käsittelee hierarkioita ja verkkoja, joiden syvyyttä
ei tiedetä etukäteen. Kategoriapuussa jokainen kategoria viittaa
ylempään:

```{.sql tiedosto="esimerkit/07-rekursio.sql" osa="taulu"}
```

Kysely koostuu *ankkurista*, joka antaa aloitusrivit, ja *rekursiivisesta
osasta*, joka liittää edellisen kierroksen rivit tauluun. Kierroksia
jatketaan, kunnes uusia rivejä ei synny:

```{.sql tiedosto="esimerkit/07-rekursio.sql" osa="rekursio"}
```

```{.tuloste tiedosto="esimerkit/07-rekursio.odotettu"}
```

Reitti on samalla järjestysavain, joka tulostaa puun syvyyssuunnassa.
Jos tieto voi sisältää silmukan (A → B → A), rekursio ei pääty.
Suojaksi käytetään syvyysrajaa (`WHERE p.taso < 20`), `UNION`-operaattoria
`UNION ALL` -operaattorin sijaan tai PostgreSQL:n `CYCLE`-määrettä.

Rekursio tuottaa myös sarjoja. Raportissa päivät, joina ei ole
tilauksia, katoavat helposti; päiväsarjaan liittäminen tuo ne
näkyviin:

```{.sql tiedosto="esimerkit/07-sarja.sql" osa="sarja"}
```

```{.tuloste tiedosto="esimerkit/07-sarja.odotettu"}
```

PostgreSQL:ssä sarja tehdään funktiolla `generate_series`.

## Näkymät

Näkymä on tietokantaan tallennettu nimetty kysely. Se ei tallenna
dataa, vaan kysely suoritetaan joka kerta:

```{.sql tiedosto="esimerkit/07-nakymat.sql" osa="nakyma"}
```

```{.tuloste tiedosto="esimerkit/07-nakymat.odotettu"}
```

Näkymä antaa toistuvalle laskulle yhden määritelmän ja voi toimia
rajapintana: sovellukselle annetaan oikeus näkymään mutta ei tauluihin,
ja taulujen rakennetta voi muuttaa näkymän pysyessä samana.
PostgreSQL:n *materialisoitu näkymä* tallentaa tuloksen, ja se
päivitetään komennolla `REFRESH MATERIALIZED VIEW`.

## Käytännössä

- **CTE monivaiheiseen kyselyyn.** Nimetyt vaiheet kertovat aikeen,
  ja jokaisen vaiheen voi tarkistaa erikseen. Sisäkkäiset alikyselyt
  luetaan sisältä ulos, mikä on hankalaa jo kolmella tasolla.
- **`UNION ALL`, kun toistot eivät haittaa tai niitä ei voi olla.**
  `UNION` järjestää tai hajauttaa koko tuloksen toistojen poistamiseksi.
- **`EXISTS` olemassaolon testiin**, liitos, kun tarvitaan toisen
  taulun sarakkeita, ja `IN` lyhyelle vakiolistalle tai alikyselylle,
  joka ei voi palauttaa NULLia.
- **Rekursioon aina päättymisehto**, jos data voi sisältää silmukan.
  Syvät hierarkiat ja suuret verkot kannattaa mitata: rekursio ei voi
  käyttää kaikkia optimointeja.
- **Näkymä yhdeksi totuudeksi.** Laskusääntö, kuten tilauksen summa,
  määritellään yhdessä paikassa. Näkymien ketjuttaminen monikerroksiseksi
  pinoksi tekee kyselysuunnitelmista kuitenkin vaikeita ymmärtää.
- **Hinnat**: korreloitu alikysely maksaa yhden haun ulomman kyselyn
  riviä kohden; indeksin kanssa se on halpa, ilman sitä neliöllinen.
  Tavallinen näkymä ei maksa mitään ylimääräistä, koska se avataan osaksi
  kyselyä. Materialisoitu näkymä on nopea lukea mutta vanhenee.

## Itsearviointi

- Osaat kirjoittaa skalaari- ja korreloidun alikyselyn ja arvioida sen
  hinnan indeksin kanssa ja ilman.
- Osaat yhdistää kyselyjen tuloksia operaatioilla `UNION`,
  `INTERSECT` ja `EXCEPT` ja valita `UNION`- ja `UNION ALL` -muodon
  välillä.
- Osaat jakaa monimutkaisen raportin nimettyihin CTE-vaiheisiin.
- Osaat kirjoittaa rekursiivisen kyselyn hierarkialle ja päiväsarjalle
  ja suojata sen silmukoilta.
- Osaat perustella, milloin näkymä on hyvä rajapinta ja milloin
  materialisoitu näkymä on tarpeen.
