# Verkko ja palvelimen data

Lähes kaikki sovelluksen data tulee palvelimelta. Sen käsittelyssä on
neljä vaikeaa kohtaa: vastauksen muoto ei ole taattu, pyyntö voi
epäonnistua monella tavalla, vastaukset voivat tulla väärässä
järjestyksessä, ja data vanhenee. Tämä luku rakentaa tyypitetyn
rajapinta-asiakkaan ja hookin, jotka hoitavat ne.

## Pieni REST-palvelin

Kehitystä ja testejä varten esimerkeissä on rajapinta pelkällä Noden
`http`-modulilla. Se jakaa validoinnin selaimen kanssa (luku 5) ja
palauttaa virheet HTTP-tiloina: 404 tuntemattomalle tilalle, 409
päällekkäiselle varaukselle ja 422 virheelliselle luonnokselle.
Tuotannon taustapalvelimen rakentaminen on oma taitonsa
(*Taustapalvelut*).

```{.typescript tiedosto="esimerkit/palvelin/api.ts" osa="palvelin"}
```

## Jäsennys rajapinnan reunalla

`response.json()` palauttaa tyypin `any`. Jos sen antaa sellaisenaan
`Tila[]`-tyyppiseksi, tyyppijärjestelmä valehtelee: palvelimen muutos
tai virhe näkyy vasta kaukana kaatumisena (`undefined is not a
function`). Siksi vastaus jäsennetään reunalla (*parse, don't validate*,
taito *TypeScript*), ja virhe kertoo tarkan polun:

```{.typescript tiedosto="esimerkit/src/07-verkko/skeema.ts" osa="skeema"}
```

```{.typescript tiedosto="esimerkit/src/07-verkko/asiakas.test.ts" osa="jasennys"}
```

## Tyypitetty asiakas

Asiakas kokoaa rajapinnan kutsut yhteen paikkaan. Komponentit kutsuvat
`api.haeTilat()` eivätkä tiedä osoitteita, otsakkeita tai virheiden
muotoa.

```{.typescript tiedosto="esimerkit/src/07-verkko/asiakas.ts" osa="asiakas"}
```

`fetch` hylkää lupauksen vain verkkovirheessä. HTTP-virhe (404, 500) on
onnistunut vastaus, jonka tila on tarkistettava (`response.ok`).
Asiakas muuttaa sen omaksi virhetyypikseen:

```{.typescript tiedosto="esimerkit/src/07-verkko/asiakas.ts" osa="virhe"}
```

Virheet jakautuvat kolmeen ryhmään, joita käsitellään eri tavoin:

| Virhe | Esimerkki | Käyttäjälle |
|-------|-----------|-------------|
| verkko tai aikakatkaisu | yhteys katkesi, `TypeError`, `TimeoutError` | "Yhteys katkesi", uusi yritys |
| palvelimen virhe (5xx) | 500, 503 | "Palvelussa on häiriö", uusi yritys myöhemmin |
| pyynnön virhe (4xx) | 404, 409, 422 | palvelimen viesti; uusi yritys ei auta |

Asiakkaan voi testata oikeaa palvelinta vastaan: testi käynnistää
palvelimen satunnaiseen porttiin (`listen(0)`) ja sulkee sen lopuksi.
Tällainen integraatiotesti löytää virheet, jotka mokatussa testissä
jäävät piiloon, kuten väärän osoitteen tai otsakkeen.

```{.typescript tiedosto="esimerkit/src/07-verkko/asiakas.test.ts" osa="integraatio"}
```

## Peruutus ja kilpatilanteet

Käyttäjä avaa tilan Aalto ja heti perään tilan Kivi. Jos Aallon vastaus
tulee hitaammin, se saapuu viimeisenä ja näkymä näyttää väärää tilaa.
Tämä kilpatilanne on yleisin datanhaun virhe. Ratkaisu on perua
vanhentunut pyyntö `AbortController`-oliolla efektin siivouksessa ja
hylätä sen tulos:

```{.typescript tiedosto="esimerkit/src/07-verkko/useHaku.ts" osa="haku"}
```

Hook palauttaa erotellun unionin, joten komponentti ei voi lukea dataa
tarkistamatta, onko se valmis. Peruutus myös vapauttaa yhteyden ja
säästää palvelinta. Testi ratkaisee lupaukset väärässä järjestyksessä
ja varmistaa, että uusi vastaus voittaa:

