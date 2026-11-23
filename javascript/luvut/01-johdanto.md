# Johdanto {.runko-johdanto}

JavaScript on verkon ohjelmointikieli. Brendan Eich kirjoitti sen
ensimmäisen version Netscapelle kymmenessä päivässä vuonna 1995, ja
kieli standardoitiin Ecma Internationalissa nimellä ECMAScript (ECMA-262)
vuonna 1997. Kiireinen alku näkyy yhä: automaattiset tyyppimuunnokset,
`this`-sidonnan säännöt ja `typeof null === "object"` ovat jäänteitä,
joita ei voi poistaa rikkomatta verkkoa.

Kieli on silti muuttunut perusteellisesti. ES5 (2009) toi tiukan tilan
ja JSON-tuen. ES2015 (ES6) oli kielen suurin uudistus: `let` ja `const`,
nuolifunktiot, luokat, modulit, lupaukset, iteraattorit ja `Map`.
Siitä lähtien standardista on julkaistu uusi versio vuosittain. TC39-
komitea hyväksyy ehdotuksen standardiin, kun se on edennyt neljännelle
vaiheelle ja vähintään kaksi selainmoottoria on toteuttanut sen. Tämä
tutoriaali opettaa nykyistä JavaScriptia (ES2024) eikä käy läpi vanhoja
tapoja kuin silloin, kun ne vielä aiheuttavat virheitä.

## Mihin JavaScript sopii ja mihin ei

JavaScript on ainoa kieli, jota kaikki selaimet ajavat suoraan, ja
Node.js toi sen palvelimelle vuonna 2009. Nykyään sitä käytetään

- selainsovelluksissa (React, Vue, Svelte, Angular)
- palvelimilla ja rajapinnoissa (Node.js, Deno, Bun; Express, Fastify)
- komentorivityökaluissa ja rakennusputkissa (npm, Vite, ESLint)
- työpöytä- ja mobiilisovelluksissa (Electron, React Native)
- palvelimettomissa funktioissa ja reunalaskennassa (Cloudflare
  Workers, AWS Lambda).

JavaScript ei ole paras valinta, kun

- työ on raskasta numeerista laskentaa: luvut ovat 64-bittisiä
  liukulukuja, ja yksi säie laskee kerrallaan (säikeet ja WebAssembly
  auttavat, luku 10)
- tarvitaan ennustettavaa viivettä tai muistinhallintaa (roskienkeruu)
- ohjelma on suuri ja pitkäikäinen eikä tyyppejä tarkisteta: silloin
  valitaan TypeScript tai tämän tutoriaalin tapa, JSDoc-tyypit ja
  tyyppitarkistin (luku 2).

## Toteutukset ja ympäristöt

Kieli (ECMAScript) ja ympäristö ovat eri asioita. Moottori toteuttaa
kielen: V8 (Chrome, Node.js, Deno), SpiderMonkey (Firefox) ja
JavaScriptCore (Safari, Bun). Ympäristö tarjoaa rajapinnat: selain
tarjoaa DOMin, `fetch`in ja tapahtumat, Node.js tiedostot, prosessit,
verkon ja `npm`-ekosysteemin. Moni rajapinta on nykyään yhteinen
(`fetch`, `URL`, `AbortController`, `structuredClone`, `TextEncoder`).

Tämän tutoriaalin esimerkit ajetaan Node.js:llä. Ne on testattu
versioilla 22 ja 24, joista jälkimmäinen on kehityskontin versio.
Noden parilliset pääversiot ovat pitkäaikaisesti tuettuja (LTS), ja
tuotannossa käytetään niitä. Selaimen DOM ja tapahtumankäsittely
käsitellään taidoissa *HTML ja CSS* ja *Web-sovellukset*.

## Työkalut

| Työkalu | Tehtävä |
|---------|---------|
| `node` | ajaa ohjelman, REPL, testit (`node --test`), debuggeri |
| `npm` | paketit, riippuvuudet ja skriptit (`package.json`) |
| `tsc` | tyyppitarkistus JSDoc-tyypeistä (`checkJs`) |
| ESLint | koodin laatu: epäilyttävät rakenteet ja tyylisäännöt |
| Prettier | automaattinen muotoilu |
| Chrome DevTools | debuggaus ja profilointi (`node --inspect`) |

Kehityskontissa ovat Node.js 24 ja TypeScript 7. Esimerkkihakemistossa
`package.json` kertoo, että tiedostot ovat ES-moduleita, ja
`tsconfig.json` ottaa tyyppitarkistuksen käyttöön. Luku 11 käy
työkalut läpi.

## Ensimmäinen ohjelma

Ohjelma lukee tekstin syötteestä ja tulostaa viisi yleisintä sanaa:

```{.javascript tiedosto="esimerkit/01-sanalaskuri.js"}
```

```text
$ node 01-sanalaskuri.js < 01-sanalaskuri.syote
```

```{.tuloste tiedosto="esimerkit/01-sanalaskuri.odotettu"}
```

Jo tässä näkyy moni nykyisen JavaScriptin piirre:

- `import` tuo Noden modulista funktion `text`, joka lukee koko
  virran merkkijonoksi. Ylimmän tason `await` odottaa sitä.
- Funktioiden yllä olevat JSDoc-kommentit kertovat parametrien ja
  paluuarvon tyypit. Ajonaikana niillä ei ole vaikutusta, mutta
  tyyppitarkistin ja editori käyttävät niitä.
- Säännöllinen lauseke `/[\p{L}\p{N}]+/gu` tunnistaa kaikkien kielten
  kirjaimet ja numerot (lippu `u` ottaa Unicode-tuen käyttöön), joten
  sanat *pöydällä* ja *äiti* säilyvät ehjinä.
- `??` antaa oletusarvon vain, kun vasen puoli puuttuu (`null` tai
  `undefined`).
- `Map` on varsinainen sanakirjatyyppi. Levityssyntaksi `[...maarat]`
  muuttaa sen avain–arvo-pareiksi, ja purkaminen `([a, m], [b, n])`
  nimeää parien osat.
- Lajittelu tehdään ensin määrän ja sitten aakkosjärjestyksen mukaan:
  `n - m || a.localeCompare(b, "fi")`.

## Lukuohje

Luku 2 on tarkoitettu toisen kielen osaavalle: se kokoaa JavaScriptin
ajattelutavan, vastaavuudet, hinnat ja sudenkuopat. Luvut 3–8 käyvät
kielen läpi, luku 9 modulit ja paketit, luku 10 asynkronisuuden ja
säikeet ja luku 11 työkalut. Jokainen luku päättyy osioon
*Käytännössä*, joka kokoaa ammattilaisten käytännöt ja hinnat, ja
*itsearviointiin*. Jos hallitset itsearvioinnin kaikki kohdat, voit
ohittaa luvun.
