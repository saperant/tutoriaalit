# Ikkunafunktiot

Ikkunafunktio laskee arvon rivien joukosta kuten kooste, mutta ei
tiivistä rivejä: jokainen rivi säilyy ja saa oman tuloksensa. Sillä
ratkaistaan tehtävät, jotka muuten vaatisivat itseliitoksia tai
sovelluskoodia: sijoitukset, kumulatiiviset summat, liukuvat keskiarvot
ja vertailu edelliseen riviin.

Ikkuna määritellään `OVER`-osassa:

- `PARTITION BY` jakaa rivit ryhmiin, joissa lasku tehdään erikseen
- `ORDER BY` järjestää rivit ryhmän sisällä
- *kehys* (`ROWS BETWEEN ...`) rajaa, mitkä rivit kuhunkin laskuun
  otetaan.

Ikkunafunktiot lasketaan `WHERE`-, `GROUP BY`- ja `HAVING`-vaiheiden
jälkeen (luku 3). Niiden tulokseen ei siksi voi viitata samassa
`WHERE`-ehdossa, vaan kysely kääritään CTE:hen.

## Sijoitus ja top-N ryhmittäin

Kunkin kategorian kallein tuote on klassinen *top-N ryhmittäin*
-tehtävä:

```{.sql tiedosto="esimerkit/08-sijoitus.sql" osa="top-n"}
```

Vaihtamalla ehdon muotoon `nro <= 3` saadaan kolme kalleinta.
Sijoitusfunktiot eroavat tasatilanteissa:

```{.sql tiedosto="esimerkit/08-sijoitus.sql" osa="rank"}
```

```{.tuloste tiedosto="esimerkit/08-sijoitus.odotettu"}
```

`row_number` numeroi rivit aina yksilöllisesti, `rank` antaa tasatuloksille
saman sijan ja jättää aukon, `dense_rank` ei jätä aukkoa. Ikkunafunktion
argumenttina voi olla kooste: `count(t.id)` lasketaan ryhmittelyssä ja
sijoitus sen jälkeen.

Tasatilanteessa `row_number` valitsee rivien järjestyksen
mielivaltaisesti. Jos tuloksen on oltava toistettava, järjestykseen
lisätään yksikäsitteinen sarake: `ORDER BY hinta_snt DESC, id`.

## Kumulatiiviset ja liukuvat laskut

```{.sql tiedosto="esimerkit/08-kumulatiivinen.sql" osa="ikkuna"}
```

```{.tuloste tiedosto="esimerkit/08-kumulatiivinen.odotettu"}
```

- `sum(...) OVER (ORDER BY paiva)` on kumulatiivinen summa.
  Oletuskehys on `RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`:
  samanarvoiset rivit (*vertaisrivit*) lasketaan mukaan yhdessä. Jos
  järjestysavain ei ole yksikäsitteinen, kehykseksi kirjoitetaan
  `ROWS`, jolloin summa kasvaa rivi kerrallaan.
- `ROWS BETWEEN 2 PRECEDING AND CURRENT ROW` on kolmen rivin liukuva
  ikkuna. Ensimmäisillä riveillä ikkunassa on vähemmän rivejä.
- `OVER ()` on koko tulosjoukko: osuus kokonaissummasta ilman erillistä
  alikyselyä.

`ROWS` laskee rivejä, ei päiviä. Jos päiviä puuttuu, kolmen rivin
ikkuna kattaa yli kolme päivää; silloin data täydennetään päiväsarjalla
(luku 7) tai käytetään kehystä `RANGE BETWEEN 2 PRECEDING AND CURRENT
ROW` numeerisella päivänumerolla.

## Edellinen ja seuraava rivi

`lag` ja `lead` hakevat arvon edelliseltä tai seuraavalta riviltä.
Kulutus lasketaan mittarilukemien erotuksena:

```{.sql tiedosto="esimerkit/08-lag.sql" osa="lag"}
```

```{.tuloste tiedosto="esimerkit/08-lag.odotettu"}
```

`WINDOW w AS (...)` nimeää ikkunan, jota useampi funktio käyttää.
Kunkin mittarin ensimmäisellä rivillä ei ole edeltäjää, joten tulos on
NULL (tässä `-`). `lag(kwh, 1, 0)` antaisi oletusarvon, mutta nolla
tekisi ensimmäisestä erotuksesta väärän.

## Käytännössä

- **Top-N ryhmittäin** on `row_number()` + CTE + `WHERE nro <= N`. Se
  korvaa korreloidun alikyselyn ja itseliitoksen, ja tuloksen
  tasatilannesäännön valitsee funktio: `row_number` (tasan N), `rank`
  tai `dense_rank` (tasatulokset mukaan).
- **Yksikäsitteinen järjestys.** Ikkunan `ORDER BY` ilman
  yksikäsitteistä avainta antaa ajosta toiseen vaihtelevan tuloksen
  `row_number`-, `lag`- ja `ROWS`-laskuissa.
- **Kehys näkyviin.** Kun kehyksellä on merkitystä, kirjoita se auki
  (`ROWS BETWEEN ...`) oletuksen varaan jättämisen sijaan.
- **Laske tietokannassa.** Kumulatiivinen summa tai liukuva keskiarvo
  sovelluksessa vaatii kaikkien rivien siirron; ikkunafunktio tekee sen
  yhdellä läpikäynnillä ja palauttaa vain tarvittavan.
- **Hinnat**: ikkunafunktio vaatii rivit järjestettyinä kunkin
  `PARTITION BY` + `ORDER BY` -yhdistelmän mukaan. Eri ikkunat samassa
  kyselyssä voivat vaatia useita järjestämisiä. Indeksi, joka vastaa
  ikkunan järjestystä, poistaa järjestämisen.

## Itsearviointi

- Osaat hakea top-N rivit ryhmittäin ja valita `row_number`-, `rank`-
  ja `dense_rank`-funktion välillä.
- Osaat laskea kumulatiivisen summan, liukuvan keskiarvon ja osuuden
  kokonaisuudesta ja selittää `ROWS`- ja `RANGE`-kehyksen eron.
- Osaat laskea muutokset edelliseen riviin `lag`-funktiolla ja
  käsitellä ensimmäisen rivin oikein.
- Osaat selittää, miksi ikkunafunktion tulokseen ei voi viitata
  samassa `WHERE`-ehdossa.
