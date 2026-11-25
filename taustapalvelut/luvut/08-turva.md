# Todennus ja valtuutus

*Todennus* (*authentication*) selvittää, kuka pyytää. *Valtuutus*
(*authorization*) päättää, saako hän tehdä sen, mitä pyytää. Virheet
näkyvät eri tilakoodeina: 401 "en tiedä, kuka olet" ja 403 "tiedän,
mutta et saa". OWASP:n API-tietoturvan kymmenen kärjessä on vuodesta
toiseen *Broken Object Level Authorization*: käyttäjä on todennettu,
mutta palvelu ei tarkista, kuuluuko pyydetty olio hänelle.

## Suodatinketju

Spring Security on joukko servlet-suodattimia, jotka ajetaan ennen
ohjainta. Pyyntö voi pysähtyä kolmessa kohdassa: todennuksessa (401),
polkusäännöissä (403) ja palvelussa, jossa tarkistetaan, kuuluuko
pyydetty olio käyttäjälle (403):

```{.dot otsikko="Pyynnön kulku turvaketjussa ja kohdat, joissa se voi päättyä"}
digraph {
  rankdir=LR; nodesep=0.35; ranksep=0.35;
  alku [shape=point, width=0.05];
  todennus [label="todennus"];
  polku [label="polku-\nsäännöt"];
  ohjain [label="ohjain,\npalvelu"];
  olio [label="olion tason\nvaltuutus"];
  vastaus [label="vastaus", shape=plaintext];
  node [color="#B4532A", fontcolor="#B4532A"];
  e401 [label="401\nkuka olet?"];
  e403a [label="403\nei roolia"];
  e403b [label="403\nei sinun"];
  alku -> todennus [label="pyyntö"];
  todennus -> polku -> ohjain -> olio -> vastaus;
  edge [color="#B4532A", fontcolor="#B4532A"];
  todennus -> e401;
  polku -> e403a;
  olio -> e403b;
  {rank=same; todennus; e401;}
  {rank=same; polku; e403a;}
  {rank=same; olio; e403b;}
}
```

Ketju määritellään yhtenä papuna, ja säännöt luetaan ylhäältä alas;
ensimmäinen osuva sääntö ratkaisee.

```{.java tiedosto="esimerkit/kauppa/src/main/java/fi/tutoriaalit/kauppa/turva/TurvaAsetukset.java" osa="ketju"}
```

Ketjun valinnat:

- **Oletus kieltää.** Viimeinen sääntö `anyRequest().authenticated()`
  kattaa kaikki polut, joita ei ole erikseen avattu. Uusi ohjain on
  siis suojattu, vaikka sääntöjä unohdettaisiin päivittää.
- **HTTP Basic** lähettää tunnuksen ja salasanan jokaisessa pyynnössä
  (Base64-koodattuna, ei salattuna). Se on hyväksyttävää vain TLS:n
  yli ja palvelujen välillä tai esimerkeissä; käyttäjille käytetään
  tokeneita (alla).
- **Tilaton.** Istuntoa ei luoda, joten jokainen pyyntö todennetaan
  erikseen ja mikä tahansa palvelininstanssi voi käsitellä sen.
- **CSRF pois, koska evästeitä ei ole.** *Cross-site request forgery*
  hyödyntää sitä, että selain liittää evästeen automaattisesti
  pyyntöön toiselta sivustolta. Kun tunnistautuminen kulkee
  `Authorization`-otsakkeessa, selain ei lisää sitä itse. Jos
  rajapinta käyttää istuntoevästettä, CSRF-suoja pidetään päällä.

Testi tarkistaa ketjun ilman tietokantaa: `@WithMockUser` asettaa
todennetun käyttäjän suoraan.

```{.java tiedosto="esimerkit/kauppa/src/test/java/fi/tutoriaalit/kauppa/tuote/TuoteOhjainTest.java" osa="valtuutus"}
```

## Salasanat

Salasanaa ei tallenneta eikä salata vaan siitä tallennetaan
*hidas, suolattu tiiviste*: bcrypt, scrypt tai Argon2. Hitaus on
tarkoituksellista. Bcryptin kustannuskerroin 10 vie noin 50–100 ms
tarkistusta kohden, mikä ei haittaa kirjautumista mutta tekee
vuotaneen tiivistekannan läpikäynnistä kallista. SHA-256 on tähän
väärä valinta, koska se on nopea.

```{.java tiedosto="esimerkit/kauppa/src/main/java/fi/tutoriaalit/kauppa/turva/TurvaAsetukset.java" osa="salasanat"}
```

Delegoiva kooderi tallentaa algoritmin tunnuksen tiivisteen eteen
(`{bcrypt}$2a$10$...`). Kun kustannusta nostetaan tai algoritmi
vaihdetaan, vanhat tiivisteet toimivat edelleen ja päivitetään
seuraavalla kirjautumisella. Kirjautumisyritysten määrä rajataan
(tilapäinen esto tai viive), ja virheviesti on sama väärälle
tunnukselle ja väärälle salasanalle, jotta tunnusten olemassaoloa ei
voi kokeilla.

