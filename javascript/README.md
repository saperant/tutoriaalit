# JavaScript

Tiivis suomenkielinen JavaScript-tutoriaali ohjelmoinnin perusteet
osaavalle (ES2024, Node.js 22–24). Tyypit kirjoitetaan JSDoc-kommentteihin
ja tarkistetaan TypeScript-kääntäjällä. Valmis dokumentti:
[javascript.pdf](javascript.pdf), pikaopas:
[javascript-pikaopas.pdf](javascript-pikaopas.pdf).

## Sisältö

1. Johdanto – historia, käyttökohteet, moottorit ja ympäristöt,
   ensimmäinen ohjelma
2. JavaScript kokeneelle – ajattelutapa, JSDoc-tyypit, vastaavuudet
   Pythoniin ja Javaan, hinnat, sudenkuopat
3. Arvot, tyypit ja syöte – yhtäsuuruus, `undefined` ja `null`, `??` ja
   `?.`, muunnokset, `Intl`, `readline`
4. Ohjausrakenteet ja funktiot – optio-olio, sulkeumat, moduulimalli,
   memoisaatio, `this`
5. Muisti, viitteet ja suorituskyky – kopiot, muuttumattomuus,
   vuodot, LRU, `WeakMap`, piilotetut luokat
6. Kokoelmat, iteraattorit ja merkkijonot – taulukot, lajittelu,
   `Map` ja `Set`, generaattorit, Unicode, JSON
7. Oliot, luokat ja tyypit – yksityiset kentät, prototyypit, erotellut
   unionit, geneeriset tyypit
8. Virheenkäsittely – virhehierarkia, `cause`, käsittelemätön hylkäys,
   poikkeus vai paluuarvo
9. Modulit ja paketit – ES-modulit, tehdasfunktio, `import()`,
   CommonJS, npm
10. Asynkronisuus ja rinnakkaisuus – tapahtumasilmukka, lupaukset,
    rajoitin, `AbortController`, putket, `EventEmitter`, säikeet
11. Työkalut, testaus ja laatu – `tsconfig`, ESLint, `node:test`,
    debuggaus, profilointi
12. Lopuksi – mallit, nyrkkisäännöt, hinnat, lähteet ja kirjastot

## Esimerkit

Esimerkit ovat hakemistossa [`esimerkit/`](esimerkit/). Jokainen
esimerkki on testattu: `make testaa` tarkistaa tyypit (`tsc --strict
--checkJs`), ajaa ohjelmat ja vertaa tulosteita, varmistaa että
`.ei-kaanny`-esimerkit hylätään ja `.kaatuu`-esimerkit kaatuvat, ja
ajaa `node:test`-testit.

```sh
cd esimerkit
node 03-syote.js < 03-syote.syote   # yksittäinen esimerkki
make                                # tyyppitarkistus ja testit
```

Kehityskontti (`.devcontainer/javascript/`) sisältää Node.js 24:n ja
TypeScriptin.

## Rakentaminen

```sh
make testaa   # rakenteen tarkistus ja esimerkkien testit
make pdf      # javascript.pdf ja javascript-pikaopas.pdf
```

## Lisenssi

CC BY-SA 4.0.
