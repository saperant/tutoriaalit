# XSS syvemmin

*Web-sovellukset* näytti, miten React suojaa XSS:ltä ja missä suojaus
pettää. Tämä luku käy läpi kolme XSS:n reittiä palvelimen näkökulmasta
ja kolme puolustuskerrosta: kontekstin mukaisen koodauksen,
sisältöturvakäytännön (CSP) ja Trusted Typesin. Ne ovat erillisiä
kerroksia: kun yksi pettää, seuraava pysäyttää hyökkäyksen. Lopuksi
käsitellään skriptit, jotka sivu lataa muilta palvelimilta.

## Kolme reittiä

| Reitti | Hyötykuorma kulkee | Esimerkki |
|--------|--------------------|-----------|
| Heijastettu | pyynnön parametrissa takaisin sivulle | hakusana, virheilmoitus |
| Tallennettu | tietokannan kautta muille käyttäjille | kommentti, profiilin nimi, ladattu tiedosto |
| DOM-pohjainen | selaimessa lähteestä nieluun, ei palvelimelle | `location.hash` → `innerHTML` |

Tallennettu XSS on vakavin: yksi hyökkäys osuu jokaiseen sivun
avaajaan, myös ylläpitäjään. DOM-pohjainen on vaikein huomata,
koska hyötykuorma ei koskaan käy palvelimella: fragmentti `#...` ei
kulje HTTP-pyynnössä, joten palvelimen lokit ja palomuurit eivät
näe sitä.

Esimerkin keskustelupalstassa ovat kaikki kolme. Puolustukset
kytketään päälle asetuksilla, jotta niiden vaikutuksen voi testata
yksitellen:

```{.typescript tiedosto="esimerkit/src/03-xss/xss.ts" osa="sivu"}
```

## Koodaus kontekstin mukaan

Ensimmäinen puolustus on koodata data siihen kontekstiin, johon se
päätyy. Esimerkkien apukehyksen funktio `h` koodaa HTML-elementin
sisällön ja lainausmerkeissä olevan attribuutin:

```{.typescript tiedosto="esimerkit/src/http.ts" osa="h"}
```

Muut kontekstit tarvitsevat oman koodauksensa:

| Konteksti | Esimerkki | Koodaus |
|-----------|-----------|---------|
| HTML-sisältö | `<p>${x}</p>` | HTML-entiteetit: `& < > " '` |
| Attribuutti | `<a title="${x}">` | sama, ja arvo aina lainausmerkeissä |
| URL | `<a href="${x}">` | tarkista skeema (`https:`), sitten `encodeURIComponent` osille |
| JavaScript | `<script>let x = ${x}</script>` | `JSON.stringify` ja `<` → `\u003c`; mieluummin `data-`-attribuutti |
| CSS | `style="color: ${x}"` | sallittujen arvojen luettelo |
| DOM | `el.innerHTML = x` | `textContent`, `createElement` |

Taulukon viimeinen rivi on DOM-pohjaisen XSS:n torjunta: selaimen
puolella data asetetaan tekstinä. Mallipohjat (React, Vue, palvelimen
mallikielet) koodaavat oletuksena HTML-sisällön ja attribuutit.
Vaara on aina mallipohjan ohituksessa: `dangerouslySetInnerHTML`,
`v-html`, `|safe`, `{{{ }}}`.

## Sisältöturvakäytäntö

CSP (*Content Security Policy*) on otsake, jolla palvelin kertoo
selaimelle, mitä skriptejä sivulla saa ajaa. Vanhat sallittujen
osoitteiden listat (`script-src https://cdn.example`) on todettu
heikoiksi, koska sallituilta palvelimilta löytyy lähes aina jotain
käytettävää (JSONP-rajapintoja, vanhoja kirjastoja). Suositus on
**tiukka CSP** (*strict CSP*):

```{.typescript tiedosto="esimerkit/src/03-xss/xss.ts" osa="csp"}
```

