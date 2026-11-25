# Liitokset

Normalisoitu tieto on monessa taulussa, ja liitos (*join*) yhdistää ne
kyselyssä takaisin. Liitos muodostaa loogisesti kaikki rivien parit ja
pitää ne, joille liitosehto on tosi. Optimoija toteuttaa sen
tehokkaammin, yleensä indeksin avulla. Kuvassa luvun 2 asiakkaat ja
tilaukset on yhdistetty ehdolla `tilaus.asiakas_id = asiakas.id`:

```{.dot otsikko="Liitos asiakkaiden ja tilausten välillä. Sisäliitos tuottaa rivin jokaisesta yhtenäisestä viivasta (kuusi riviä); ulkoliitos lisää parittoman asiakkaan NULL-arvoin."}
digraph {
  rankdir=LR; nodesep=0.12; ranksep=1.6;
  node [fontsize=9, height=0.3];
  edge [arrowhead=none];
  subgraph cluster_a { label="asiakas"; fontsize=10; color="#D9E0E3";
    a1 [label="1 Aino"]; a2 [label="2 Matti"]; a3 [label="3 Liisa"];
    a4 [label="4 Juha"]; a5 [label="5 Sari"]; }
  subgraph cluster_t { label="tilaus (id, asiakas_id)"; fontsize=10; color="#D9E0E3";
    t1 [label="1, asiakas 1"]; t2 [label="2, asiakas 1"];
    t3 [label="3, asiakas 2"]; t6 [label="6, asiakas 2"];
    t4 [label="4, asiakas 3"]; t5 [label="5, asiakas 4"];
    n [label="NULL", style="rounded,dashed", fillcolor="white"]; }
  a1 -> t1; a1 -> t2; a2 -> t3; a2 -> t6; a3 -> t4; a4 -> t5;
  a5 -> n [style=dashed, label="vain LEFT JOIN", fontsize=8];
}
```

## Sisä- ja ulkoliitos

Sisäliitos (`JOIN` eli `INNER JOIN`) palauttaa vain rivit, joille
löytyy pari:

```{.sql tiedosto="esimerkit/05-liitokset.sql" osa="inner"}
```

Ulkoliitos (`LEFT JOIN`) säilyttää vasemman taulun kaikki rivit. Jos
paria ei löydy, oikean taulun sarakkeet ovat NULL:

```{.sql tiedosto="esimerkit/05-liitokset.sql" osa="left"}
```

```{.tuloste tiedosto="esimerkit/05-liitokset.odotettu"}
```

Sari Laineella ei ole tilauksia, ja hän näkyy silti. Laskuri on
`count(t.id)` eikä `count(*)`: jälkimmäinen laskisi myös NULL-rivin ja
antaisi Sarille yhden tilauksen.

Ulkoliitoksen tavallisin virhe on oikean taulun ehto `WHERE`-osassa.
Ehto `WHERE t.paiva >= '2026-11-01'` hylkää NULL-rivit ja muuttaa
liitoksen käytännössä sisäliitokseksi. Ehto, jonka on tarkoitus rajata
vain liitettäviä rivejä, kuuluu `ON`-osaan:
`LEFT JOIN tilaus AS t ON t.asiakas_id = a.id AND t.paiva >= ...`.

SQLite 3.39+ tukee myös liitoksia `RIGHT JOIN` ja `FULL JOIN`.
`RIGHT JOIN` kirjoitetaan yleensä `LEFT JOIN` -muotoon vaihtamalla
taulujen järjestys, koska koko kyselyn lukeminen vasemmalta oikealle on
helpompaa.

## Semi- ja anti-liitos

Usein kysytään, *onko* rivillä pari, eikä tarvita parin tietoja.
`EXISTS` ilmaisee tämän suoraan eikä monista rivejä:

```{.sql tiedosto="esimerkit/05-anti.sql" osa="anti"}
```

```{.sql tiedosto="esimerkit/05-anti.sql" osa="semi"}
```

```{.tuloste tiedosto="esimerkit/05-anti.odotettu"}
```

Kahvia tilattiin Helsinkiin kahdesti, mutta se näkyy kerran. Sama
tavallisella liitoksella vaatisi `DISTINCT`-sanan, joka peittää
monistumisen eikä kerro aikeesta mitään.

