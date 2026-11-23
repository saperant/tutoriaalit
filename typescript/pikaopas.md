---
title: TypeScript
subtitle: Pikaopas kokeneelle kehittäjälle · TypeScript 7, Node.js 24
---

# Työkalut

| Tarkoitus | Komento |
|-----------|---------|
| Tarkistus | `tsc --noEmit -p .`, jatkuva `tsc -w` |
| Ajo | `node main.ts` (Node 22.18+ poistaa tyypit) |
| Testit | `node --test`, `node:assert/strict` |
| Lint | `eslint .` (typescript-eslint) |
| Kirjasto | `tsc -p tsconfig.build.json` (`declaration`) |
| Tyypit | `npm i -D @types/node@24` |

# Asetukset

| Asetus | Miksi |
|--------|-------|
| `strict` | null-tarkistus, ei implisiittistä `any`ä |
| `noUncheckedIndexedAccess` | `xs[i]` voi olla `undefined` |
| `erasableSyntaxOnly` | vain poistettava syntaksi |
| `verbatimModuleSyntax` | `import type` pakollinen tyypeille |
| `module: nodenext` | Noden ESM; `"type": "module"` |
| `allowImportingTsExtensions` | tuonnit `./x.ts` |

# Tyypit

```{.typescript tiedosto="esimerkit/pikaopas.ts" osa="tyypit"}
```

- `unknown` ulkoiselle datalle, ei `any`ä; `never` = ei arvoja.
- `const` päättelee literaalin, `let` levennetyn tyypin.
- `interface` laajennettavaksi, `type` muuhun (unionit, monikot).
- `?:` valinnainen, `readonly` vain käännösaikana, `#x` aidosti
  yksityinen.

# Unionit ja kavennus

```{.typescript tiedosto="esimerkit/pikaopas.ts" osa="unionit"}
```

| Kavennus | Esimerkki |
|----------|-----------|
| Primitiivi | `typeof x === "string"` |
| Luokka | `x instanceof Date` |
| Kenttä | `"viite" in x` |
| Erotin | `x.laji === "ympyra"` |
| Puuttuva | `x == null`, `x ?? oletus`, `x?.y` |
| Oma | `x is T`, `asserts x is T` |

```{.typescript tiedosto="esimerkit/pikaopas.ts" osa="vartijat"}
```

# Geneerisyys ja johdetut tyypit

```{.typescript tiedosto="esimerkit/pikaopas.ts" osa="geneeriset"}
```

| Tyyppi | Tulos |
|--------|-------|
| `Partial`, `Required`, `Readonly` | kentät valinnaisiksi, pakollisiksi, `readonly` |
| `Pick<T, K>`, `Omit<T, K>` | valitut kentät, muut kentät |
| `Record<K, V>` | olio avaimin `K` |
| `ReturnType`, `Parameters`, `Awaited` | funktion ja lupauksen tyypit |
| `keyof T`, `T[K]`, `typeof x` | avaimet, kentän tyyppi, arvon tyyppi |
| `(typeof A)[number]` | `as const` -taulukon alkiot |

# Data ja tyypit

| Merkintä | Tarkistaa | Tyyppi |
|----------|-----------|--------|
| `x: T = a` | kyllä | `T` |
| `a as const` | ei | literaalit, `readonly` |
| `a satisfies T` | kyllä | päätelty |
| `a as T` | **ei** | `T` (väite!) |

# enumin korvaajat

| Tarve | Malli |
|-------|-------|
| vaihtoehdot | literaaliunioni `type Taso` |
| nimi → arvo | `const O = { … } as const` |
| läpikäynti | `const T = [ … ] as const` |

# Sudenkuopat

- **Tyypit poistetaan:** `as`, `.d.ts` ja vartijat ovat lupauksia.
- **`any` leviää:** `JSON.parse`, `res.json()`, hylkäyksen syy.
- **Ylimääräiset kentät** tarkistetaan vain tuoreista literaaleista.
- **`Object.keys`** on `string[]`; käytä `entries`/`values`/`Map`.
- **Totuusarvo** ohittaa `0` ja `""`; käytä `??` ja `!== undefined`.
- **Unohtunut `await`:** lupaus on aina tosi; `no-floating-promises`.
- **Ei `enum`, `namespace`, `constructor(private x)`.**
- **`@ts-expect-error`**, ei `@ts-ignore`.