## Istunto vai token

| | Istunto (eväste) | Token (`Authorization: Bearer`) |
|-|------------------|-------------------------------|
| Tila | palvelimella (istuntovarasto) | tokenissa itsessään |
| Mitätöinti | heti: poista istunto | vasta vanhenemisen jälkeen |
| CSRF | suojattava | ei koske |
| XSS | `HttpOnly`-evästettä ei voi lukea | selaimen tallennus luettavissa |
| Sopii | perinteinen selainsovellus | mobiili, palvelujen välinen |

Tuotannossa tokenin myöntää yleensä erillinen tunnistuspalvelu
(Keycloak, Entra ID, Auth0, Cognito) OAuth 2.0- ja OpenID Connect
-protokollilla. Taustapalvelu on silloin *resurssipalvelin*: se ei
näe salasanoja lainkaan vaan tarkistaa tokenin allekirjoituksen
palvelun julkisella avaimella. Spring Bootissa tämä on starter
`spring-boot-starter-oauth2-resource-server`, asetus
`spring.security.oauth2.resourceserver.jwt.issuer-uri` ja ketjussa
`.oauth2ResourceServer(o -> o.jwt(...))` HTTP Basicin tilalla. Muu
ketju ja valtuutus pysyvät samoina. Esimerkkipalvelu todentaa HTTP
Basicilla, jotta sen voi käynnistää ilman tunnistuspalvelua, mutta
tokenin tarkistus on mukana omana luokkanaan.

JWT (*JSON Web Token*) on kolme Base64url-koodattua osaa: otsake
(algoritmi), väitteet (*claims*) ja allekirjoitus. Väitteistä
tärkeimmät ovat myöntäjä (`iss`), käyttäjä (`sub`), yleisö (`aud`, eli
mille palvelulle token on tarkoitettu) ja vanheneminen (`exp`).
Tarkistin hyväksyy tokenin vain, jos kaikki neljä asiaa täsmäävät:

```{.java tiedosto="esimerkit/kauppa/src/main/java/fi/tutoriaalit/kauppa/turva/Tokenit.java" osa="tarkistin"}
```

Tuotannossa julkinen avain haetaan tunnistuspalvelun osoitteesta
(`issuer-uri`), ja Spring Boot rakentaa saman tarkistimen asetuksista.
Testissä tunnistuspalvelua esittää testi itse: se luo avainparin ja
allekirjoittaa tokenit. Kelvollisesta tokenista luetaan käyttäjä ja
roolit:

```{.java tiedosto="esimerkit/kauppa/src/test/java/fi/tutoriaalit/kauppa/turva/TokenTest.java" osa="kelvollinen"}
```

```{.java tiedosto="esimerkit/kauppa/src/main/java/fi/tutoriaalit/kauppa/turva/Tokenit.java" osa="roolit"}
```

Olennaisempaa on, mitä tarkistin hylkää. Jokainen testi muuttaa
kelvollisesta tokenista yhden asian:

```{.java tiedosto="esimerkit/kauppa/src/test/java/fi/tutoriaalit/kauppa/turva/TokenTest.java" osa="hylatyt"}
```

Testit vastaavat JWT:n tunnettuja sudenkuoppia:

- **Allekirjoitus tarkistetaan aina ja algoritmi kiinnitetään.**
  Allekirjoittamaton token (`alg: none`) ja algoritmin vaihto
  symmetriseksi ovat tunnettuja hyökkäyksiä kirjastoja vastaan, jotka
  uskovat tokenin omaa otsaketta. Tarkistin hyväksyy vain RS256:n.
- **Vanheneminen** (`exp`) on lyhyt (minuutteja), koska tokenia ei voi
  perua. Pitkäikäinen pääsy hoidetaan päivitystokenilla (*refresh
  token*), jonka tunnistuspalvelu voi perua.
- **Yleisö** (`aud`) ja **myöntäjä** (`iss`) tarkistetaan, jotta toiselle
  palvelulle myönnetty token ei kelpaa.
- **Token ei ole salattu**, vain allekirjoitettu. Siihen ei laiteta
  luottamuksellista tietoa.

Allekirjoitusten ja avainten taustat ovat taidossa *Kryptografia*,
kirjautumisen periaatteet taidossa *Tietoturvan perusteet* ja
palvelujen väliset tokenit taidossa *Palveluarkkitehtuurin
tietoturva*.

## Olion tason valtuutus

Polkusäännöt eivät riitä: jokainen asiakas saa kutsua
`GET /api/v1/tilaukset/{id}`, mutta vain omalla tilauksellaan.
Tarkistus tehdään palvelussa, jossa olio on käsillä.
*Menetelmätason valtuutus* tekee sen deklaratiivisesti:
`@PostAuthorize` tarkistaa palautetun olion.

