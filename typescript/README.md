# TypeScript

Tiivis suomenkielinen TypeScript-tutoriaali JavaScriptiä osaavalle:
tyyppijärjestelmä suunnittelun välineenä. Esimerkit on testattu
TypeScript 7.0:lla tiukassa tilassa ja ajettu Node.js:llä, joka poistaa
tyypit ajossa. Valmiit dokumentit: [typescript.pdf](https://saperant.github.io/tutoriaalit/materiaalit/typescript.pdf) ja
pikaopas [typescript-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/typescript-pikaopas.pdf).

## Sisältö

1. Johdanto – historia, tyyppien tarkistus ja poisto, työkalut
2. TypeScript kokeneelle – ajattelutapa, vastaavuudet, hinnat, vain
   poistettava syntaksi, sudenkuopat
3. Tyypit, tiukka tila ja syöte – literaalityypit, `unknown`, `any`,
   `never`, `tsconfig`, `Intl.NumberFormat`
4. Funktiot, kavennus ja asynkronisuus – tyyppivartijat, `asserts`,
   kattavuustarkistus, ylikuormitus, `Promise.all`, `Awaited`
5. Oliotyypit ja luokat – `interface` ja `type`, ylimääräiset kentät,
   `#`-kentät, tehdasmetodi
6. Unionit ja tilakoneet – erotellut unionit, `enum`in korvaajat
7. Geneerisyys ja tyyppien muuntaminen – rajoitteet, `keyof`,
   apuvälinetyypit, kuvatut ja ehdolliset tyypit
8. Kokoelmat ja datasta johdetut tyypit – `Map`, `Set`, monikot,
   `satisfies`, `as const`, `Object.keys`
9. Virheet ja ulkoisen datan jäsentäminen – `catch`, `Tulos`-tyyppi,
   jäsennys reunalla, tyyppi skeemasta, brändätyt tyypit
10. Modulit, esittelytiedostot ja projektit – `import type`, `.d.ts`,
    `@types`, projektiviittaukset
11. Työkalut ja testaus – node:test, tyyppitestit, typescript-eslint
12. Lopuksi – nyrkkisäännöt, mallit, lähteet

## Esimerkit

Hakemistossa `esimerkit/` on 36 testattua esimerkkiä. Tiedostot ovat
ES-moduleita (`package.json`), ja `tsconfig.json` sisältää samat
asetukset, joilla testaaja tarkistaa ne.

```
cd esimerkit
node 06-tilakone.ts          # yksi esimerkki
make                         # kaikkien tyyppitarkistus ja node:test-testit
```

`*.ei-kaanny.ts` -esimerkit eivät tarkoituksella läpäise
tyyppitarkistusta; rivit, joilla on merkintä `@virhe`, aiheuttavat
virheen. Kehityskontti: `.devcontainer/typescript/`.

## Rakentaminen

```
make testaa    # rakenne, tsc ja ajo kaikille esimerkeille, testit
make pdf       # typescript.pdf ja typescript-pikaopas.pdf
```
