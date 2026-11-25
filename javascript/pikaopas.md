---
title: JavaScript
subtitle: Pikaopas kokeneelle kehittäjälle · ES2025, Node.js 22–24
---

# Työkalut

| Tarkoitus | Komento |
|-----------|---------|
| Ajo, REPL | `node ohjelma.js`, `node` |
| Uudelleenajo | `node --watch ohjelma.js` |
| Tyypit | `tsc -p .` (`checkJs`, `strict`), `// @ts-check` |
| Testit | `node --test`, `--test-reporter=spec` |
| Kattavuus | `node --test --experimental-test-coverage` |
| Debuggaus | `node --inspect-brk`, `chrome://inspect` |
| Profiili | `node --cpu-prof`, `--heap-prof` |
| Paketit | `npm install -D x`, `npm ci`, `npm run x`, `npx` |
| Laatu | `eslint .`, `prettier --check .`, `npm audit` |

# Perusteet

```{.javascript tiedosto="esimerkit/pikaopas.js" osa="perus"}
```

- Epätodet: `false 0 -0 0n "" null undefined NaN`; kaikki muu tosi.
- `===` aina; `Object.is` erottaa `-0`:n ja löytää `NaN`:n.
- `typeof null === "object"`; `Array.isArray(x)`.
- `Number("4x")` on `NaN`, `parseInt("4x")` on 4.
- Rahat sentteinä, `Intl.NumberFormat`, `Intl.DateTimeFormat`.

```{.javascript tiedosto="esimerkit/pikaopas.js" osa="funktiot"}
```

| `this` | Arvo |
|--------|------|
| `o.m()` | `o` |
| `m()` irrotettuna | `undefined` |
| `m.call(x)`, `m.bind(x)` | `x` |
| nuolifunktio | ympäröivä `this` |

# Oliot ja tyypit

```{.javascript tiedosto="esimerkit/pikaopas.js" osa="oliot"}
```

| JSDoc | Tarkoitus |
|-------|-----------|
| `@param {T} x`, `@returns {T}` | funktion tyyppi |
| `@param {T} [x]` | valinnainen |
| `@typedef {{ a: number }} Nimi` | tyyppinimi |
| `@template T`, `@template {keyof T} K` | geneerisyys |
| `@import { T } from "./m.js"` | tyypin tuonti |
| `/** @type {T} */ (x)` | tyyppimuunnos |

- Kopio: `{ ...o }` matala, `structuredClone(o)` syvä.
- `Object.freeze` matala; `const` estää vain uudelleensijoituksen.
- Eroteltu unioni + `switch` + `never` = kattava käsittely.

# Kokoelmat

```{.javascript tiedosto="esimerkit/pikaopas.js" osa="kokoelmat"}
```

| Tarve | Kirjoitus |
|-------|-----------|
| muunna, valitse, kokoa | `map`, `filter`, `reduce`, `flatMap` |
| hae | `find`, `findLast`, `some`, `every`, `includes` |
| lajittele kopioiden | `toSorted((a, b) => a - b)`, `Intl.Collator("fi").compare` |
| ryhmittele | `Object.groupBy`, `Map.groupBy` |
| luo | `Array.from({ length: n }, (_, i) => i)` |
| sanakirja, joukko | `Map`, `Set`; olioavaimelle `WeakMap` |
| merkit | `[...s]`, `Intl.Segmenter`, `s.normalize()` |
| oma iteroitava | `*[Symbol.iterator]() { yield ... }` |

# Asynkronisuus

```{.javascript tiedosto="esimerkit/pikaopas.js" osa="async"}
```

```{.tuloste tiedosto="esimerkit/pikaopas.odotettu"}
```

| Tarve | Väline |
|-------|--------|
| kaikki / kaikki tulokset | `Promise.all`, `Promise.allSettled` |
| nopein / ensimmäinen onnistunut | `Promise.race`, `Promise.any` |
| peruutus, aikaraja | `AbortController`, `AbortSignal.timeout`, `.any` |
| virta riveinä | `for await (const r of readline.createInterface(...))` |
| tapahtumat | `EventEmitter`, `events.once` |
| laskenta | `worker_threads`, säiepooli |

- Järjestys: synkroninen → mikrotehtävät (lupaukset) → makrotehtävä
  (ajastin, I/O).
- Jokainen lupaus odotetaan tai `.catch`; käsittelemätön hylkäys
  kaataa Noden.

# Virheet

- `throw new Virhe(viesti, { cause })`; `this.name = new.target.name`.
- `catch (e)`: `e` on `unknown`; kavenna `instanceof`-tarkistuksella,
  heitä tuntematon eteenpäin.
- Odotettu epäonnistuminen: `{ ok: false, virhe }`, ei poikkeusta.

# Hinnat

| Halpaa | Kallista |
|--------|----------|
| kutsu, sulkeuma, lyhytikäinen olio | `delete`, vaihteleva kenttäjärjestys |
| samanmuotoiset oliot | monimuotoinen kutsukohta |
| `Map`/`Set`-haku | `includes`, `shift` suurella taulukolla |
| heittämätön `try` | heitetty poikkeus (pinojälki) |
| `await` I/O:lle | synkroninen I/O, raskas laskenta pääsäikeessä |

# Sudenkuopat

- `sort()` ilman vertailijaa lajittelee merkkijonoina.
- `||` hylkää `0`:n ja `""`:n; käytä `??`.
- `for...in` taulukolle antaa avaimet merkkijonoina.
- `0.1 + 0.2 !== 0.3`; `(1.005).toFixed(2)` on `"1.00"`.
- Unohtunut `await` palauttaa lupauksen.
- `JSON.stringify` kadottaa `Map`-, `Set`- ja `undefined`-arvot.
- Olioavain `__proto__` käyttäjän datasta: käytä `Map`-rakennetta.