## Itseliitos

Taulu voidaan liittää itseensä, kun rivi viittaa toiseen samanlaiseen
riviin. Aliakset erottavat roolit:

```{.sql tiedosto="esimerkit/05-itseliitos.sql" osa="taulu"}
```

```{.sql tiedosto="esimerkit/05-itseliitos.sql" osa="kysely"}
```

```{.tuloste tiedosto="esimerkit/05-itseliitos.odotettu"}
```

Itseliitos hakee yhden tason. Koko hierarkia, kuten kaikki Kaisan
alaiset, haetaan rekursiivisella kyselyllä (luku 7).

## Rivien moninkertaistuminen

Kun tauluun liitetään kaksi eri 1–N-yhteyttä, jokainen vasemman puolen
rivi parittuu jokaisen oikean puolen rivin kanssa. Lisätään malliin
maksut:

```{.sql tiedosto="esimerkit/05-moninkertaistuminen.sql" osa="maksu"}
```

```{.sql tiedosto="esimerkit/05-moninkertaistuminen.sql" osa="vaarin"}
```

Tilauksella 3 on kolme riviä ja kaksi maksua, joten liitos tuottaa
kuusi riviä, ja molemmat summat kertautuvat:

```{.tuloste tiedosto="esimerkit/05-moninkertaistuminen.odotettu"}
```

Ensimmäinen taulu on väärin: tilauksessa 3 on 5 kappaletta ja maksuja
84,46 euroa. Virhe on vaarallinen, koska kysely toimii ja luvut
näyttävät uskottavilta. Korjaus on koota kumpikin 1–N-puoli ensin
omaksi tulokseksi ja liittää vasta yhden rivin tilauskohtaiset
tulokset (toinen taulu):

```{.sql tiedosto="esimerkit/05-moninkertaistuminen.sql" osa="oikein"}
```

`WITH`-rakenne (CTE) esitellään luvussa 7. `USING (tilaus_id)` on
lyhenne ehdolle `ON r.tilaus_id = m.tilaus_id`.

## Käytännössä

- **Eksplisiittinen `JOIN ... ON`.** Vanha muoto `FROM a, b WHERE
  a.id = b.a_id` sekoittaa liitosehdot ja suodatusehdot, ja unohtunut
  ehto tuottaa huomaamatta karteesisen tulon.
- **Lyhyet, merkitykselliset aliakset** (`a`, `t`, `tu`) ja jokainen
  sarake aliaksen kanssa, kun kyselyssä on useampi taulu. Kysely ei
  rikkoudu, kun toiseen tauluun lisätään samanniminen sarake.
- **Tarkista rivimäärä.** Jokaisen 1–N-liitoksen jälkeen pitää tietää,
  minkä tason rivejä tulos sisältää (asiakas, tilaus vai tilausrivi).
  Kahta rinnakkaista 1–N-liitosta ei koota samassa vaiheessa.
- **`DISTINCT` ei ole korjaus.** Jos tulokseen ilmestyy toistoja,
  liitos on yleensä väärä tai semi-liitos on kirjoitettu tavallisena
  liitoksena.
- **Hinnat**: liitos viiteavaimella on halpa, kun liitettävän taulun
  sarakkeella on indeksi: jokainen haku maksaa O(log n). Pääavaimella
  on indeksi aina, mutta *viiteavainsarakkeella ei automaattisesti*
  SQLitessä eikä PostgreSQL:ssä. Ilman indeksiä SQLite rakentaa
  kyselyn ajaksi väliaikaisen indeksin (*automatic index*) ja
  PostgreSQL valitsee hajautus- tai lomitusliitoksen; molemmat käyvät
  koko taulun läpi.

## Itsearviointi

- Osaat valita sisäliitoksen, ulkoliitoksen, semi-liitoksen ja
  anti-liitoksen kysymyksen mukaan.
- Osaat selittää, miksi oikean taulun ehto `WHERE`-osassa muuttaa
  ulkoliitoksen sisäliitokseksi, ja siirtää ehdon `ON`-osaan.
- Osaat tunnistaa rivien moninkertaistumisen ja korjata sen kokoamalla
  1–N-yhteydet ennen liitosta.
- Osaat kirjoittaa itseliitoksen aliaksilla.
