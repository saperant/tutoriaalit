# NULL ja kolmiarvoinen logiikka

`NULL` merkitsee puuttuvaa tai tuntematonta arvoa. Se ei ole nolla eikä
tyhjä merkkijono. Koska arvoa ei tunneta, vertailu siihen ei ole tosi
eikä epätosi vaan *tuntematon*. SQL:n logiikka on siksi kolmiarvoinen:
tosi, epätosi ja tuntematon.

## Vertailut ja totuustaulu

```{.sql tiedosto="esimerkit/04-null.sql" osa="vertailut"}
```

```{.tuloste tiedosto="esimerkit/04-null.odotettu"}
```

- `NULL = NULL` on tuntematon: kaksi tuntematonta arvoa voivat olla
  samat tai eri.
- `IS NULL` ja `IS NOT NULL` ovat ainoat tavat testata puuttuvuutta.
- `AND` on epätosi, jos yksikin osa on epätosi; `OR` on tosi, jos
  yksikin osa on tosi. Muuten tuntematon säilyy.
- `coalesce(a, b, ...)` palauttaa ensimmäisen arvon, joka ei ole NULL.

SQLite esittää totuusarvot lukuina 1 ja 0. PostgreSQL:ssä tulos olisi
`true`, `false` ja `NULL`.

## NULL suodatuksessa

`WHERE` hyväksyy vain rivit, joiden ehto on *tosi*. Tuntematon putoaa
pois yhtä lailla kuin epätosi:

```{.sql tiedosto="esimerkit/04-null-kaupungit.sql" osa="where"}
```

Sari Laineen kaupunki puuttuu, joten ehto `kaupunki <> 'Helsinki'` on
hänen kohdallaan tuntematon ja hän putoaa pois. Jos kysymys on "kaikki,
joiden kaupunki ei ole Helsinki, myös tuntemattomat", vertailu tehdään
NULL-turvallisella operaattorilla. SQLitessä se on `IS NOT`, standardissa
ja PostgreSQL:ssä `IS DISTINCT FROM`, jota myös SQLite 3.39+ tukee.

## NULL koosteissa

Koostefunktiot ohittavat NULL-arvot. `count(*)` laskee rivit,
`count(sarake)` arvot:

```{.sql tiedosto="esimerkit/04-null-kaupungit.sql" osa="koosteet"}
```

```{.tuloste tiedosto="esimerkit/04-null-kaupungit.odotettu"}
```

Tyhjän joukon `sum` ja `avg` ovat NULL, eivät nolla. Raportissa
summa kirjoitetaan `coalesce(sum(x), 0)`, jos nolla on oikea vastaus.

## NOT IN -ansa

Yleisin NULL-virhe on `NOT IN` alikyselyn kanssa. Ehto
`x NOT IN (a, b, NULL)` tarkoittaa `x <> a AND x <> b AND x <> NULL`, ja
viimeinen osa on aina tuntematon. Ehto ei siis ole koskaan tosi:

```{.sql tiedosto="esimerkit/04-not-in.sql" osa="ansa"}
```

Kysely ei palauta yhtään riviä, vaikka tarkoitus oli rajata pois vain
Oulu. `NOT EXISTS` vertaa rivi kerrallaan eikä kärsi ongelmasta:

```{.sql tiedosto="esimerkit/04-not-in.sql" osa="oikein"}
```

```{.tuloste tiedosto="esimerkit/04-not-in.odotettu"}
```

Tulos sisältää myös Sarin, jonka kaupunki on tuntematon. Jos hänet
halutaan pois, se sanotaan ehdossa erikseen (`a.kaupunki IS NOT NULL`).

## Muita NULL-sääntöjä

- **Järjestys**: SQLite järjestää NULL-arvot pienimmiksi, PostgreSQL
  suurimmiksi. `ORDER BY kaupunki NULLS LAST` toimii molemmissa.
- **Yksikäsitteisyys**: `UNIQUE`-sarakkeessa saa olla monta NULLia,
  koska ne eivät ole keskenään yhtä suuria. PostgreSQL 15+ voi kieltää
  tämän määreellä `NULLS NOT DISTINCT`.
- **Ryhmittely**: `GROUP BY` ja `DISTINCT` käsittelevät NULL-arvot
  yhtenä ryhmänä.
- **Merkkijonot**: `'a' || NULL` on NULL. Oracle on poikkeus: siellä
  tyhjä merkkijono on NULL.

## Käytännössä

- **`NOT NULL` on oletus.** Jokainen sarake, joka saa olla NULL, lisää
  kolmiarvoista logiikkaa jokaiseen sitä käyttävään kyselyyn. NULL
  sallitaan vain, kun "ei tiedossa" tai "ei koske" on mallissa
  mielekäs tila.
- **Ei taikalukuja.** Puuttuvaa arvoa ei esitetä arvolla `-1`, `0`,
  `''` tai `'1900-01-01'`. Ne näyttävät oikeilta arvoilta ja vääristävät
  koosteita.
- **`NOT EXISTS` mieluummin kuin `NOT IN`** alikyselyn kanssa. Optimoija
  muuttaa sen tehokkaaksi anti-liitokseksi, eikä tulos riipu siitä,
  sisältääkö alikysely NULLeja.
- **Tarkista ehtojen NULL-käytös.** Jokaisen `<>`- ja `NOT`-ehdon
  kohdalla kannattaa kysyä, mitä NULL-riveille tapahtuu.
- **`coalesce` raportin reunalla.** Muunna NULL nollaksi vasta, kun
  nolla on oikea vastaus. Keskiarvossa puuttuva ei ole nolla.

## Itsearviointi

- Osaat ennustaa vertailujen ja `AND`/`OR`-lausekkeiden tuloksen, kun
  mukana on NULL.
- Osaat selittää, miksi `NOT IN` palauttaa tyhjän tuloksen, jos
  alikyselyssä on NULL, ja korjata kyselyn `NOT EXISTS` -ehdolla.
- Osaat valita `count(*)`, `count(sarake)` ja `coalesce`-funktion
  välillä raportin tarpeen mukaan.
- Osaat kirjoittaa NULL-turvallisen vertailun SQLitessä ja
  PostgreSQL:ssä.
