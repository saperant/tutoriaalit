# Web-sovellukset

Selainsovellusten rakentaminen TypeScriptillä ja Reactilla:
DOM ja tapahtumat, tila ja komponentit, lomakkeet ja reducer, efektit,
verkko ja palvelimen data, reititys, testaus Vitestillä ja
Playwrightilla, tietoturva sekä suorituskyky ja saavutettavuus.
Valmis dokumentti: [web-sovellukset.pdf](web-sovellukset.pdf), pikaopas:
[web-sovellukset-pikaopas.pdf](web-sovellukset-pikaopas.pdf).

Esitiedot: taidot *TypeScript*, *HTML ja CSS* ja *Tietoverkot*.

## Esimerkit

`esimerkit/` on yksi npm-projekti (Vite 8, React 19, TypeScript 7,
Vitest 5, happy-dom, Testing Library, Playwright 1.63), jonka
esimerkkisovellus on kokoustilojen varausjärjestelmä.

```text
cd esimerkit
make            # npm ci, tyypit, Vitest, käännös, Playwright ja demo
npm run dev     # kehityspalvelin (rajapinta: node palvelin/api.ts)
```

## Rakentaminen

`make testaa` tarkistaa rakenteen ja ajaa esimerkkiprojektin kaikki
testit, `make pdf` rakentaa PDF:t.

Lisenssi: CC BY-SA 4.0.
