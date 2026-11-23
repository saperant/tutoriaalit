# Modulit, esittelytiedostot ja projektit {.runko-modulit}

TypeScript käyttää JavaScriptin ES-moduleita. Tyyppejä varten mukana on
kaksi lisäkäsitettä: tyyppituonnit, jotka poistetaan ajosta, ja
esittelytiedostot (`.d.ts`), jotka kuvaavat JavaScript-koodin tyypit.

## Tuonnit ja verbatimModuleSyntax

Node ajaa `.ts`-tiedostot sellaisinaan, joten tuonnit kirjoitetaan
ajettavan tiedoston nimellä: `./malli.ts`. Tyyppien tuonnit merkitään
`type`-sanalla, joko koko lauseelle (`import type { … }`) tai
yksittäiselle nimelle (`import { tilaus, type Tilaus }`).

Asetus `verbatimModuleSyntax` vaatii merkinnän. Sääntö on yksinkertainen:
kaikki `type`-merkityt tuonnit poistetaan, kaikki muut säilyvät. Tuonnin
poistaminen ei siis riipu siitä, mitä tuodussa modulissa on, ja tyypit
voi poistaa tiedosto kerrallaan ilman koko ohjelman analyysiä.

```{.typescript tiedosto="esimerkit/10-tuonti.ei-kaanny.ts"}
```

```
10-tuonti.ei-kaanny.ts(3,17): error TS1484: 'ParsedPath' is a type and
  must be imported using a type-only import when 'verbatimModuleSyntax'
  is enabled.
```

```{.tuloste tiedosto="esimerkit/10-tuonti.odotettu"}
```

Ilman merkintää Node yrittäisi tuoda ajossa nimen, jota ei ole olemassa,
ja ohjelma kaatuisi.

## Esittelytiedostot

JavaScript-modulin tyypit kuvataan `.d.ts`-tiedostossa. Se sisältää
pelkät esittelyt (`declare`) ilman toteutusta. Kääntäjä etsii
tuonnille `./hinnoittelu.js` esittelyn `./hinnoittelu.d.ts`, ja Node
ajaa JavaScript-tiedoston.

```{.javascript tiedosto="esimerkit/10-kirjasto/hinnoittelu.js"}
```

```{.typescript tiedosto="esimerkit/10-kirjasto/hinnoittelu.d.ts"}
```

```{.typescript tiedosto="esimerkit/10-kirjasto/tyypit.ts"}
```

```{.typescript tiedosto="esimerkit/10-kirjasto/main.ts"}
```

```{.tuloste tiedosto="esimerkit/10-kirjasto.odotettu"}
```

Kääntäjä ei tarkista, että esittely vastaa toteutusta. Käsin kirjoitettu
`.d.ts` on siksi samanlainen lupaus kuin `as`. Tavallisin tapa on
toisin päin: kirjasto kirjoitetaan TypeScriptillä, ja `tsc
--declaration` tuottaa esittelyt koodista.

Kirjastojen tyypit tulevat kolmesta lähteestä:

| Lähde | Esimerkki |
|-------|-----------|
| Paketin omat tyypit (`types`-kenttä `package.json`issa) | `zod`, `vite` |
| DefinitelyTyped-paketti `@types/…` | `@types/node`, `@types/express` |
| Oma esittely projektissa (`declare module "x"`) | Vanha sisäinen kirjasto |

`@types`-paketin versio pidetään samassa pääversiossa kuin kirjasto tai
ajoympäristö (`@types/node@24` Node 24:lle).

## tsconfig ja projektin rakenne

`tsconfig.json` määrittää kääntäjän asetukset ja tiedostot. Tämän
paketin asetukset on esitelty luvussa 3. Suuremmassa projektissa
lisäksi:

- **`include` ja `exclude`** rajaavat tiedostot.
- **Projektiviittaukset** (`references` ja `composite`) jakavat
  monorepon osiin, jotka tarkistetaan erikseen ja inkrementaalisesti
  (`tsc -b`). Jokainen paketti näkee toisista vain niiden `.d.ts`-
  esittelyt, mikä nopeuttaa tarkistusta ja pakottaa selkeät rajapinnat.
- **Kirjasto julkaistaan JavaScriptinä** ja esittelyineen (`outDir`,
  `declaration`). npm-pakettiin ei julkaista `.ts`-lähteitä ajettavaksi,
  koska Node ei poista tyyppejä `node_modules`-hakemiston tiedostoista.
- **`package.json`in `exports`** määrittää modulin julkiset
  tuontipolut; se on modulin rajapinta samalla tavalla kuin
  `export`-lauseet ovat tiedoston rajapinta.

## Käytännössä

- **`import type` aina tyypeille.** `verbatimModuleSyntax` tekee
  tuonneista ennustettavia ja on edellytys tyyppien poistolle.
- **Yksi moduli, yksi vastuu.** Tyyppimoduli (`tyypit.ts`), puhtaat
  funktiot ja reunan I/O erillisiin tiedostoihin. Syklit modulien välillä
  ovat merkki väärästä jaosta.
- **`.d.ts` vain JavaScriptille.** Uusi koodi kirjoitetaan
  TypeScriptillä, jolloin esittelyt tuotetaan koodista eivätkä voi erota
  siitä.
- **Kirjastojen tyypeille ei luoteta sokeasti.** Ulkoisen API:n tyypit
  ovat lupauksia; data jäsennetään silti reunalla (luku 9).
- **Ei `namespace`a eikä `require`a.** ES-modulit hoitavat
  nimiavaruudet; vanhat muodot eivät ole poistettavaa syntaksia.

## Itsearviointi

- Osaat kirjoittaa ES-modulituonnit `.ts`-päätteineen ja merkitä
  tyyppituonnit `type`-sanalla.
- Osaat kirjoittaa `.d.ts`-esittelyn JavaScript-modulille ja kertoa sen
  rajoitukset.
- Osaat selittää, mistä kirjastojen tyypit tulevat ja miten
  `@types`-paketin versio valitaan.
- Osaat kuvata `tsconfig`in keskeiset asetukset ja projektiviittausten
  hyödyn monorepossa.
