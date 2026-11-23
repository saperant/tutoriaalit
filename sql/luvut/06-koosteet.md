# Koosteet ja ryhmittely

Koostefunktio (`count`, `sum`, `avg`, `min`, `max`) tiivistää monta
riviä yhdeksi arvoksi. `GROUP BY` jakaa rivit ryhmiin, ja koosteet
lasketaan ryhmittäin. Tulos sisältää yhden rivin kutakin ryhmää kohden.

## GROUP BY ja HAVING

Myynti kategorioittain, vain yli 50 euron kategoriat:

```{.sql tiedosto="esimerkit/06-koosteet.sql" osa="ryhmittely"}
```

- `count(DISTINCT r.tilaus_id)` laskee eri tilaukset; tavallinen
  `count` laskisi tilausrivit.
- `WHERE` suodattaa rivejä *ennen* ryhmittelyä, `HAVING` ryhmiä
  *jälkeen* sen. Ehto, joka koskee yksittäisiä rivejä, kuuluu
  `WHERE`-osaan: silloin turhia rivejä ei edes ryhmitellä.
- Summa lasketaan senteissä kokonaislukuina ja muunnetaan euroiksi
  vasta näytettäessä.

Jokaisen tulossarakkeen on oltava ryhmittelyssä tai koosteen sisällä.
PostgreSQL hylkää muut sarakkeet, paitsi jos ne riippuvat ryhmittelyn
pääavaimesta (`GROUP BY a.id` sallii sarakkeen `a.nimi`). SQLite
hyväksyy minkä tahansa sarakkeen ja palauttaa sen arvon jostakin
ryhmän rivistä. Tämä *paljaan sarakkeen* laajennus on kätevä mutta
piilottaa virheitä; siirrettävä koodi ei nojaa siihen.

## Ehdolliset koosteet

`FILTER` rajaa koosteen rivit. Yksi kysely voi laskea monta eri ehdon
mukaista lukua yhdellä läpikäynnillä:

```{.sql tiedosto="esimerkit/06-koosteet.sql" osa="filter"}
```

```{.tuloste tiedosto="esimerkit/06-koosteet.odotettu"}
```

`FILTER` on standardin mukainen, ja se toimii SQLitessä ja
PostgreSQL:ssä. Tietokannoissa, joissa sitä ei ole (MySQL, SQL Server),
sama tehdään muodossa `sum(CASE WHEN ehto THEN 1 ELSE 0 END)`.
Samalla tavalla rivit käännetään sarakkeiksi (*pivot*): kukin sarake on
oma ehdollinen koosteensa.

## Merkkijonojen kokoaminen

`string_agg` yhdistää ryhmän arvot yhdeksi merkkijonoksi. Järjestys
annetaan koosteen sisällä:

```{.sql tiedosto="esimerkit/06-merkkijonokoosteet.sql" osa="string-agg"}
```

```{.tuloste tiedosto="esimerkit/06-merkkijonokoosteet.odotettu"}
```

`string_agg` on PostgreSQL:ssä ja SQLite 3.44:stä alkaen; vanhempi
SQLite tuntee saman nimellä `group_concat`. Sopiva käyttö on raportit ja
näkymät. Sovellukselle tieto palautetaan riveinä, ei merkkijonoon
koottuna.

## Ryhmittelyn laajennukset

PostgreSQL tukee standardin osia `ROLLUP`, `CUBE` ja `GROUPING SETS`,
jotka laskevat välisummat samassa kyselyssä: `GROUP BY ROLLUP
(kategoria, tuote)` tuottaa tuotetason rivit, kategorioiden summat ja
kokonaissumman. SQLitessä niitä ei ole; välisummat tehdään yhdistämällä
kyselyt `UNION ALL` -operaattorilla tai sovelluksessa.

## Käytännössä

- **Suodata ennen ryhmittelyä.** `WHERE` pienentää käsiteltävää
  joukkoa ja voi käyttää indeksiä; `HAVING` vain koosteille.
- **Kokonaisluvut summiin.** Senttien summa on tarkka. Liukulukujen
  summa riippuu laskujärjestyksestä, joten sama raportti voi antaa
  eri tuloksen eri suoritussuunnitelmalla.
- **`avg` ja jakolaskut**: `avg` palauttaa liukuluvun, mutta
  `sum(x) / count(*)` on kokonaislukujako, jos molemmat ovat
  kokonaislukuja. Kerro toinen osapuoli luvulla `1.0` tai muunna
  `CAST`-lausekkeella.
- **Ehdolliset koosteet yhdellä kyselyllä** monen erillisen
  `count`-kyselyn sijaan. Jokainen erillinen kysely käy datan läpi
  uudestaan.
- **Hinnat**: ryhmittely vaatii järjestämisen tai hajautustaulun, eli
  koko suodatetun joukon läpikäynnin. Jos ryhmittelysarakkeella on
  indeksi, rivit saadaan valmiiksi järjestyksessä. Toistuvasti
  laskettava raskas kooste kannattaa tallentaa yhteenvetotauluun tai
  PostgreSQL:n materialisoituun näkymään.
- **Sudenkuoppa: kooste liitoksen jälkeen.** Jos liitos monistaa rivejä
  (luku 5), `sum` ja `count` monistuvat mukana.

## Itsearviointi

- Osaat ryhmitellä ja suodattaa ryhmiä ja selittää `WHERE`- ja
  `HAVING`-osan eron.
- Osaat laskea monta ehdollista koostetta yhdellä kyselyllä
  `FILTER`-määreellä tai `CASE`-lausekkeella.
- Osaat selittää, miksi SQLiten paljaat sarakkeet ovat riski ja miten
  PostgreSQL ne käsittelee.
- Osaat koota merkkijonoja järjestyksessä `string_agg`-funktiolla.
