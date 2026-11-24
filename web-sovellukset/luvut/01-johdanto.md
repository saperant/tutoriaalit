# Johdanto {.runko-johdanto}

Web-sovellus on selaimessa toimiva ohjelma, jonka tila muuttuu
käyttäjän toimista ilman, että koko sivu ladataan uudelleen:
varausjärjestelmä, verkkopankki, sähköposti tai projektinhallinta.
Tämä tutoriaali opettaa rakentamaan sellaisen niin, että se on
ylläpidettävä, testattu, saavutettava ja turvallinen.

Esitietoina ovat taidot *TypeScript*, *HTML ja CSS* ja *Tietoverkot*:
tyyppijärjestelmä, semanttinen HTML ja saavutettavuuden perusteet sekä
HTTP:n ja selaimen ja palvelimen välisen liikenteen perusteet
oletetaan. Niitä ei toisteta.

Kaikki esimerkit kuuluvat samaan sovellukseen: kokoustilojen
varausjärjestelmään. Luvut etenevät periaatteista kehykseen. Ensin
selaimen omilla rajapinnoilla nähdään, mitä ongelmia kehykset
ratkaisevat, sitten samat asiat tehdään Reactilla.

## Sovellusarkkitehtuurit

Selainsovelluksen HTML voi syntyä kolmessa paikassa, ja valinta on
arkkitehtuurin tärkein päätös:

| Malli | HTML syntyy | Sopii | Hinta |
|-------|-------------|-------|-------|
| Monisivuinen (MPA) | palvelimella joka pyynnöllä | sisältösivustot, lomakepalvelut | sivulataus joka toiminnolla |
| Yksisivuinen (SPA) | selaimessa JavaScriptillä | sovellusmaiset näkymät kirjautumisen takana | iso JavaScript-paketti, hidas ensimmäinen näkymä, hakukoneet |
| Palvelinrenderöinti (SSR) + hydraatio | palvelimella, selain jatkaa | julkiset sovellukset, verkkokaupat | palvelin ja kehys monimutkaisempia |
| Staattinen generointi (SSG) | käännösvaiheessa | dokumentaatio, blogit | sisältö päivittyy vasta käännöksessä |

Tämä tutoriaali rakentaa SPA:n, koska siinä selainsovelluksen omat
ongelmat näkyvät selvimmin: tila, reititys, verkko ja fokus ovat
kokonaan sovelluksen vastuulla. Samat periaatteet pätevät SSR-kehyksiin
(Next.js, React Router, Nuxt, SvelteKit), jotka lisäävät palvelinosan.
Hyvä nyrkkisääntö: julkinen, hakukoneille näkyvä sisältö palvelimelta,
kirjautumisen takana oleva sovellus voi olla SPA. Taidossa *HTML ja
CSS* esitelty progressiivinen parantaminen on edelleen pohja: linkit ovat
linkkejä ja lomakkeet lomakkeita, vaikka JavaScript hoitaa ne.

## Työkalut

| Työkalu | Versio | Tehtävä |
|---------|--------|---------|
| Node.js | 24 LTS | kehitystyökalujen ja testien ajoympäristö |
| npm | Noden mukana | riippuvuudet ja lukitustiedosto |
| TypeScript | 7.0 | tyyppitarkistus (`tsc --noEmit`) |
| Vite | 8.3 | kehityspalvelin ja tuotantokäännös |
| React | 19.3 | käyttöliittymäkirjasto |
| Vitest | 5.1 | yksikkö- ja komponenttitestit |
| happy-dom | 21 | kevyt DOM-toteutus Noden testeihin |
| Testing Library | 16 | komponenttien testaus käyttäjän näkökulmasta |
| Playwright | 1.63 | päästä päähän -testit oikeassa selaimessa |

Valinnat on tehty niin, että riippuvuuksia on vähän ja jokainen
ratkaisee selvän ongelman. **Vite** kääntää TypeScriptin ja JSX:n
itse, eikä React tarvitse erillistä liitännäistä. **React** valittiin,
koska se on alan yleisin käyttöliittymäkirjasto ja sen malli
(komponentit, yksisuuntainen datavirta, tila) siirtyy muihin kehyksiin.
Reititin, tilanhallinta ja datan haku toteutetaan tässä itse
muutamalla kymmenellä rivillä, jotta periaate näkyy; tuotannossa
käytetään vakiintuneita kirjastoja, jotka mainitaan kunkin luvun
lopussa.

Vite ei tarkista tyyppejä vaan poistaa ne nopeasti. Tyypit tarkistaa
`tsc --noEmit` erikseen editorissa, testeissä ja CI:ssä. Asetukset
ovat samat kuin taidon *TypeScript* tiukassa tilassa, lisäksi selaimen
kirjastot ja JSX:

```{.json tiedosto="esimerkit/tsconfig.json"}
```

## Projektin rakenne

```text
esimerkit/
  index.html            sovelluksen sivu; lataa src/sovellus/main.tsx
  package.json          riippuvuudet tarkkoina versioina
  package-lock.json     koko riippuvuuspuun lukitus (commitoidaan)
  vite.config.ts        Vite ja Vitest
  playwright.config.ts  päästä päähän -testit
  turvaotsakkeet.ts     CSP ja muut tietoturvaotsakkeet
  palvelin/api.ts       pieni REST-palvelin kehitykseen ja testeihin
  src/02-dom/ ...       lukujen esimerkit ja niiden testit (*.test.ts)
  src/sovellus/         valmis sovellus
  e2e/                  Playwright-testit (*.spec.ts)
```

Riippuvuudet kiinnitetään tarkkoihin versioihin, ja
`package-lock.json` lukitsee myös epäsuorat riippuvuudet. `npm ci`
asentaa täsmälleen lukitut versiot, joten kehittäjän kone, CI ja
kehityskontti käyttävät samaa koodia:

```{.json tiedosto="esimerkit/package.json"}
```

## Esimerkkien ajaminen

```text
cd esimerkit
npm ci                    # riippuvuudet lukitustiedoston mukaan
node palvelin/api.ts      # rajapinta portissa 3001 (oma pääte)
npm run dev               # kehityspalvelin: http://localhost:5173
npm run testit            # Vitest
npm run build && npm run e2e   # tuotantokäännös ja Playwright
```

Kehityspalvelin ohjaa osoitteet `/api/...` paikalliselle palvelimelle,
jolloin selaimen näkökulmasta sovellus ja rajapinta ovat samassa
alkuperässä (luku 10). Kaikki tarkistukset ajetaan esimerkkihakemiston
Makefilellä, jota myös tutoriaalin oma testaus ja CI käyttävät:

```{.makefile tiedosto="esimerkit/Makefile"}
```

Kehityskontissa (*Web-sovellukset: esimerkit*) on valmiina Node 24 ja
Playwrightin Chromium.
