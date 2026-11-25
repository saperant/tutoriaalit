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

### Dokumentaatiokommentit

Esittelyn `/** … */`-kommentit ovat rajapinnan dokumentaatio. Editori
näyttää ne vihjeessä kutsupaikalla, ja `tsc --declaration` kopioi ne
lähdekoodista esittelytiedostoon. Kommentit kirjoitetaan
TSDoc-muodossa, joka on JSDocin sukulainen. Tärkein ero on, että
tyyppejä ei toisteta kommentissa, koska ne ovat jo koodissa:

| Merkintä | Tarkoitus |
|----------|-----------|
| ensimmäinen kappale | yhteenveto vihjeeseen ja luetteloihin |
| `@param nimi - kuvaus` | parametrin merkitys ja yksikkö, ei tyyppiä |
| `@returns`, `@throws` | paluuarvo ja virheet, joita tyyppi ei kerro |
| `@remarks` | tarkennukset yhteenvedon jälkeen |
| `@example` | käyttöesimerkki |
| `@deprecated` | vanhentunut; editori yliviivaa kutsun |
| `{@link Nimi}` | viittaus toiseen esittelyyn |
| `@internal` | ei julkista rajapintaa (`stripInternal` poistaa esittelystä) |

Edellä näytetyssä tiedostossa `hinnoittelu.d.ts` funktiolla
`verollinen` on yhteenveto, parametrien yksiköt ja esimerkki, ja
funktion `alennus` `@remarks` kertoo ehdon, jota tyyppi `number` ei
ilmaise.

Julkisen rajapinnan HTML-dokumentaation tuottaa TypeDoc, jonka
lähtöpisteiksi annetaan samat tiedostot kuin `package.json`in
`exports`-kentässä. CI:ssä TypeDocin varoitukset käsitellään virheinä,
jolloin rikkinäinen `{@link}` tai dokumentoimaton vienti pysäyttää
rakennuksen. Kommentin tekstiä ja `@example`-lohkoja ei tarkista
mikään, joten ne luetaan katselmoinnissa. Dokumentaation rakenne,
lukijat ja testaus käsitellään taidossa *Tekninen dokumentaatio*.

### Olemassa olevan tyypin täydentäminen

Sovelluskoodissa esittelyjä kirjoitetaan useimmin siksi, että
kirjaston tai ympäristön tyyppi ei tiedä sovelluksen lisäyksistä:
ympäristömuuttujista, kehyksen pyyntöolioon lisätystä käyttäjästä tai
selaimen `window`-olion omasta kentästä. Samannimiset
`interface`-esittelyt yhdistyvät (luku 5), joten olemassa olevaan
rajapintaan voi lisätä kenttiä
`declare global`- tai `declare module "paketti"` -lohkossa:

```{.typescript tiedosto="esimerkit/10-ymparisto.ts"}
```

```{.tuloste tiedosto="esimerkit/10-ymparisto.odotettu"}
```

`declare namespace` on pelkkä esittely eikä tuota koodia, joten se on
poistettavaa syntaksia toisin kuin luvussa 2 kielletty ajonaikainen
`namespace`. Täydennys on lupaus kuten muutkin esittelyt: se ei
tarkista, että muuttuja on asetettu, joten arvo jäsennetään silti.

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

## JavaScript-projektista TypeScriptiin

Taidon *JavaScript* tapa, JSDoc-tyypit ja `checkJs`, on jo
TypeScriptin tyyppijärjestelmän käyttöä. Siirtyminen `.ts`-tiedostoihin
on siksi syntaksin vaihto, jonka voi tehdä tiedosto kerrallaan:

1. **Molemmat kielet samaan projektiin.** Asetukset `allowJs` ja
   `checkJs` pitävät vanhat tiedostot tarkistettuina, ja `.ts`- ja
   `.js`-tiedostot voivat tuoda toisiaan.
2. **Lehdet ensin.** Aloita moduleista, joita muut tuovat mutta jotka
   eivät itse tuo paljon: tyyppimäärittelyt ja apufunktiot. Nimeä
   tiedosto uudelleen ja siirrä tyypit kommenteista koodiin:
   `@typedef` muuttuu `type`-määrittelyksi, `@param {T} x` muotoon
   `x: T` ja `@template T` muotoon `<T>`. Kuvaukset jäävät
   kommenttiin.
3. **Tiukkuus asetus kerrallaan.** Jos projekti ei ollut tiukassa
   tilassa, ota ensin `noImplicitAny`, sitten `strictNullChecks` ja
   lopuksi `strict` ja `noUncheckedIndexedAccess`. Jokainen asetus
   korjataan kerralla loppuun.
4. **Ei `any`-tulvaa.** Kohta, jota ei ehdi korjata, merkitään
   kommentilla `// @ts-expect-error` ja syyllä. Merkinnät löytyvät
   haulla, ja kääntäjä ilmoittaa, kun merkintä käy tarpeettomaksi.

Siirtymän aikana CI ajaa koko ajan saman `tsc --noEmit` -tarkistuksen,
joten keskeneräinenkin tila on tarkistettu.

## Käytännössä

- **Dokumentoi julkinen rajapinta TSDoc-kommentein.** Kerro se, mitä
  tyyppi ei kerro: yksiköt, ehdot ja virheet.
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
- Osaat kirjoittaa rajapinnalle TSDoc-kommentin ja täydentää
  olemassa olevaa tyyppiä `declare global` -lohkolla.
- Osaat suunnitella JSDoc-tyypitetyn JavaScript-projektin siirtämisen
  TypeScriptiin vaiheittain.
- Osaat kuvata `tsconfig`in keskeiset asetukset ja projektiviittausten
  hyödyn monorepossa.
