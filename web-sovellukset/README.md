# Web-sovellukset

Selainsovellusten rakentaminen TypeScriptillä ja Reactilla:
DOM ja tapahtumat, tila ja komponentit, lomakkeet ja reducer, efektit,
verkko ja palvelimen data, reititys ja saavutettavuus, testaus
Vitestillä ja Playwrightilla, tietoturva sekä suorituskyky.
Valmis dokumentti: [web-sovellukset.pdf](https://saperant.github.io/tutoriaalit/materiaalit/web-sovellukset.pdf), pikaopas:
[web-sovellukset-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/web-sovellukset-pikaopas.pdf).

Esitiedot: taidot *TypeScript*, *HTML ja CSS* ja *Tietoverkot*.
Kehysten vertailu (React, Vue, Angular, Svelte) ja niiden yhteiset
periaatteet: [Web-sovelluskehykset ja niiden periaatteet](../web-sovelluskehykset/).

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
testit, `make pdf` rakentaa PDF:t. `make kuvat` päivittää hakemiston
`kuvat/` kuvakaappaukset valmiista sovelluksesta (Playwright,
`esimerkit/kuvitus/`) ja aikajanakuvat (Matplotlib, `kuvat/piirra.py`);
kuvat ovat versionhallinnassa.

Esimerkkien avaaminen kehityskontissa ja ajaminen: ks. [Kehitysympäristöt ja Dev Containers](../kehitysymparistot/), luku 2.

Lisenssi: CC BY-SA 4.0.
