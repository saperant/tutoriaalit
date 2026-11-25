# Lopuksi {.runko-lahteet}

## Nyrkkisäännöt

1. **Näkymä on tilan funktio.** Tila yhdessä paikassa, johdetut arvot
   lasketaan, päivitykset ovat muuttumattomia.
2. **Data alas, tapahtumat ylös.** Esityskomponentit saavat kaiken
   propseina; kontit omistavat tilan ja sivuvaikutukset.
3. **Tilakone erotelluksi unioniksi.** Mahdottomat tilat eivät käänny,
   ja siirtymät ovat testattavassa reducerissa.
4. **Efekti on synkronointia.** Käyttäjän toiminnot
   tapahtumankäsittelijöihin, johdetut arvot renderöintiin, ulkoinen
   tila `useSyncExternalStore`-hookilla. Jokaisella efektillä on
   siivous.
5. **Rajapinnan reunalla jäsennetään.** Yksi tyypitetty asiakas,
   aikaraja ja peruutus jokaiselle pyynnölle, virheet luokiteltuina,
   virheraja odottamattomille.
6. **URL on tilaa.** Jaettava ja palattava näkymä kuuluu osoitteeseen;
   linkit ovat `<a href>`-elementtejä.
7. **Fokus ja otsikko joka reitillä, elävät alueet muutoksille.**
8. **Tekstinä, ei koodina.** Ei `innerHTML`-ominaisuutta eikä
   `dangerouslySetInnerHTML`-propsia epäluotettavalla datalla; tiukka
   CSP; istunto `HttpOnly`-evästeessä.
9. **Testaa niin kuin käyttäjä.** Roolit ja nimet, `user-event`,
   mokattu verkko, ei odotusaikoja.
10. **Mittaa ennen optimointia.** Vähemmän koodia, rinnakkaiset haut,
    tilan sijainti ennen `memo`a.

## Mallit

| Malli | Ongelma | Luku |
|-------|---------|------|
| tapahtumien delegointi | kuuntelija jokaiselle elementille | 2 |
| näkymä tilan funktiona | DOM ja data eri tahtiin | 3 |
| signaali ja johdettu arvo | hienojakoinen päivitys | 3 |
| yksisuuntainen datavirta, tilan nostaminen | jaettu tila | 4 |
| kontti- ja esityskomponentti | testattavuus, uudelleenkäyttö | 4 |
| reducer ja eroteltu unioni | mahdottomat tilat | 5 |
| oma hook | uudelleenkäytettävä käyttäytyminen | 6 |
| debounce | pyyntö joka näppäilystä | 6 |
| tyypitetty asiakas, jäsennys reunalla | luottamus `any`-dataan | 7 |
| peruutettava haku | kilpatilanne | 7 |
| optimistinen päivitys | odotus nopeassa toiminnossa | 7 |
| virheraja | yksi renderöintivirhe tyhjentää sivun | 7 |
| stale-while-revalidate | vanha data tai turhat haut | 7 |
| URL tilana | menetetty haku, jakamaton näkymä | 8 |
| riippuvuuksien injektointi propsina | testattavuus | 8 |
| koodin pilkkominen, render-as-you-fetch | latausaika, vesiputoukset | 11 |

## Jatkotaidot

- *Web-sovelluskehykset ja niiden periaatteet*: Vue, Svelte ja Angular
  perustuvat samoihin käsitteisiin; signaalien malli on tuttu
  luvusta 3. Taito tekee saman sovelluksen Reactilla, Vuella,
  Angularilla ja Sveltellä ja vertaa niiden renderöintimalleja,
  mallipohjia ja tilanhallintaa. Sieltä löytyvät myös kehyksen valinnan
  perusteet.
- *Taustapalvelut*: rajapinnan, tietokannan, todennuksen ja
  valtuutuksen toteutus palvelimella.
- *Kontit ja pilvi-infrastruktuuri*: sovelluksen julkaisu, CDN ja
  palvelinasetukset (SPA fallback, otsakkeet).

Tuotannossa reititys, datan haku ja välimuisti tulevat kirjastoista:
React Router tai TanStack Router, TanStack Query, lomakkeisiin React
Hook Form, saavutettaviin komponentteihin React Aria tai Radix.
SSR-kehykset (Next.js, React Router, Remix) yhdistävät palvelimen ja
selaimen.

## Lähteet ja jatkolukeminen

- **MDN Web Docs** (<https://developer.mozilla.org>): DOM, Fetch,
  History, Web Storage, IndexedDB, CSP ja CORS. Sisältö on lisensoitu
  CC BY-SA 2.5 -lisenssillä.
- **React-dokumentaatio** (<https://react.dev>), erityisesti *Thinking in
  React*, *Managing State*, *You Might Not Need an Effect* ja
  *Synchronizing with Effects*. Lisenssi CC BY 4.0.
- **Vite** (<https://vite.dev>) ja **Vitest** (<https://vitest.dev>):
  asetukset, kehityspalvelimen välityspalvelin ja testiympäristöt.
  MIT-lisenssi.
- **Testing Library** (<https://testing-library.com>): ohjaavat
  periaatteet ja kyselyjen suositusjärjestys. MIT-lisenssi.
- **Playwright** (<https://playwright.dev>): lokaattorit, automaattinen
  odotus ja verkon mokkaus. Apache 2.0 -lisenssi.
- **OWASP Cheat Sheet Series** (<https://cheatsheetseries.owasp.org>):
  *Cross Site Scripting Prevention*, *Content Security Policy*,
  *Cross-Site Request Forgery Prevention* ja *HTML5 Security*.
  Lisenssi CC BY-SA 4.0.
- **web.dev** (<https://web.dev>): Core Web Vitals, koodin pilkkominen
  ja suorituskyvyn mittaus. Lisenssi CC BY 4.0.
- **ARIA Authoring Practices Guide** (<https://www.w3.org/WAI/ARIA/apg/>)
  saavutettavien komponenttien näppäimistömallit.
- **TanStack Query -dokumentaatio** (<https://tanstack.com/query>)
  palvelimen tilan ja välimuistin käsitteistä.
- **Kirjat**: Kent C. Dodds ja muut, *Epic React* -materiaalit
  (komponenttimallit ja testaus); Addy Osmani, *Learning JavaScript
  Design Patterns* (verkossa ilmaiseksi).