```{.typescript tiedosto="esimerkit/src/07-verkko/useHaku.test.tsx" osa="testi"}
```

## Optimistinen päivitys

Kun toiminto onnistuu lähes aina, käyttöliittymä voi näyttää sen
tuloksen heti ja korjata, jos palvelin hylkää sen. Peruutettu varaus
katoaa listasta ilman odotusta:

```{.typescript tiedosto="esimerkit/src/07-verkko/OmatVaraukset.tsx" osa="optimistinen"}
```

```{.typescript tiedosto="esimerkit/src/07-verkko/OmatVaraukset.test.tsx" osa="testi"}
```

Optimistinen päivitys sopii toimintoihin, jotka ovat peruttavissa ja
harvoin epäonnistuvia: tykkäys, merkintä luetuksi, järjestyksen muutos.
Se ei sovi maksuun tai varaukseen, jossa kilpailija voi ehtiä ensin.

## Välimuisti

Palvelimen data on aina kopio, joka vanhenee. Tuotantosovellus ei hae
samaa dataa jokaiseen näkymään uudelleen eikä toisaalta näytä
vanhentunutta dataa loputtomasti. Yleisin malli on
**stale-while-revalidate**: näytetään välimuistin data heti ja haetaan
taustalla uusi. Välimuisti tunnistaa datan avaimella (`["tila", id]`),
tietää datan iän ja mitätöi avaimet muutoksen jälkeen (varauksen
jälkeen tilan varaukset haetaan uudelleen).

Tämä on juuri se, mitä **TanStack Query** ja **SWR** tekevät: lisäksi
ne yhdistävät samanaikaiset haut, yrittävät uudelleen viiveellä ja
hakevat uudelleen, kun välilehti saa fokuksen. Luvun `useHaku` näyttää
periaatteen, mutta tuotannossa käytetään kirjastoa. Toinen suunta ovat
kehykset, jotka hakevat datan reitin yhteydessä (React Router, Next.js)
ja välttävät näin vesiputoukset (luku 11).

## Käytännössä

- **Yksi asiakas, ei `fetch`-kutsuja komponenteissa.** Osoitteet,
  otsakkeet, aikakatkaisu, virheiden muunnos ja jäsennys yhdessä
  paikassa. Asiakas annetaan komponenteille propsina tai kontekstilla,
  jolloin testit voivat antaa omansa.
- **Jäsennä reunalla.** Rajapinnan vastaus on `unknown`, kunnes se on
  tarkistettu. Tarkistuksen hinta on pieni verrattuna virheeseen, joka
  näkyy kaukana lähteestään.
- **Jokaisella pyynnöllä on aikaraja ja peruutus.** `AbortSignal.timeout`
  ja `AbortSignal.any` yhdistävät ne.
- **Lataus, virhe ja tyhjä tila ovat suunniteltuja näkymiä,** ei
  jälkikäteen lisättyjä. Virheessä kerrotaan, mitä tapahtui ja mitä
  käyttäjä voi tehdä.
- **Uudelleenyritys vain, kun se voi auttaa:** verkko ja 5xx, kasvavalla
  viiveellä. Muuttavat pyynnöt (POST) toistetaan vain, jos palvelin
  tunnistaa toistot (idempotenssiavain).
- **Hinnat.** Jokainen pyyntö maksaa edestakaisen matkan (mobiiliverkossa
  satoja millisekunteja). Turhat haut karsitaan välimuistilla, ja
  peräkkäiset haut tehdään rinnakkain.

## Itsearviointi

- Osaat kirjoittaa tyypitetyn rajapinta-asiakkaan, joka jäsentää
  vastaukset ja erottaa verkko-, palvelin- ja pyyntövirheet.
- Osaat selittää datanhaun kilpatilanteen ja estää sen
  `AbortController`-oliolla.
- Osaat toteuttaa optimistisen päivityksen palautuksineen ja tiedät,
  milloin se sopii.
- Osaat testata asiakkaan sekä oikeaa paikallista palvelinta vastaan
  että valefetchillä.
- Osaat kuvata stale-while-revalidate-välimuistin periaatteen.
