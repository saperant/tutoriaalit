# Tietoturvatestaus

Tietoturva, jota ei testata, rapautuu: uusi reitti ilman
valtuutustarkistusta, poistettu otsake tai kirjastopäivitys, joka
muuttaa oletusta. Tämä luku kokoaa testauksen tavat ja sen, mihin
kohtaan kehitystä kukin kuuluu.

## Testauksen tasot

| Taso | Mitä | Milloin | Esimerkki |
|------|------|---------|-----------|
| Yksikkötesti | politiikka, validointi, tokenin tarkistus | jokainen muutos | luvut 6, 9, 10 |
| Hyökkäystesti | tunnettu hyökkäys haavoittuvaa ja korjattua vastaan | jokainen muutos | luvut 2–11 |
| Selaintesti | selaimen käytäntöjen kanssa toimivat suojaukset | jokainen muutos | XSS, CSRF, WebAuthn |
| SAST | lähdekoodin staattinen analyysi | jokainen muutos | Semgrep, CodeQL, ESLint-säännöt |
| Riippuvuuksien tarkistus | tunnetut haavoittuvuudet kirjastoissa | jokainen muutos ja päivittäin | `npm audit`, Dependabot |
| DAST | käynnissä oleva sovellus ulkoapäin | säännöllisesti, ennen julkaisua | OWASP ZAP |
| Tunkeutumistestaus | ihminen etsii logiikkavirheitä | ennen julkaisua, vuosittain | ulkoinen testaaja |

Tämän tutoriaalin esimerkit ovat hyökkäystestejä: jokainen
haavoittuvuus on testi, joka epäonnistuu, jos korjaus poistetaan.
Löydetystä haavoittuvuudesta kirjoitetaan sama testi ennen korjausta,
jotta se ei palaa (*regressiotesti*).

## Selaintestit

Monet suojaukset ovat selaimen toimintaa: CSP:n noudattaminen,
SameSite-evästeet, kehysten esto ja WebAuthnin alkuperätarkistus.
Niitä ei voi testata pelkällä HTTP-asiakkaalla, koska asiakas ei
noudata selaimen sääntöjä. Playwright-testit (luvut 3, 4 ja 7) ajavat
hyökkäykset oikeassa selaimessa kahden eri sivuston välillä.

## Dynaaminen skannaus

DAST-työkalu lähettää käynnissä olevalle sovellukselle pyyntöjä ja
etsii vastauksista tunnettuja puutteita: puuttuvia otsakkeita,
heijastuvia parametreja, evästeiden lippuja ja virheilmoituksia.
Esimerkin pieni skanneri näyttää periaatteen:

```{.typescript tiedosto="esimerkit/src/12-testaus/skanneri.ts" osa="skanneri"}
```

```{.typescript tiedosto="esimerkit/src/12-testaus/skanneri.test.ts" osa="testi"}
```

Korjatussakin palstassa skanneri muistuttaa kahdesta puuttuvasta
otsakkeesta: palsta torjuu XSS:n, mutta ei asettanut luvun 11 otsakkeita.
Juuri tällaiset puutteet skannaus löytää halvalla. OWASP ZAP tekee
saman perusteellisesti, ja sen voi ajaa CI:ssä testiympäristöä vastaan
(*baseline scan* passiivisesti, *full scan* aktiivisilla hyökkäyksillä
vain omassa testiympäristössä).

## Mitä automaatio ei löydä

Skannerit ja staattinen analyysi löytävät tunnetut kaavat. Ne eivät
ymmärrä sovelluksen logiikkaa: voiko alennuskoodin käyttää kahdesti
rinnakkaisilla pyynnöillä, voiko tilauksen summan muuttaa negatiiviseksi,
näkeekö tiimin entinen jäsen vielä tiimin tiedostot. Nämä löytyvät
uhkamallinnuksesta (*Tietoturvan perusteet*), valtuutustesteistä
(luku 10) ja ihmisen tekemästä testauksesta.

## Käytännössä

- **Jokainen löydös testiksi** ennen korjausta.
- **Valtuutuksen taulukkotestit**: roolit × rajapinnat × odotettu tila.
- **Selaintestit** suojauksille, jotka ovat selaimen toimintaa.
- **SAST ja riippuvuuksien tarkistus jokaisessa muutoksessa**, DAST
  säännöllisesti testiympäristöön. Prosessista tarkemmin taidossa
  *Tietoturva kehitystyössä*.
- **Hinta:** hyökkäystestit ovat yhtä nopeita kuin muut testit (tämän
  tutoriaalin kaikki testit vievät sekunteja). DAST-ajo kestää minuutteja
  tai tunteja, joten se ajetaan erillään tavallisista testeistä.

## Itsearviointi

- Osaat sijoittaa tietoturvatestauksen tasot kehitysprosessiin.
- Osaat kirjoittaa hyökkäystestin, joka ajaa saman hyökkäyksen
  haavoittuvaa ja korjattua versiota vastaan.
- Osaat perustella, milloin testi vaatii oikean selaimen.
- Osaat kertoa, mitä dynaaminen skannaus löytää ja mitä se ei löydä.
