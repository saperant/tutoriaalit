# Työkalut ja testaus {.runko-tyokalut}

## Työkaluketju

| Vaihe | Työkalu | Komento |
|-------|---------|---------|
| Tyyppitarkistus | tsc | `tsc --noEmit -p .`, jatkuva `tsc -w` |
| Ajo kehityksessä | Node | `node main.ts`, `node --watch main.ts` |
| Testit | node:test | `node --test` |
| Lint | ESLint + typescript-eslint | `eslint .` |
| Muotoilu | Prettier tai Biome | `prettier --check .` |
| Selainpaketti | Vite, esbuild | `vite build` |
| Kirjaston julkaisu | tsc | `tsc -p tsconfig.build.json` |
| Debuggaus | Node + VS Code | `node --inspect main.ts` |

Tyypit tarkistaa aina `tsc`. Rakennustyökalut (Vite, esbuild) ja Node
vain poistavat tyypit tarkistamatta niitä, joten `tsc --noEmit` ajetaan
CI:ssä erikseen. TypeScript 7:n natiivi kääntäjä tarkistaa suurenkin
projektin sekunneissa, joten tarkistus kannattaa ajaa myös ennen
committia.

Koska Node poistaa tyypit korvaamalla ne välilyönneillä, rivit ja
sarakkeet säilyvät: pinojälki ja debuggerin katkaisukohdat osuvat
lähdekoodiin ilman lähdekarttoja.

## Yksikkötestit node:testillä

Noden sisäänrakennettu testikehys riittää useimpiin projekteihin. Testit
ovat tavallisia TypeScript-tiedostoja, joten testikoodi tyyppitarkistetaan
kuten muukin koodi.

```{.typescript tiedosto="esimerkit/11-hinnasto/hinnasto.ts"}
```

```{.typescript tiedosto="esimerkit/11-hinnasto/hinnasto.test.ts"}
```

```{.typescript tiedosto="esimerkit/11-hinnasto/main.ts"}
```

```{.tuloste tiedosto="esimerkit/11-hinnasto.odotettu"}
```

Testit ajetaan komennolla:

```
node --test --test-reporter=spec 11-hinnasto/*.test.ts
```

- **`node:assert/strict`** vertaa syvästi (`deepEqual`) ja ilman
  tyyppimuunnoksia. `assert.throws(f, RangeError)` tarkistaa myös
  virheen tyypin.
- **Taulukkotesti** (`tapaukset` ja silmukka) kattaa raja-arvot
  vähällä koodilla, ja jokainen tapaus raportoidaan omana testinään.
- **Puhtaat funktiot** ovat helppoja testata. I/O pidetään reunalla
  (`main.ts`), ja logiikka testataan ilman tiedostoja tai verkkoa.
- Vitest ja Jest ovat yleisiä vaihtoehtoja, kun tarvitaan
  selainympäristöä, tilannekuvia tai rinnakkaisajoa työntekijöissä.

## Tyyppitestit

Kirjastojen ja apuvälinetyyppien tyypit ovat itsessään koodia, jota
kannattaa testata. Tyyppitesti on lause, joka kääntyy vain, jos väite
pitää:

```{.typescript tiedosto="esimerkit/11-tyyppitestit.ts"}
```

```{.tuloste tiedosto="esimerkit/11-tyyppitestit.odotettu"}
```

- `Yhtasuuri<A, B>` vertaa tyyppejä tarkasti (myös `any` ja
  valinnaisuus); tavallinen `A extends B` hyväksyisi alityypit.
- `// @ts-expect-error` vaatii, että seuraavalla rivillä *on* virhe.
  Se on parempi kuin `@ts-ignore`, joka vaientaa virheen myös silloin,
  kun sitä ei enää ole.
- Kirjastoissa käytetään valmiita apuvälineitä, kuten `expect-type` tai
  `tsd`.

## Lint ja koodin laatu

typescript-eslint käyttää tyyppitietoa sääntöihin, joita kääntäjä ei
tarkista. Hyödyllisimpiä:

| Sääntö | Löytää |
|--------|--------|
| `no-floating-promises` | Lupaus, jota ei odoteta eikä käsitellä |
| `no-misused-promises` | Lupaus ehdossa tai väärässä takaisinkutsussa |
| `switch-exhaustiveness-check` | Kattamaton unionin `switch` |
| `no-explicit-any`, `no-unsafe-*` | `any`n käyttö ja leviäminen |
| `consistent-type-imports` | Tyyppituonnit ilman `type`-merkintää |
| `no-unnecessary-condition` | Ehto, joka on tyyppien perusteella aina tosi |

Esimerkkien hakemiston `Makefile` tarkistaa kaikki esimerkit kerralla
(`tsc -p .`) ja ajaa testit. Samat vaiheet kuuluvat projektin CI:hin.

## Käytännössä

- **`tsc --noEmit` CI:hin ja ennen committia.** Ajo ilman tarkistusta on
  JavaScriptiä; tyyppivirheet eivät estä ohjelmaa käynnistymästä.
- **Testit TypeScriptillä, sama tsconfig.** Testikoodin tyyppivirheet
  ovat yhtä todellisia kuin tuotantokoodin.
- **Logiikka puhtaisiin funktioihin.** Testattava ydin ja ohut I/O-reuna
  ovat sama malli kuin muissakin kielissä (*functional core, imperative
  shell*).
- **`@ts-expect-error` eikä `@ts-ignore`.** Jos virhe on pakko vaientaa,
  vaientaminen pitää huomata, kun syy poistuu. Lisää kommenttiin syy.
- **Tyyppitietoinen lint.** Kääntäjä ei huomaa unohtunutta `await`ia;
  typescript-eslint huomaa.

## Itsearviointi

- Osaat koota TypeScript-projektin työkaluketjun ja selittää, mikä
  vaihe tarkistaa tyypit ja mikä vain poistaa ne.
- Osaat kirjoittaa node:test-yksikkötestit, mukaan lukien taulukkotestit
  ja virheiden tarkistukset.
- Osaat kirjoittaa tyyppitestin ja käyttää `@ts-expect-error`ia oikein.
- Osaat valita typescript-eslintin säännöt, jotka paikkaavat kääntäjän
  aukot.
