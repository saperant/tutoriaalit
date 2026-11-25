# Web-sovelluskehykset

Web-sovelluskehysten periaatteet vertailemalla: sama tehtävälista on
toteutettu ilman kehystä sekä Reactilla, Vuella, Angularilla ja
Sveltellä, ja kaikki viisi toteutusta läpäisevät saman
Playwright-testisarjan. Aiheina ovat renderöintimallit (virtuaalinen
DOM, muutostentunnistus, signaalit, kääntäjä), mallipohjat ja JSX,
komponentin rajapinta, tila ja reaktiivisuus, jaettu tila, kehyksestä
riippumaton testaus, palvelinrenderöinti sekä kehyksen valinta ja
elinkaari.
Valmis dokumentti: [web-sovelluskehykset.pdf](https://saperant.github.io/tutoriaalit/materiaalit/web-sovelluskehykset.pdf), pikaopas:
[web-sovelluskehykset-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/web-sovelluskehykset-pikaopas.pdf).

Esitiedot: taidot *Web-sovellukset*, *TypeScript* ja *HTML ja CSS*.

Tutoriaali opettaa pysyvät periaatteet ja kehysten rakenteen. Versiosta
riippuvat yksityiskohdat katsotaan kehysten omista dokumentaatioista:
<https://react.dev>, <https://vuejs.org>, <https://angular.dev> ja
<https://svelte.dev>.

## Esimerkit

`esimerkit/` on yksi npm-projekti, jossa on viisi toteutusta samasta
sovelluksesta (React 19, Vue 3.5, Angular 22, Svelte 5, Vite 8,
TypeScript 6.0, Playwright 1.63). Versiot on lukittu tiedostoon
`package-lock.json`. Node.js 24 LTS tai 22.

```text
cd esimerkit
make                                  # npm ci, tyypit, käännökset, testit
npx vite --config react/vite.config.ts   # kehityspalvelin (vue, svelte, paljas)
npx ng serve                          # Angularin kehityspalvelin
npx playwright test --project=vue     # selaintestit yhdelle toteutukselle
```

Hakemisto `periaatteet/` sisältää renderöintimallien pienoistoteutukset,
jotka ajetaan suoraan Nodella. Kehitysympäristö on valmiina
Dev Container -määrittelynä `.devcontainer/web-sovelluskehykset/`.

## Rakentaminen

`make testaa` tarkistaa rakenteen ja ajaa esimerkkiprojektin kaikki
testit, `make pdf` rakentaa PDF:t.

Lisenssi: CC BY-SA 4.0.
