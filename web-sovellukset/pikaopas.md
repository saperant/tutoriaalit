---
title: Web-sovellukset
subtitle: Pikaopas · React, tila, verkko, testaus ja tietoturva
---

# Komennot

| Komento | Tehtävä |
|---------|---------|
| `npm ci` | riippuvuudet lukitustiedoston mukaan |
| `npm run dev` | kehityspalvelin, `/api` välitetään eteenpäin |
| `npx tsc --noEmit -p .` | tyyppitarkistus (Vite ei tarkista) |
| `npx vitest run` / `npx vitest` | testit kerran / tarkkailutila |
| `npm run build`, `npm run preview` | tuotantokäännös ja esikatselu |
| `npx playwright test --ui` | päästä päähän -testit ja niiden selain |

# Hookit

| Hook | Käyttö | Sudenkuoppa |
|------|--------|-------------|
| `useState` | paikallinen tila | päivitys ei näy heti; `set(x => …)` |
| `useReducer` | tilakone, monta kenttää | reducer puhtaaksi |
| `useEffect` | synkronointi ulkoiseen | siivous, rehelliset riippuvuudet |
| `useRef` | DOM-elementti, ei-näkyvä arvo | muutos ei renderöi |
| `useMemo` / `useCallback` | raskas arvo / vakaa funktio | vain mitattuun ongelmaan |
| `useContext` | jaettu harvoin muuttuva arvo | muutos renderöi kaikki lukijat |
| `useSyncExternalStore` | URL, storage, ulkoinen tila | tilannekuva vakaaksi |
| `lazy` + `Suspense` | koodin pilkkominen | oletusvienti |

Ei hookeja ehtolauseissa. Johdettu arvo renderöinnissä, käyttäjän
toiminnon seuraus käsittelijässä, tilan nollaus `key`-propsilla.

# Komponentti

```{.typescript tiedosto="esimerkit/src/04-react/TilaLista.tsx" osa="lista"}
```

`key` vakaasta tunnisteesta, ei indeksistä. `{lkm > 0 && …}`, ei
`{lkm && …}`.

# Haku

```{.typescript tiedosto="esimerkit/src/07-verkko/useHaku.ts" osa="haku"}
```

| Virhe | Tunniste | Uusi yritys |
|-------|----------|-------------|
| verkko, aikaraja | `TypeError`, `TimeoutError` | kyllä |
| palvelin | 5xx | kyllä, viiveellä |
| pyyntö | 4xx | ei; näytä viesti |
| renderöinti | poikkeus komponentissa | virheraja + varanäkymä |

# Testaus

| Testing Library | Playwright |
|-----------------|------------|
| `getByRole("button", { name })` | `page.getByRole(…)` |
| `getByLabelText("Aihe")` | `page.getByLabel("Aihe")` |
| `findByRole` (odottaa) | `await expect(l).toBeVisible()` |
| `queryBy…` → `null` | `not.toBeVisible()` |
| `userEvent.setup()`, `type`, `click` | `fill`, `click`, `goBack` |
| `vi.useFakeTimers()`, `act` | `page.route(url, r => r.fulfill(…))` |

# Tietoturva

| Uhka | Torjunta |
|------|----------|
| XSS | JSX-lausekkeet ja `textContent`; ei `dangerouslySetInnerHTML` |
| injektoitu skripti | CSP `script-src 'self'` |
| CSRF | `SameSite`-eväste, muutokset POST/PUT/DELETE |
| istunnon varkaus | `HttpOnly; Secure` -eväste, ei `localStorage` |
| riippuvuudet | lukitus, `npm ci`, `npm audit` |
| salaisuudet | ei selaimeen; `VITE_`-muuttujat ovat julkisia |

# Saavutettavuus ja suorituskyky

Reitillä: fokus `h1`-otsikkoon (`tabIndex={-1}`) ja `document.title`.
Muutokset: `aria-live="polite"`, virheet `role="alert"`. Mittarit
LCP enintään 2,5 s, INP 200 ms ja CLS 0,1. Riippumattomat haut
`Promise.all`; pilko reittien rajoilta; tila alas ennen `memo`a.
