# Tietoturva selaimessa

Selainsovellus ajaa koodia käyttäjän koneella, käyttäjän istunnolla ja
käyttäjän oikeuksilla. Jos hyökkääjä saa oman skriptinsä sivulle, se voi
tehdä kaiken, mitä käyttäjä voi: lukea tiedot, lähettää pyyntöjä ja
vaihtaa salasanan. Tämä luku käy läpi tärkeimmät uhat ja niiden
torjunnan. Laajempi käsittely on taidossa *Tietoturvan perusteet*, ja
OWASP:n *Cheat Sheet Series* on hyvä tarkistuslista.

## XSS

**Sivustojen välinen komentosarja** (*cross-site scripting*, XSS) syntyy,
kun epäluotettava data päätyy sivulle koodina. Lähde voi olla
palvelimelle tallennettu kommentti (*tallennettu XSS*), URL:n parametri
(*heijastettu*) tai selaimessa käsitelty data (*DOM-pohjainen*).

React suojaa oletuksena: JSX:n lausekkeet asetetaan tekstinä, kuten
`textContent` luvussa 2. Suojaus pettää neljässä kohdassa:

| Kohta | Riski | Torjunta |
|-------|-------|----------|
| `dangerouslySetInnerHTML` | HTML suoraan DOM:iin | vältä; jos pakko, puhdista (DOMPurify) |
| `href`, `src` | `javascript:`-osoite | salli vain `https:` ja suhteelliset |
| `innerHTML`, `insertAdjacentHTML` | sama kuin yllä | `textContent`, elementit |
| `eval`, `new Function`, merkkijono `setTimeout`-kutsulle | koodi datasta | ei koskaan |

Käyttäjän kirjoittaman muotoilun voi näyttää ilman HTML:ää jäsentämällä
sen React-elementeiksi:

```{.typescript tiedosto="esimerkit/src/10-tietoturva/Kuvaus.tsx" osa="kuvaus"}
```

Lyhyt "korjaus" merkkijonolla ja `dangerouslySetInnerHTML`-propsilla
päästää läpi kaiken, mitä syötteessä on:

```{.typescript tiedosto="esimerkit/src/10-tietoturva/Kuvaus.tsx" osa="vaarallinen"}
```

```{.typescript tiedosto="esimerkit/src/10-tietoturva/Kuvaus.test.tsx" osa="testi"}
```

Päästä päähän -testi tarkistaa saman oikeassa selaimessa: rajapinnan
palauttama nimi, jossa on `onerror`-käsittelijä, näkyy tekstinä eikä
suoritu:

```{.typescript tiedosto="esimerkit/e2e/tietoturva.spec.ts" osa="xss"}
```

## Sisällön suojauskäytäntö (CSP)

CSP on toinen puolustuslinja: palvelin kertoo selaimelle otsakkeessa,
mistä skriptejä, tyylejä ja yhteyksiä saa ladata. Vaikka XSS-aukko
olisi olemassa, injektoitu inline-skripti ei suoritu. Vite tuottaa
erilliset skriptitiedostot, joten sovellus toimii tiukalla
käytännöllä ilman `'unsafe-inline'`-poikkeusta:

```{.typescript tiedosto="esimerkit/turvaotsakkeet.ts" osa="otsakkeet"}
```

Esikatselupalvelin lähettää samat otsakkeet, joten päästä päähän
-testit ajetaan tuotannon käytäntöä vastaan. Jos joku lisää
inline-skriptin tai ulkoisen kirjaston, testit epäonnistuvat heti:

```{.typescript tiedosto="esimerkit/e2e/tietoturva.spec.ts" osa="csp"}
```

Uusi käytäntö otetaan käyttöön ensin tarkkailutilassa
(`Content-Security-Policy-Report-Only` ja raportointiosoite), jotta
rikkomukset näkyvät ennen kuin ne estävät mitään.

## CORS

Selain estää skriptiä lukemasta vastausta toisesta alkuperästä
(protokolla, verkkotunnus ja portti), ellei palvelin salli sitä
CORS-otsakkeilla (`Access-Control-Allow-Origin`). Yleinen väärinkäsitys
on, että CORS suojaa palvelinta. Se suojaa käyttäjää: pyyntö lähtee
silti, ja palvelimen on tarkistettava oikeudet itse. CORS-virheen
"korjaaminen" asettamalla `Access-Control-Allow-Origin: *`
evästeiden kanssa (`credentials`) ei edes toimi, eikä sitä pidä yrittää.
Otsakkeet asetetaan palvelimella; sen puolen käsittelee taito
*Taustapalvelut*.

