# Kokoelmat ja datasta johdetut tyypit {.runko-kokoelmat}

Kokoelmat ovat JavaScriptin taulukot, `Map` ja `Set`, ja niiden
algoritmit (`map`, `filter`, `reduce`, `toSorted`, `Object.groupBy`)
opetetaan JavaScript-paketissa. Tässä luvussa keskitytään siihen, miten
kokoelmat tyypitetään ja miten tyypit johdetaan datasta.

## Kokoelmien tyypit

```{.typescript tiedosto="esimerkit/08-kokoelmat.ts"}
```

```{.tuloste tiedosto="esimerkit/08-kokoelmat.odotettu"}
```

| Tyyppi | Käyttö |
|--------|--------|
| `T[]`, `readonly T[]` | Taulukko; `readonly` poistaa muuttavat metodit (`push`, `sort`) |
| `[a: A, b: B]` | Monikko: kiinteä pituus, paikkakohtaiset tyypit |
| `Map<K, V>` | Avaimet dataa, mikä tahansa avaintyyppi, järjestys säilyy |
| `Set<T>` | Joukko, jäsenyys vakioajassa |
| `Record<K, V>` | Olio, jonka avainjoukko on tunnettu (`K` literaaliunioni) |
| `Partial<Record<K, V>>` | Olio, josta osa avaimista voi puuttua (`Object.groupBy`) |

- **`readonly`-taulukko parametrina** kertoo, ettei funktio muuta
  argumenttia, ja hyväksyy sekä muuttuvat että muuttumattomat taulukot.
- **`Object.groupBy`** palauttaa olion, jonka avaimet ovat valinnaisia:
  ryhmä on olemassa vain, jos siihen kuului alkioita. Siksi
  `alueittain.etelä ?? []`.
- **`toSorted`, `toReversed` ja `with`** (ES2023) palauttavat uuden
  taulukon. Ne toimivat myös `readonly`-taulukoille, toisin kuin
  `sort`.
- **Lajittelufunktion** parametrien tyypit päätellään taulukosta;
  monikon purku `([, a], [, b])` nimeää vain tarvittavat paikat.

## Tyypit datasta

TypeScriptissä tyypin ja datan suhde toimii kumpaankin suuntaan. Tyypillä
tarkistetaan data, ja datasta johdetaan tyyppi, kun data on totuuden
lähde (reitit, asetukset, käännökset, virhekoodit).

```{.typescript tiedosto="esimerkit/08-satisfies.ts"}
```

```{.tuloste tiedosto="esimerkit/08-satisfies.odotettu"}
```

| Merkintä | Tarkistaa | Tyyppi |
|----------|-----------|--------|
| `const x: T = arvo` | kyllä | `T` (levennetty) |
| `const x = arvo` | ei | päätelty, levennetty (`string`) |
| `const x = arvo as const` | ei | literaalit, syvästi `readonly` |
| `const x = arvo satisfies T` | kyllä | päätelty arvosta |
| `const x = arvo as const satisfies T` | kyllä | literaalit, `readonly` |

Annotaatio `Record<string, Reitti>` hukkaa tiedon siitä, mitkä reitit on
olemassa: jokainen haku voi epäonnistua. `satisfies` tarkistaa saman
muodon mutta säilyttää tarkan tyypin, joten `keyof typeof reitit` on
reittien nimien unioni ja virheellinen nimi on käännösvirhe.

`typeof OLETUKSET` johtaa tyypin oletusarvoista, jolloin uusi asetus
lisätään yhteen paikkaan.

## Olion avaimet

`Object.keys` palauttaa `string[]`, ei `(keyof T)[]`. Rakenteellisessa
tyypityksessä olio voi sisältää muitakin kenttiä kuin sen tyyppi
kertoo (luku 5), joten avainten lista ei rajaudu tyypin kenttiin.

```{.typescript tiedosto="esimerkit/08-avaimet.ei-kaanny.ts"}
```

```
08-avaimet.ei-kaanny.ts(7,47): error TS7053: Element implicitly has an
  'any' type because expression of type 'string' can't be used to index
  type 'Hinnat'.
```

```{.tuloste tiedosto="esimerkit/08-avaimet.odotettu"}
```

Ratkaisut: `Object.values` ja `Object.entries`, kun tarvitaan arvot;
`Map`, kun avaimet ovat dataa; tai tunnettu avainlista
`as const` -taulukkona, jonka yli iteroidaan.

## Käytännössä

- **`Map` dataa, olio rakennetta varten.** Kun avaimet tulevat datasta
  (tuotenimet, käyttäjätunnukset), `Map` on oikea valinta: avaimet eivät
  törmää perittyihin kenttiin, ja koko ja järjestys ovat määriteltyjä.
- **`readonly` parametreihin.** `readonly T[]` ja `ReadonlyMap<K, V>`
  dokumentoivat, ettei funktio muuta kokoelmaa.
- **`satisfies` konfiguraatioon.** Vakiotaulukot ja -oliot kirjoitetaan
  `as const satisfies T`, jolloin muoto tarkistetaan ja tarkat
  literaalityypit säilyvät.
- **Johda tyyppi datasta, kun data on lähde.** `keyof typeof`,
  `(typeof T)[number]` ja `typeof X` pitävät tyypin ja datan
  synkronissa.
- **Muista indeksoinnin `undefined`.** Hakutulos `Map.get` ja
  `Record`-indeksointi voivat puuttua; käsittele puuttuminen `??`- tai
  `if`-lauseella.

## Itsearviointi

- Osaat tyypittää taulukot, monikot, `Map`-, `Set`- ja
  `Record`-kokoelmat ja valita niiden välillä.
- Osaat selittää eron annotaation, `as const`in ja `satisfies`in välillä
  ja käyttää niitä konfiguraatiodatassa.
- Osaat johtaa tyypin datasta `typeof`-, `keyof typeof`- ja
  `[number]`-merkinnöillä.
- Osaat selittää, miksi `Object.keys` palauttaa `string[]`, ja käsitellä
  olion avaimet turvallisesti.
