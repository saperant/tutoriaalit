# JavaScript

Tiivis suomenkielinen JavaScript-tutoriaali ohjelmoinnin perusteet
osaavalle (ES2025, Node.js 22–24). Tyypit kirjoitetaan JSDoc-kommentteihin
ja tarkistetaan TypeScript-kääntäjällä. Valmis dokumentti:
[javascript.pdf](https://saperant.github.io/tutoriaalit/materiaalit/javascript.pdf), pikaopas:
[javascript-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/javascript-pikaopas.pdf).

## Sisältö

1. Johdanto – historia, käyttökohteet, moottorit ja ympäristöt,
   ensimmäinen ohjelma
2. JavaScript kokeneelle – ajattelutapa, JSDoc-tyypit ja `tsconfig`,
   vastaavuudet Pythoniin ja Javaan, hinnat, sudenkuopat
3. Arvot, tyypit ja syöte – yhtäsuuruus, `undefined` ja `null`, `??` ja
   `?.`, muunnokset, `Intl`, aika ja päivämäärät, `readline`
4. Ohjausrakenteet ja funktiot – optio-olio, sulkeumat, moduulimalli,
   memoisaatio, `this`
5. Muisti, viitteet ja suorituskyky – kopiot, muuttumattomuus,
   vuodot, LRU, `WeakMap`, piilotetut luokat
6. Kokoelmat, iteraattorit ja merkkijonot – taulukot, lajittelu,
   `Map` ja `Set`, generaattorit ja iteraattorien apumetodit, Unicode,
   säännölliset lausekkeet, JSON
7. Oliot, luokat ja tyypit – olioliteraali ja purkaminen, yksityiset
   kentät, prototyypit, erotellut unionit, geneeriset tyypit
8. Virheenkäsittely – virhehierarkia, `cause`, resurssien vapautus
   (`using`), käsittelemätön hylkäys, poikkeus vai paluuarvo
9. Modulit ja paketit – ES-modulit, tehdasfunktio, `import()`,
   CommonJS, npm
10. Asynkronisuus ja rinnakkaisuus – tapahtumasilmukka, lupaukset,
    rajoitin, `AbortController`, putket, tiedostot, `EventEmitter`,
    säikeet
11. Työkalut, testaus ja laatu – tyyppitarkistus, JSDoc
    dokumentaationa, ESLint, `node:test`, debuggaus, profilointi
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

Esimerkkien avaaminen kehityskontissa ja ajaminen: ks.
[Kehitysympäristöt ja Dev Containers](../kehitysymparistot/), luku 2.

## Lisenssi

CC BY-SA 4.0.
