# Kyselyt

`SELECT`-lause kuvaa tulostaulun: mistä riveistä se muodostetaan, mitkä
rivit hyväksytään ja mitä sarakkeita lasketaan. Tämä luku käsittelee
yhden taulun kyselyt; liitokset ovat luvussa 5 ja koosteet luvussa 6.

## Suoritusjärjestys

Lauseen osat kirjoitetaan eri järjestyksessä kuin ne loogisesti
suoritetaan. Looginen järjestys selittää, mihin kukin osa voi viitata:

```{.dot otsikko="SELECT-lauseen looginen suoritusjärjestys. Kukin vaihe saa edellisen vaiheen tuloksen."}
digraph {
  rankdir=TB; nodesep=0.25; ranksep=0.45;
  node [width=1.25, height=0.55, fixedsize=true, fontsize=9];
  f [label="FROM, JOIN\nlähderivit"];
  w [label="WHERE\nrivien suodatus"];
  g [label="GROUP BY\nryhmittely"];
  h [label="HAVING\nryhmien suodatus"];
  s [label="SELECT\nsarakkeet, ikkunat"];
  d [label="DISTINCT\ntoistojen poisto"];
  o [label="ORDER BY\njärjestys"];
  l [label="LIMIT, OFFSET\nrivien rajaus"];
  { rank=same; f -> w -> g -> h; }
  { rank=same; s -> d -> o -> l; }
  h -> s [constraint=false];
  f -> s [style=invis];
}
```

Kukin vaihe näkee vain sen, mitä aiemmat vaiheet ovat tuottaneet.
`GROUP BY`, `HAVING` ja ikkunafunktiot esitellään luvuissa 6 ja 8;
tässä luvussa käytetään vaiheita `FROM`, `WHERE`, `SELECT`,
`ORDER BY` ja `LIMIT`.

Siksi `SELECT`-osan alias ei standardin mukaan näy `WHERE`-ehdossa
mutta näkyy `ORDER BY` -osassa. SQLite sallii aliaksen myös
`WHERE`-ehdossa, PostgreSQL ei; siirrettävä koodi ei käytä sitä.
Optimoija saa suorittaa kyselyn missä järjestyksessä tahansa, kunhan
tulos on sama.

## Suodatus, lausekkeet ja järjestys

```{.sql tiedosto="esimerkit/03-select.sql" osa="perus"}
```

- `IN (...)` on lyhenne `OR`-ketjulle.
- Jakaja `100.0` tekee jakolaskusta liukulukujaon. `899 / 100` on
  kokonaislukujakona 8 sekä SQLitessä että PostgreSQL:ssä.
- Merkkijonot ovat yksinkertaisissa lainausmerkeissä. Kaksinkertaiset
  lainausmerkit rajaavat *tunnisteita*, kuten sarakkeiden nimiä.
- `printf` on SQLiten muotoilufunktio; PostgreSQL:ssä vastaava on
  `to_char` tai `format`.

`CASE` luokittelee rivejä. Haarat käydään järjestyksessä ja ensimmäinen
tosi haara valitaan:

```{.sql tiedosto="esimerkit/03-select.sql" osa="case"}
```

```{.tuloste tiedosto="esimerkit/03-select.odotettu"}
```

`LIMIT` ilman `ORDER BY` -lausetta palauttaa mielivaltaiset rivit.
Sivutuksesta ja sen hinnasta kerrotaan luvussa 11.

## Päivämäärät ja ajat

SQLitessä päivämäärät tallennetaan ISO 8601 -tekstinä, ja
funktiot `date`, `datetime`, `strftime` ja `julianday` laskevat niillä.
Koska muoto `VVVV-KK-PP` järjestyy aakkosjärjestyksessä oikein,
vertailut ja välit toimivat suoraan merkkijonoina.

```{.sql tiedosto="esimerkit/03-paivamaarat.sql" osa="paivat"}
```

Ehto on *puoliavoin väli* `>= alku AND < loppu`. Se toimii samoin
päivämäärille ja aikaleimoille: väli `paiva <= '2026-10-31'` jättäisi
aikaleiman `2026-10-31 14:00` pois, koska se on merkkijonona suurempi.

Muunnokset annetaan funktioille muuntimina:

```{.sql tiedosto="esimerkit/03-paivamaarat.sql" osa="lisays"}
```

```{.tuloste tiedosto="esimerkit/03-paivamaarat.odotettu"}
```

PostgreSQL:ssä samat laskut tehdään tyypeillä: `date '2026-11-20' -
interval '30 days'`, `date_trunc('month', ...)` ja vähennyslasku, joka
palauttaa päivien määrän. Esimerkeissä käytetään kiinteää päivää
`2026-11-20`, jotta tulosteet pysyvät samoina. Oikeassa koodissa nykyhetki
on `date('now')` tai PostgreSQL:ssä `current_date`.

## Käytännössä

- **`ORDER BY` aina, kun järjestyksellä on väliä.** Ilman sitä
  järjestys riippuu suoritustavasta ja voi muuttua, kun data kasvaa tai
  indeksi lisätään. Järjestyksen on oltava yksikäsitteinen, jos sitä
  käytetään sivutukseen: lisää lopuksi pääavain.
- **Puoliavoimet välit** päivämäärille ja aikaleimoille. Ne liittyvät
  toisiinsa aukotta ja päällekkäisyydettä, ja ne voivat käyttää
  indeksiä.
- **Sarake vertailun toiselle puolelle sellaisenaan.** Ehto
  `strftime('%Y', paiva) = '2026'` laskee funktion jokaiselle riville
  eikä voi käyttää indeksiä; `paiva >= '2026-01-01' AND paiva <
  '2027-01-01'` voi (luku 11).
- **Nimetyt sarakkeet, ei `SELECT *`** sovelluksen kyselyissä. Kysely
  kertoo, mitä se tarvitsee, ei rikkoudu sarakkeen lisäämisestä eikä
  siirrä turhaa dataa. Interaktiivisessa tutkimisessa `*` on kätevä.
- **Muotoilu kuuluu sovellukseen.** Tietokanta palauttaa luvut ja
  päivämäärät koneluettavina; valuuttamerkit, desimaalipilkku ja
  aikavyöhykkeet lisätään käyttöliittymässä. Esimerkkien `printf` on
  tässä luettavuuden vuoksi.
- **Yhtenäinen tyyli**: avainsanat isolla, yksi tulossarake riville,
  aliakset `AS`-sanalla. Tyyliä voi valvoa työkalulla, kuten SQLFluff.

## Itsearviointi

- Osaat kertoa `SELECT`-lauseen loogisen suoritusjärjestyksen ja
  selittää sen avulla, miksi alias ei näy `WHERE`-ehdossa.
- Osaat suodattaa aikavälin puoliavoimella ehdolla ja laskea
  päivämäärillä SQLiten funktioilla.
- Osaat luokitella rivejä `CASE`-lausekkeella ja välttää
  kokonaislukujaon yllätykset.
- Osaat perustella, miksi `ORDER BY` tarvitaan aina, kun järjestys
  merkitsee.
