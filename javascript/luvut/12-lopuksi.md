# Lopuksi {.runko-kaytannot .runko-lahteet}

## Mallit ja idiomit

| Malli | Mitä se ratkaisee | Luku |
|-------|-------------------|------|
| Optio-olio ja purkaminen oletusarvoin | nimetyt, laajennettavat parametrit | 4 |
| Moduulimalli (sulkeuma) | yksityinen tila ilman luokkaa | 4, 9 |
| Tehdasfunktio | kapselointi, rajapinta olion metodeina | 9 |
| Funktioiden koostaminen (putki) | vaiheet yhdeksi muunnokseksi | 4 |
| Memoisaatio | puhtaan funktion tulos muistiin | 4 |
| Muuttumaton päivitys (`{ ...tila }`) | muutos havaitaan viitevertailulla | 5 |
| LRU-välimuisti `Map`-rakenteella | rajattu muisti | 5 |
| `WeakMap`-metatieto | tieto olioon ilman vuotoa | 5 |
| Iteraattoriprotokolla, generaattori | oma rakenne `for...of`-silmukkaan, laiska data | 6 |
| Validointi rajapinnassa | `unknown` → tyyppi tarkistusten kautta | 6 |
| Eroteltu unioni ja kattava `switch` | variantit datana, unohtunut tapaus on virhe | 7 |
| Tulos-olio `{ ok, arvo }` | odotettu epäonnistuminen ilman poikkeusta | 7, 8 |
| Virhehierarkia ja `cause` | virhelajin käsittely, ketju säilyy | 8 |
| Vapautusprotokolla (`Symbol.dispose`, `using`) | resurssi vapautuu myös virheessä | 8 |
| Rinnakkaisuuden rajoitin | *n* työtä kerrallaan | 10 |
| `AbortSignal` | peruutus ja aikaraja | 10 |
| Async-iteraattoriputki | datan virtaus vähällä muistilla | 10 |
| Havainnoija (`EventEmitter`) | löyhä kytkentä tapahtumiin | 10 |
| Riippuvuuden injektio | testattavuus, vaihdettavat palvelut | 11 |
| Middleware-ketju | pyyntöjen käsittely vaiheina (Express, Koa) | – |

Middleware on Node-palvelimien perusmalli: jokainen vaihe saa pyynnön ja
funktion `next`, jolla se kutsuu seuraavaa vaihetta. Malli on sama kuin
luvun 4 putki, mutta asynkroninen. Se käsitellään taidossa
*Taustapalvelut*.

## Nyrkkisäännöt

1. `const`, `===`, `??` ja `?.`; ei `var`-, `==`- eikä `arguments`-
   rakenteita.
2. Tyypit JSDociin ja tiukka tarkistus päälle (`checkJs`, `strict`).
3. Data muunnetaan ja validoidaan rajapinnassa, sisällä luotetaan
   tyyppeihin.
4. Rahat sentteinä, ajat UTC:nä, muotoilu `Intl`-olioilla.
5. `Map` ja `Set` dynaamisille kokoelmille, olio tietueelle.
6. Kopioivat taulukkometodit oletuksena, muuttaminen paikallisesti.
7. Vertailufunktio jokaiseen `sort`-kutsuun.
8. Luokat vain, kun on invariantti; muuten funktiot ja data.
9. Heitä `Error`-olioita, käsittele vain tunnetut virheet, säilytä
   `cause`.
10. Jokainen lupaus odotetaan tai käsitellään; pitkä työ ottaa
    `AbortSignal`-signaalin.
11. Älä tuki tapahtumasilmukkaa: I/O asynkronisesti, laskenta säikeisiin.
12. ES-modulit, nimetyt viennit, ei sivuvaikutuksia tuonnissa.
13. Riippuvuudet harkiten, lukitustiedosto versionhallintaan.

## Hinnat koottuina