Yksinkertaisin ratkaisu on välttää CORS kokonaan: sovellus ja rajapinta
samasta alkuperästä, kehityksessä Viten välityspalvelimella (luku 1) ja
tuotannossa käänteisellä välityspalvelimella.

## CSRF ja istunnot

**Sivustojen välinen pyyntöväärennös** (*cross-site request forgery*)
hyödyntää sitä, että selain liittää evästeet pyyntöihin automaattisesti.
Hyökkääjän sivu voi lähettää lomakkeen sovelluksen rajapintaan, ja
pyyntö kulkee käyttäjän istunnolla. Torjunta:

- istuntoeväste asetuksin `HttpOnly; Secure; SameSite=Lax` (tai
  `Strict`), jolloin selain ei lähetä sitä toisen sivuston pyynnöissä,
- tilaa muuttavat pyynnöt vain POST-, PUT- ja DELETE-metodeilla, ei
  koskaan GET-pyynnöllä,
- tarvittaessa CSRF-tunniste tai `Origin`-otsakkeen tarkistus
  palvelimella.

Kirjautumistunnisteen säilytys on yleinen kiistakysymys. `HttpOnly`-
eväste on skriptien ulottumattomissa, joten XSS ei voi varastaa sitä.
`localStorage`en tallennettu tunniste on jokaisen sivulle päässeen
skriptin luettavissa. Suositus on siksi `HttpOnly`-eväste ja
saman alkuperän rajapinta, tai *backend for frontend* -palvelin, joka
pitää varsinaiset tunnisteet palvelimella.

## Riippuvuudet ja salaisuudet

Sovelluksen npm-riippuvuudet ajetaan samoilla oikeuksilla kuin oma
koodi. Siksi riippuvuuksia on vähän, versiot ovat lukitut
(`package-lock.json`, `npm ci`), ja päivitykset tehdään hallitusti
(Dependabot, Renovate) ja tarkistetaan (`npm audit`). Asennusskriptit
voi estää (`npm ci --ignore-scripts`), kun niitä ei tarvita.

Kaikki selainpakettiin päätyvä on julkista. Viten `VITE_`-alkuiset
ympäristömuuttujat kirjoitetaan pakettiin sellaisinaan, joten
rajapinta-avaimet ja salasanat kuuluvat vain palvelimelle.

## Käytännössä

- **Tekstinä, ei koodina.** Kaikki ulkoinen data JSX:n lausekkeiden tai
  `textContent`-ominaisuuden kautta. `dangerouslySetInnerHTML` vaatii
  perustelun ja puhdistuksen, ja koodikatselmointi kysyy sen.
- **Tiukka CSP alusta asti.** `script-src 'self'` on helppo pitää ja
  vaikea lisätä jälkikäteen. Testaa käytäntöä vastaan.
- **Selaimen tarkistukset ovat käytettävyyttä, palvelimen ovat
  tietoturvaa.** Piilotettu painike tai poissa käytöstä oleva kenttä ei
  estä ketään lähettämästä pyyntöä.
- **Istunto `HttpOnly`-evästeessä,** `SameSite` ja `Secure` päällä;
  tilaa muuttavat pyynnöt vain muilla kuin GET-metodeilla.
- **Ei salaisuuksia selaimeen.** Selainpaketti, lähdekartat ja
  ympäristömuuttujat ovat julkisia.
- **Hinta.** Tietoturva maksaa vähän, kun se on oletus (React, CSP,
  evästeasetukset), ja paljon, kun se lisätään jälkikäteen.

## Itsearviointi

- Osaat selittää XSS:n tyypit ja ne kohdat, joissa Reactin suojaus ei
  auta.
- Osaat näyttää käyttäjän muotoilun ilman HTML:ää.
- Osaat kirjoittaa tiukan CSP:n ja testata, että sovellus toimii sen
  kanssa ja että se estää inline-skriptin.
- Osaat selittää CORS:n ja CSRF:n eron ja valita istunnon säilytystavan.
- Osaat hallita riippuvuuksien ja ympäristömuuttujien riskit.