```{.java tiedosto="esimerkit/kauppa/src/main/java/fi/tutoriaalit/kauppa/tilaus/TilausPalvelu.java" osa="valtuutus"}
```

```{.java tiedosto="esimerkit/kauppa/src/test/java/fi/tutoriaalit/kauppa/tilaus/TilausIntegraatioTest.java" osa="omistaja"}
```

Vieraan tilauksen pyyntö saa 403. Joskus halutaan mieluummin 404, jotta
ulkopuolinen ei saa tietää, että tilaus on olemassa; silloin omistaja
lisätään hakuehtoon (`findByIdAndAsiakas`). Listauksissa sama periaate
on pakollinen: omat tilaukset haetaan ehdolla `asiakas = ?`, eikä
kaikkia hakea ja suodattaa sovelluksessa.

## CORS

Selain estää JavaScriptiä lukemasta vastauksia toisesta *alkuperästä*
(protokolla, isäntä ja portti), ellei palvelin salli sitä CORS-otsakkeilla.
Kun selainsovellus `http://localhost:5173` kutsuu rajapintaa
`https://api.kauppa.example`, palvelimen on sallittava alkuperä:

```{.java tiedosto="esimerkit/kauppa/src/main/java/fi/tutoriaalit/kauppa/turva/TurvaAsetukset.java" osa="cors"}
```

Pavun nimi on osa sopimusta: ketjun `.cors(withDefaults())` etsii
pavun nimeltä `corsConfigurationSource`. Toisella nimellä asetukset
jäisivät käyttämättä ilman virheilmoitusta, ja siksi niiden vaikutus
kannattaa varmistaa testillä.

Ennen varsinaista pyyntöä selain kysyy luvan *esipyynnöllä*
(*preflight*): `OPTIONS`-pyyntö kertoo alkuperän, aiotun metodin ja
otsakkeet. Esipyyntö tehdään, kun metodi on muu kuin GET, HEAD tai
POST, sisältötyyppi muu kuin lomakkeiden tavallinen (kuten JSON) tai
pyynnössä on omia otsakkeita, kuten `Authorization` tai
`Idempotency-Key`. Käytännössä siis lähes jokaiselle rajapintakutsulle. Spring vastaa esipyyntöön
asetusten perusteella ennen todennusta, koska selain ei liitä siihen
tunnistetietoja:

```{.java tiedosto="esimerkit/kauppa/src/test/java/fi/tutoriaalit/kauppa/tuote/TuoteOhjainTest.java" osa="cors"}
```

CORS ei ole pääsynvalvontaa: se rajoittaa vain selaimia, ja `curl` ohittaa
sen. Se estää vierasta sivustoa käyttämästä käyttäjän selainta
rajapinnan lukemiseen. Sallittu lista on tarkka; `*` yhdessä
tunnistetietojen kanssa on virhe, jonka Spring torjuu.

Tämä on CORSin palvelinpuoli. Selaimen näkökulma (miltä CORS-virhe
näyttää sovelluksessa ja miten CORSin voi välttää kokonaan
tarjoamalla sovelluksen ja rajapinnan samasta alkuperästä)
käsitellään taidossa *Web-sovellukset*, ja selainpuolen hyökkäykset
(XSS, CSRF, CSP) taidossa *Web-sovellusten tietoturva*.

## Käytännössä

- **Oletus kieltää**: avaa polut erikseen, suojaa loput.
- **Olion tason tarkistus jokaisessa haussa ja listauksessa.**
  Polkusääntö "asiakas saa hakea tilauksia" ei kerro, *mitä*
  tilauksia.
- **Hidas salasanatiiviste** (bcrypt, Argon2) ja delegoiva kooderi.
  Ei omia tiivistefunktioita, ei salausta.
- **Tunnistuspalvelu tuotannossa.** Oma kirjautumisen, salasanan
  palautuksen ja monivaiheisen tunnistautumisen toteutus on suuri ja
  riskialtis työ; OIDC-palvelu hoitaa sen.
- **Lyhytikäiset tokenit**, tarkistettu allekirjoitus, myöntäjä ja
  yleisö.
- **Hinta:** bcrypt maksaa kymmeniä millisekunteja prosessoriaikaa
  jokaisessa tarkistuksessa. HTTP Basic tarkistaa salasanan *jokaisessa
  pyynnössä*, mikä on yksi syy käyttää tokeneita: JWT:n
  allekirjoituksen tarkistus kestää mikrosekunteja.

## Itsearviointi

- Osaat erottaa todennuksen ja valtuutuksen sekä 401:n ja 403:n.
- Osaat määritellä Spring Securityn suodatinketjun ja perustella
  tilattomuuden ja CSRF-valinnan.
- Osaat tallentaa salasanat oikein.
- Osaat kertoa, mitä resurssipalvelin tarkistaa JWT-tokenista, ja
  testata tarkistuksen itse myönnetyillä tokeneilla.
- Osaat toteuttaa olion tason valtuutuksen ja CORS-asetukset.
