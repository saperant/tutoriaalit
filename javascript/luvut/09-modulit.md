# Modulit ja paketit {.runko-modulit}

Tähän asti jokainen esimerkki on ollut yksi tiedosto. Suurempi ohjelma
jaetaan moduleihin, joista kukin piilottaa toteutuksensa ja näyttää
muille pienen rajapinnan. Tässä luvussa käydään läpi kielen oma
modulijärjestelmä, Noden vanhempi CommonJS sekä npm-paketit, joilla
toisten kirjoittama koodi otetaan käyttöön.

## ES-modulit

ES-moduli (ESM) on tiedosto, jolla on oma näkyvyysalue. Se näyttää
ulos vain `export`-merkityt nimet ja tuo muiden modulien nimiä
`import`-lauseella. Modulit ovat aina tiukassa tilassa, ne ladataan
kerran ja tuonnit ovat eläviä sidoksia, eivät kopioita.

Esimerkkiohjelmassa on kolme modulia. Varastomoduli piilottaa
tietorakenteensa tehdasfunktion taakse:

```{.javascript tiedosto="esimerkit/09-varasto/varasto.js"}
```

```{.javascript tiedosto="esimerkit/09-varasto/muotoilu.js"}
```

```{.javascript tiedosto="esimerkit/09-varasto/main.js"}
```

```{.tuloste tiedosto="esimerkit/09-varasto.odotettu"}
```

```{.dot otsikko="Esimerkin tuonnit. Yhtenäinen nuoli on ajonaikainen tuonti, katkoviiva pelkkä tyyppituonti, joka ei lataa modulia."}
digraph {
  rankdir=LR; node [shape=box];
  main [label="main.js"]; varasto [label="varasto.js"];
  muotoilu [label="muotoilu.js"]; testi [label="varasto.test.js"];
  main -> varasto [label="luoVarasto,\nTILAUSRAJA"];
  main -> muotoilu [label="oletusvienti"];
  muotoilu -> varasto [style=dashed, label="@import Saldo"];
  testi -> varasto;
}
```

- Nimetyt viennit (`export function`, `export const`) ovat oletus:
  nimi on sama kaikkialla, ja editori osaa tuoda ja nimetä ne uudelleen.
  Oletusvienti (`export default`) sopii modulille, jolla on yksi
  päätehtävä, mutta tuoja voi antaa sille minkä nimen tahansa.
- Suhteellisessa tuonnissa on aina tiedostopääte (`./varasto.js`).
  Pakettien ja Noden sisäisten modulien nimet tuodaan ilman polkua
  (`node:fs`).
- JSDocin `@import` tuo tyypin toisesta modulista ilman ajonaikaista
  tuontia, ja `ReturnType<typeof luoVarasto>` johtaa tyypin funktiosta.

Tehdasfunktio, joka palauttaa olion metodeineen, on JavaScriptin
yleisin tapa kapseloida: tila on sulkeumassa, ja palautettu olio on
rajapinta. Testit kirjoitetaan samalle rajapinnalle (luku 11):

```{.javascript tiedosto="esimerkit/09-varasto/varasto.test.js"}
```

## Dynaaminen tuonti ja import.meta

`import()` lataa modulin ajon aikana ja palauttaa lupauksen. Sillä
ladataan harvoin tarvittavat tai valinnaiset osat vasta tarvittaessa.
Ylimmän tason `await` on sallittu moduleissa:

```{.javascript tiedosto="esimerkit/09-dynaaminen.js" osa="dynaaminen"}
```

`import.meta` sisältää modulin omat tiedot. Se korvaa CommonJS:n
`__filename`- ja `__dirname`-muuttujat:

```{.javascript tiedosto="esimerkit/09-dynaaminen.js" osa="meta"}
```

```{.tuloste tiedosto="esimerkit/09-dynaaminen.odotettu"}
```

## CommonJS

Node käytti alun perin omaa modulijärjestelmäänsä CommonJS:ää
(`require`, `module.exports`), ja suuri osa npm-paketeista on yhä
sellaisia. Erot:

| | ES-moduli | CommonJS |
|-|-----------|----------|
| syntaksi | `import`, `export` | `require()`, `module.exports` |
| lataus | asynkroninen, analysoitavissa etukäteen | synkroninen, ajon aikana |
| tiedosto | `.mjs` tai `"type": "module"` | `.cjs` tai oletus |
| ylimmän tason `await` | kyllä | ei |

ES-moduli voi tuoda CommonJS-paketin, ja Node 22:sta alkaen myös
`require` voi ladata ES-modulin (kunhan siinä ei ole ylimmän tason
`await`-lausetta). Uusi koodi kirjoitetaan ES-moduleina.

Selaimessa ES-modulit ladataan `<script type="module">`-elementillä, ja
tuonnit ovat URL-osoitteita. Tuotannossa koodi kootaan yleensä
paketoijalla (Vite, esbuild, Rollup), joka yhdistää modulit ja poistaa
käyttämättömän koodin (*tree shaking*).

## npm ja package.json

`package.json` kuvaa paketin: nimen, version, moduulityypin,
riippuvuudet ja skriptit. Esimerkkihakemiston tiedosto:

```{.json tiedosto="esimerkit/package.json"}
```

- `dependencies` ovat ajonaikaisia riippuvuuksia, `devDependencies`
  vain kehityksessä tarvittavia (testit, tyyppitarkistus, paketointi).
- Versiot noudattavat semanttista versiointia `PÄÄ.SIVU.KORJAUS`.
  `^24.0.0` sallii sivu- ja korjausversiot, `~7.0.2` vain korjaukset.
- `npm install` kirjoittaa tarkat versiot lukitustiedostoon
  `package-lock.json`, joka versioidaan. CI asentaa komennolla `npm ci`,
  joka asentaa täsmälleen lukitut versiot.
- `npm run tarkista` ajaa skriptin; `npx` ajaa paketin komennon.
- Kirjaston `exports`-kenttä määrää, mitkä polut paketista saa tuoda.
  Kaikki muu on yksityistä.

Riippuvuudet ovat hyökkäyspinta: jokainen paketti ja sen riippuvuudet
ajavat koodia koneellasi ja tuotannossa. `npm audit` kertoo tunnetut
haavoittuvuudet, ja asennusskriptit voi estää asetuksella
`ignore-scripts`. Pieni apufunktio kannattaa usein kirjoittaa itse
kuin tuoda paketti.

## Käytännössä

- **ES-modulit, nimetyt viennit.** Oletusvienti vain, kun modulilla on
  yksi selvä päätehtävä.
- **Yksi vastuu modulia kohden**, ja julkinen rajapinta mahdollisimman
  pieni. Tehdasfunktio tai luokka kapseloi tilan.
- **Ei sivuvaikutuksia tuonnissa.** Moduli, joka avaa yhteyksiä tai
  muuttaa globaalia tilaa ladattaessa, on vaikea testata. Tee alustus
  eksplisiittisellä funktiolla.
- **Ei kehäriippuvuuksia.** Ne toimivat ES-moduleissa, mutta arvot voivat
  olla vielä alustamatta. Kehä kertoo, että vastuut ovat sekaisin.
- **Lukitustiedosto versionhallintaan, `npm ci` CI:hin**, ja
  riippuvuuksien päivitykset hallitusti (Dependabot, Renovate).
- **Hinta.** Modulin lataus on kertaluonteinen; `import()` maksaa vain
  ensimmäisellä kerralla. Suuri riippuvuuspuu hidastaa käynnistystä ja
  kasvattaa selaimeen lähetettävää koodia.

## Itsearviointi

- Osaat jakaa ohjelman ES-moduleihin, käyttää nimettyjä ja oletusvientejä
  ja tuoda tyyppejä JSDocin `@import`-merkinnällä.
- Osaat kapseloida tilan tehdasfunktiolla ja käyttää dynaamista tuontia.
- Osaat kertoa ES-modulien ja CommonJS:n erot ja sen, miten Node valitsee
  modulityypin.
- Osaat lukea ja kirjoittaa `package.json`-tiedoston, selittää
  semanttisen versioinnin merkinnät ja lukitustiedoston tarkoituksen.