- `'nonce-…'`: vain skriptit, joiden `nonce`-attribuutti vastaa
  otsakkeen arvoa, ajetaan. Arvo arvotaan joka vastaukselle, joten
  hyökkääjä ei voi tietää sitä. Ujutettu `<script>` ja
  tapahtuma-käsittelijä `onerror="…"` jäävät ajamatta.
- `'strict-dynamic'`: luotettu skripti saa ladata muita skriptejä.
  Tämä tekee tiukasta CSP:stä käyttökelpoisen modernien
  sovellusten kanssa.
- `object-src 'none'` ja `base-uri 'none'` sulkevat kaksi tunnettua
  ohitusta: liitännäiset ja `<base>`-elementillä vaihdettu
  skriptien perusosoite.

## Trusted Types

`require-trusted-types-for 'script'` muuttaa DOM:n vaaralliset
nielut (`innerHTML`, `outerHTML`, `document.write`, `eval`,
`script.src`) sellaisiksi, että ne hyväksyvät vain erityisiä
tyyppiolioita, eivät merkkijonoja. Olion voi luoda vain nimetty
käytäntö (`trustedTypes.createPolicy`), joka puhdistaa tai tarkistaa
arvon. Silloin jokainen DOM-sijoitus kulkee muutaman katselmoidun
käytännön kautta, eikä koodikannan jokaista `innerHTML`-kohtaa
tarvitse tarkistaa käsin.

```{.typescript tiedosto="esimerkit/e2e/xss.spec.ts" osa="tt"}
```

## Hyökkäystestit

Playwright-testi ajaa kaikki kolme reittiä neljää kokoonpanoa vastaan.
Hyökkäys onnistuu, jos sivulle ujutettu koodi asettaa muuttujan
`window.pwned`:

```{.typescript tiedosto="esimerkit/e2e/xss.spec.ts" osa="testit"}
```

Testi kirjaa jokaisen yrityksen tuloksen. Taulussa on reitti riveinä
ja kokoonpano sarakkeina; "ajettiin" tarkoittaa, että ujutettu koodi
suoritettiin selaimessa:

```{.tuloste tiedosto="esimerkit/naytos/03-xss.odotettu"}
```

Kumpikin puolustus pysäyttää hyökkäykset yksinäänkin. Sarake *vain
CSP* on syvyyspuolustus näkyvissä: koodaus on unohdettu, mutta CSP
estää kaikki kolme hyökkäystä. Silti kumpaakaan ei jätetä
pois. CSP ei estä HTML-injektiota (väärennetty kirjautumislomake
sivun keskellä toimii ilman skriptiä), ja koodaus voi pettää yhdessä
paikassa sadoista.

Saman palstan saa omaan selaimeen komennolla `make kokeile`
hakemistossa `esimerkit`. Se käynnistää haavoittuvan version
osoitteeseen `127.0.0.1` ja tulostaa osoitteet, joilla kutakin reittiä
voi kokeilla. `make kokeile PUOLUSTUS="csp"` kytkee CSP:n päälle,
jolloin selaimen kehittäjätyökalujen konsolissa näkyy, minkä skriptin
käytäntö esti.

## Kolmannen osapuolen skriptit ja SRI

Sivun oma koodi ei ole ainoa skriptien lähde. Analytiikka,
maksupainikkeet, chat-ikkunat ja CDN:stä ladatut kirjastot ajetaan
sivun alkuperässä samoin oikeuksin kuin oma koodi: ne voivat lukea
lomakkeet ja lähettää pyyntöjä käyttäjän nimissä. Jos jakelupalvelin
murretaan tai kirjaston ylläpitäjä vaihtuu, muutettu skripti päätyy
jokaisen sivuston jokaiselle käyttäjälle. Näin on käynyt useita
kertoja; tunnetuin tapaus on verkkokauppojen maksusivuille ujutettu
kortinlukukoodi.