| Toiminto | Hinta |
|----------|-------|
| funktiokutsu, olioliteraali, sulkeuma | halpa (inline-laajennus, nuori sukupolvi) |
| kentän haku samanmuotoisista olioista | halpa; monimuotoinen kohta hidas |
| `delete`, kenttien lisäys jälkikäteen | muodon vaihto, mahdollisesti sanakirjatila |
| `Map`/`Set`: haku, lisäys, poisto | vakioaikainen |
| `includes`, `indexOf`, `shift` | lineaarinen |
| poikkeuksen heitto | pinojäljen keruu: kallis |
| `JSON.parse`, `structuredClone` | lineaarinen datan koossa, ei ilmainen |
| `await` | mikrotehtävä |
| synkroninen I/O tai raskas laskenta | pysäyttää kaikki pyynnöt |
| Worker-säikeen käynnistys | kymmeniä millisekunteja, muistia |

## Jatkotaidot

- *TypeScript*: tyypit osaksi kieltä, tyyppijärjestelmä suunnittelun
  välineenä.
- *HTML ja CSS* ja *Web-sovellukset*: DOM, selaimen tapahtumat,
  sovelluskehykset.
- *Taustapalvelut*: HTTP-palvelimet, tietokannat ja autentikointi Nodella.
- *Web-sovelluskehykset ja niiden periaatteet*: mitä React, Vue,
  Angular ja Svelte ratkaisevat ja miten.
- *Funktionaalinen ohjelmointi (Racket)*: korkeamman asteen
  funktioiden, sulkeumien ja muuttumattomuuden juuret.
- *Tekninen dokumentaatio*: lukijat, dokumenttityypit ja
  rajapintadokumentaation tuottaminen JSDoc-kommenteista.

## Lähteet ja dokumentaatio

- ECMA-262: *ECMAScript Language Specification*.
  <https://tc39.es/ecma262/>
- TC39-ehdotukset ja niiden vaiheet. <https://github.com/tc39/proposals>
- MDN Web Docs: JavaScript-opas ja -viite (CC BY-SA 2.5).
  <https://developer.mozilla.org/fi/docs/Web/JavaScript>
- Node.js-dokumentaatio (rajapinnat, `node:test`, modulit).
  <https://nodejs.org/docs/latest/api/>
- TypeScript: *JSDoc Reference* ja *Type Checking JavaScript Files*.
  <https://www.typescriptlang.org/docs/handbook/jsdoc-supported-types.html>
- V8-blogi: piilotetut luokat, inline-välimuistit, roskienkeruu.
  <https://v8.dev/blog>
- Jake Archibald: *Tasks, microtasks, queues and schedules*.
  <https://jakearchibald.com/2015/tasks-microtasks-queues-and-schedules/>

## Kirjat

- Axel Rauschmayer: *Exploring JavaScript* (vapaasti luettavissa
  verkossa). <https://exploringjs.com/>
- Marijn Haverbeke: *Eloquent JavaScript*, 4. painos (CC BY-NC 3.0,
  luettavissa verkossa). <https://eloquentjavascript.net/>
- Kyle Simpson: *You Don't Know JS Yet* (CC BY-NC-ND, GitHub).
- David Flanagan: *JavaScript: The Definitive Guide*, 7. painos.
  O'Reilly 2020.

## Kirjastot ja työkalut

| Tarve | Kirjastot |
|-------|-----------|
| HTTP-palvelin | Fastify, Express, Hono |
| validointi | Zod, Valibot, Ajv |
| testaus | `node:test`, Vitest, Playwright (selain) |
| laatu | ESLint, typescript-eslint, Prettier, Biome |
| paketointi | Vite, esbuild, Rollup |
| loki | pino |
| päivämäärät | `Intl`, date-fns, Luxon; Temporal, kun Node tukee sitä |
| dokumentaatio | TypeDoc, `jsdoc` |
| rinnakkaisuus | p-limit, Piscina |
