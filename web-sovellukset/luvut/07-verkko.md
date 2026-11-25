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

![Kilpatilanne aikajanalla. Ilman peruutusta hitaan Aalto-pyynnön
vastaus korvaa näkymän, vaikka käyttäjä valitsi jo
Kiven.](kuvat/07-kilpatilanne.png){width=100%}

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

## Kun komponentti kaatuu

Hook `useHaku` hoitaa odotetut virheet: verkko katkeaa tai palvelin
vastaa virheellä, ja näkymä näyttää virhetilan ja tarjoaa uutta
yritystä:

![Odotettu virhe: palvelin vastasi tilalla 503. Näkymä kertoo, mitä
tapahtui, ja tarjoaa uuden yrityksen.](kuvat/07-virhe.png){width=70%}

Odottamaton virhe on ohjelmointivirhe renderöinnissä, esimerkiksi
`undefined`-arvon kentän lukeminen. Silloin React poistaa koko
komponenttipuun, ja käyttäjälle jää tyhjä sivu. **Virheraja** (*error
boundary*) rajaa vahingon: se on komponentti, joka ottaa kiinni
lastensa renderöinnissä heitetyt poikkeukset ja näyttää niiden
tilalla varanäkymän.

```{.typescript tiedosto="esimerkit/src/07-verkko/Virheraja.tsx" osa="virheraja"}
```

```{.typescript tiedosto="esimerkit/src/07-verkko/Virheraja.test.tsx" osa="testi"}
```

Testissä otsikko säilyy ja vain rajan sisäpuoli korvautuu.
`componentDidCatch` saa virheen ja komponenttipinon, ja se on oikea
paikka lähettää virhe seurantapalveluun: kehittäjä ei muuten saa
tietää käyttäjän selaimessa tapahtuneesta kaatumisesta.

- Raja ottaa kiinni vain renderöinnin ja efektien virheet. Tapahtuman
  käsittelijän ja lupauksen virheet käsitellään itse (`try`/`catch`,
  `useHaku`), koska ne eivät tapahdu renderöinnin aikana.
- Rajoja on muutama, ei yhtä eikä sataa: sovelluksen juuressa ja
  itsenäisten osien (reitti, sivupalkki, upotettu kaavio) ympärillä.
  Valmiissa sovelluksessa (luku 8) raja on reitin näkymän ympärillä, ja
  `key`-propsi nollaa sen, kun reitti vaihtuu.
- Varanäkymä kertoo, että jotain meni vikaan, ja antaa keinon jatkaa.
  Teknistä virheilmoitusta ei näytetä käyttäjälle.
- Kirjasto `react-error-boundary` tarjoaa saman valmiina
  funktiokomponenttien kanssa käytettävänä.

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
- Osaat rajata renderöintivirheen virherajalla ja kertoa, mitä
  virheitä se ei ota kiinni.
- Osaat kuvata stale-while-revalidate-välimuistin periaatteen.