**SRI** (*Subresource Integrity*) sitoo ladattavan tiedoston sisältöön.
Sivu ilmoittaa `integrity`-määritteessä tiedoston tiivisteen, ja selain
jättää skriptin ajamatta, jos ladattu sisältö ei vastaa sitä:

```{.typescript tiedosto="esimerkit/src/03-xss/sri.ts" osa="sri"}
```

Määrite `crossorigin="anonymous"` on pakollinen toisen alkuperän
tiedostolle: selain tarkistaa tiivisteen vain, jos palvelin sallii
vastauksen lukemisen CORS-otsakkeella. Testissä "CDN" on toisessa
osoitteessa ja jakaa joko alkuperäisen tai muutetun kirjaston:

```{.typescript tiedosto="esimerkit/e2e/sri.spec.ts" osa="testi"}
```

```{.tuloste tiedosto="esimerkit/naytos/03-sri.odotettu"}
```

SRI sopii tiedostoille, joiden sisältö on kiinnitetty versioon. Se ei
sovi skripteille, joita toimittaja päivittää samassa osoitteessa
(useimmat analytiikka- ja maksuskriptit). Niiden riski rajataan
toisin: skripti ladataan vain sivuille, joilla sitä tarvitaan,
maksulomake eristetään toimittajan omaan kehykseen, ja kirjastot
jaetaan mieluiten omalta palvelimelta, jolloin ne kulkevat saman
katselmoinnin ja riippuvuuksien tarkistuksen läpi kuin muu koodi
(*Tietoturva kehitystyössä*).

## Käytännössä

- **Koodaus mallipohjalla, tekstinä DOM:iin.** Käsin kootut
  HTML-merkkijonot ovat XSS:n yleisin lähde. Jos HTML:ää on pakko
  näyttää (rikastettu teksti), se puhdistetaan DOMPurifylla tai
  palvelimella sallittujen elementtien luettelolla.
- **Tiukka CSP noncella** heti projektin alussa. Jälkikäteen
  käyttöönotto on työlästä, koska inline-skriptit ja
  tapahtumakäsittelijät on siirrettävä. Aloita tilalla
  `Content-Security-Policy-Report-Only`, kerää rikkomukset ja kiristä.
- **Trusted Types** suurissa koodikannoissa: nielut keskittyvät
  muutamaan käytäntöön, joiden katselmointi riittää.
- **`HttpOnly`-eväste** rajaa XSS:n vahinkoa: skripti ei voi lukea
  istuntotunnistetta. Se ei estä skriptiä tekemästä pyyntöjä
  käyttäjän nimissä, joten se ei korvaa XSS:n torjuntaa.
- **Kolmannen osapuolen skriptit ovat omaa koodia.** Kiinnitä versio
  ja `integrity`, tai jaa kirjasto itse. Mitä vähemmän vieraita
  skriptejä kirjautumis- ja maksusivuilla, sen parempi.
- **Hinta:** nonce vaatii, että HTML luodaan joka pyynnölle (ei
  staattista välimuistia sellaisenaan). CDN:llä nonce lisätään
  reunapalvelimella, tai käytetään tiivisteisiin perustuvaa CSP:tä
  (`'sha256-…'`) staattisille skripteille.

## Itsearviointi

- Osaat erottaa heijastetun, tallennetun ja DOM-pohjaisen XSS:n ja
  selittää, miksi DOM-pohjainen ei näy palvelimen lokeissa.
- Osaat valita oikean koodauksen kontekstin mukaan.
- Osaat kirjoittaa tiukan CSP:n noncella ja selittää `strict-dynamic`-,
  `object-src`- ja `base-uri`-direktiivien merkityksen.
- Osaat kertoa, mitä Trusted Types muuttaa DOM-rajapinnoissa.
- Osaat kirjoittaa Playwright-testin, joka todentaa XSS-suojauksen.
- Osaat kertoa, mitä SRI takaa, mitä se vaatii palvelimelta ja milloin
  se ei sovi.
