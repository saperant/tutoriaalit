# Graafitietokannat: Neo4j

Graafitietokannassa yhteydet ovat yhtä tärkeitä kuin itse tiedot.
Data on *solmuja* ja niiden välisiä *suhteita*, ja molemmilla voi olla
ominaisuuksia. Relaatiotietokannassa yhteys syntyy kyselyhetkellä
liitoksella, joka hakee indeksistä; graafitietokannassa suhde on
tallennettu suoraan solmun yhteyteen, joten naapurista naapuriin
siirtyminen ei riipu tietokannan koosta (*index-free adjacency*).

Tämä näkyy kyselyissä, jotka kulkevat monta askelta: ystävien ystävät,
toimitusketjut, riippuvuusverkot, petosrenkaat, reitit ja suositukset.
Relaatiotietokannassa jokainen askel on liitos, ja vaihtelevan
mittainen polku vaatii rekursiivisen kyselyn.

Neo4j on tunnetuin graafitietokanta, ja sen kyselykieli *Cypher* on
pohjana vuonna 2024 julkaistulle ISO-standardille GQL. Muita ovat
esimerkiksi Memgraph, JanusGraph ja Amazon Neptune; PostgreSQLiin
graafikyselyt saa Apache AGE -laajennuksella.

## Solmut ja suhteet

Kaupan asiakkaat seuraavat toisiaan, ja he ostavat tuotteita:

```{.python tiedosto="esimerkit/nosql/verkosto.py" osa="data"}
```

```{.dot otsikko="Seuraamisverkko: kuka seuraa ketä." leveys="55%"}
digraph {
  layout=circo; node [shape=ellipse];
  aino -> eero; eero -> ilona; ilona -> oskari; aino -> maija;
  maija -> oskari; oskari -> pekka; pekka -> aino;
}
```

Ostot ovat toinen suhdetyyppi samassa graafissa: viisi asiakasta osti
keittimen, ja heistä kolme osti myös makuupussin.

Cypherissä solmu kirjoitetaan sulkeisiin ja suhde nuoleksi:
`(a:Kayttaja)-[:SEURAA]->(b:Kayttaja)`. `MERGE` luo solmun tai suhteen,
jos sitä ei vielä ole, ja `UNWIND` käy läpi parametrina annetun
luettelon:

```{.python tiedosto="esimerkit/luku09/graafi.py" osa="luonti"}
```

## Polkukyselyt

Kahden askeleen päässä olevat käyttäjät, joita Aino ei vielä seuraa:

```{.python tiedosto="esimerkit/luku09/graafi.py" osa="kaksi-askelta"}
```

`[:SEURAA*2]` on täsmälleen kahden suhteen polku; `*1..3` olisi yhdestä
kolmeen. Kysely on kuva siitä, mitä etsitään, mikä tekee Cypheristä
luettavaa.

## Suositukset

"Tämän ostaneet ostivat myös" on kahden askeleen kysely tuotteesta
ostajiin ja heistä muihin tuotteisiin:

```{.python tiedosto="esimerkit/luku09/graafi.py" osa="suositus"}
```

## Lyhin polku

`shortestPath` etsii lyhimmän polun leveyshaulla:

```{.python tiedosto="esimerkit/luku09/graafi.py" osa="polku"}
```

```{.tuloste tiedosto="esimerkit/luku09/graafi.odotettu"}
```

## Samat kyselyt SQL:llä

Suositus on SQL:ssä yksi liitos ostotaulun itsensä kanssa:

```{.python tiedosto="esimerkit/luku09/cte.py" osa="suositus"}
```

Vaihtelevan mittainen polku vaatii rekursiivisen CTE:n, jossa polku
kasvatetaan askel kerrallaan ja kehät estetään itse:

```{.python tiedosto="esimerkit/luku09/cte.py" osa="polku"}
```

```{.tuloste tiedosto="esimerkit/luku09/cte.odotettu"}
```

Tulos on sama, ja pienellä datalla PostgreSQL on yhtä nopea. Ero tulee
esiin, kun graafi on suuri ja polut pitkiä: rekursiivinen CTE tuottaa
kaikki polut ennen suodatusta, kun taas graafitietokanta voi lopettaa
haun, kun lyhin polku on löytynyt, ja seuraa suhteita ilman
indeksihakuja. Jos sovelluksessa on muutama graafikysely, PostgreSQL
riittää. Jos graafi on koko sovelluksen ydin, graafitietokanta
kannattaa.

## Graafimallinnus

- Substantiivit ovat solmuja, verbit suhteita: `(kayttaja)-[:OSTI]->(tuote)`.
- Suhteella on aina suunta ja tyyppi, ja sillä voi olla ominaisuuksia
  (ostopäivä, kappalemäärä).
- Tieto, jolla kuljetaan, kannattaa tehdä solmuksi: jos kaupunkia
  käytetään yhdistämään asiakkaita, `(:Kaupunki)` on parempi kuin
  ominaisuus `kaupunki`.
- Hyvin suosittu solmu (*supernode*), kuten kaikkien seuraama julkkis,
  hidastaa sen kautta kulkevia kyselyjä; sille rajataan suhdetyyppejä
  tai suuntia.

## Käytännössä

- Käytä graafitietokantaa, kun sovelluksen tärkeimmät kysymykset ovat
  monen askeleen polkuja. Yksittäisiin suosituksiin riittää SQL.
- Anna Cypherille arvot parametreina (`$nimi`), älä muodosta kyselyä
  merkkijonoista; se estää injektiot ja sallii suunnitelman
  uudelleenkäytön.
- Tee indeksi tai yksilöllisyysrajoite ominaisuudelle, jolla solmut
  haetaan polun aluksi (`CREATE CONSTRAINT ... IS UNIQUE`).
- Rajaa vaihtelevan mittaiset polut (`*1..4`). Rajaton polku voi käydä
  läpi koko graafin.

## Itsearviointi

- Osaat mallintaa datan solmuiksi ja suhteiksi.
- Osaat kirjoittaa Cypher-kyselyn, joka kulkee kiinteän tai vaihtelevan
  määrän askeleita, ja etsiä lyhimmän polun.
- Osaat tehdä saman polkukyselyn SQL:n rekursiivisella CTE:llä.
- Osaat perustella, milloin graafitietokanta kannattaa ja milloin SQL
  riittää.
