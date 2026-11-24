# Monivaiheinen tunnistus ja pääsyavaimet

Monivaiheinen tunnistus (MFA) vaatii kaksi eri tekijää: jotain mitä
tiedät (salasana), jotain mitä sinulla on (puhelin, avain) tai jotain
mitä olet (biometria). Varastettu salasana ei yksin riitä. Menetelmät
eroavat kuitenkin paljon siinä, kestävätkö ne kalastelun.

| Menetelmä | Kalastelu | Muut heikkoudet |
|-----------|-----------|-----------------|
| Tekstiviestikoodi | ei kestä: käyttäjä kirjoittaa koodin väärälle sivulle | SIM-kaappaus, numeron siirto |
| TOTP-sovellus | ei kestä: koodi välitetään reaaliajassa | salaisuus palvelimella |
| Push-hyväksyntä | ei kestä; "väsytyshyökkäys" toistuvilla pyynnöillä | numeron vertailu auttaa |
| Pääsyavain (WebAuthn) | kestää: avain on sidottu sivuston nimeen | laitteen menetys, palautusprosessi |

## TOTP

Aikaan perustuva kertakäyttökoodi (RFC 6238) lasketaan yhteisestä
salaisuudesta ja kellonajasta: HMAC-SHA1 30 sekunnin
aikalaskurista, ja tuloksesta poimitaan kuusi numeroa.

```{.typescript tiedosto="esimerkit/src/07-mfa/totp.ts" osa="totp"}
```

Palvelin sallii yhden aika-askeleen eron kumpaankin suuntaan, koska
puhelimen ja palvelimen kellot eroavat. Käytetty askel muistetaan,
jotta kalastelija ei voi käyttää samaa koodia uudelleen:

```{.typescript tiedosto="esimerkit/src/07-mfa/totp.ts" osa="tarkistus"}
```

```{.typescript tiedosto="esimerkit/src/07-mfa/totp.test.ts" osa="testi"}
```

Kuusinumeroinen koodi on arvattavissa ilman nopeusrajoitusta: miljoona
vaihtoehtoa ja kolme kelpaavaa koodia kerrallaan. Luvun 6
rajoitin kuuluu myös koodin tarkistukseen. TOTP-salaisuus on
palvelimella selväkielisenä (HMAC tarvitsee sen), joten se salataan
levossa ja pidetään erillään muista tiedoista.

## Pääsyavaimet

Pääsyavain (*passkey*) on WebAuthn-standardin julkisen avaimen
tunniste. Rekisteröinnissä laite luo sivustolle avainparin ja antaa
palvelimelle julkisen avaimen. Kirjautuessa palvelin lähettää
satunnaisen haasteen, ja laite allekirjoittaa sen yksityisellä
avaimella, kun käyttäjä on varmistettu (PIN, sormenjälki,
kasvot). Yksityinen avain ei koskaan poistu laitteelta tai sen
synkronoidusta avainnipusta.

Kalastelunkestävyys tulee kahdesta asiasta. Selain antaa avaimen vain
sille sivustolle, jolle se luotiin (*relying party ID*), ja
allekirjoitettu data sisältää sivun alkuperän. Kalastelusivu
`pankki-kirjaudu.example` ei voi pyytää `pankki.fi`:n avainta, eikä
välitetty allekirjoitus kelpaisi.

Palvelin tarkistaa asiakkaan tiedot: tyyppi, haaste ja alkuperä.

```{.typescript tiedosto="esimerkit/src/07-mfa/webauthn.ts" osa="asiakastiedot"}
```

Laitteen tiedoissa (*authenticator data*) ovat sivuston nimen
tiiviste, liput ja laskuri:

```{.typescript tiedosto="esimerkit/src/07-mfa/webauthn.ts" osa="authdata"}
```

Rekisteröinti purkaa CBOR-muotoisen attestaatio-olion ja tallentaa
julkisen avaimen:

```{.typescript tiedosto="esimerkit/src/07-mfa/webauthn.ts" osa="rekisterointi"}
```

Kirjautuminen tarkistaa allekirjoituksen laitteen tietojen ja
asiakastietojen tiivisteen yli:

```{.typescript tiedosto="esimerkit/src/07-mfa/webauthn.ts" osa="kirjautuminen"}
```

Playwright voi ajaa WebAuthnia virtuaalisella todentimella Chromiumin
DevTools-protokollan kautta. Testi rekisteröi avaimen, kirjautuu ja
kokeilee lopuksi samaa sivua toisesta alkuperästä, kuten kalastelusivu
tekisi:

```{.typescript tiedosto="esimerkit/e2e/webauthn.spec.ts" osa="testi"}
```

Esimerkistä puuttuu paljon, mitä tuotantototeutus tekee:
attestaation tarkistus (luotetaanko laitevalmistajaan), useat
algoritmit (RS256, EdDSA), käyttäjän tunnisteen käsittely ja
avainten hallinta. Siksi tuotannossa käytetään kirjastoa, kuten
SimpleWebAuthnia tai kehyksen tukea.

## Palautus on heikoin lenkki

Monivaiheinen tunnistus on yhtä vahva kuin sen palautusprosessi. Jos
"kadotin puhelimeni" -lomake ohittaa MFA:n sähköpostilinkillä, hyökkääjä
käyttää sitä. Hyviä käytäntöjä:

- Useampi pääsyavain tai toinen tekijä rekisteröitynä etukäteen.
- Kertakäyttöiset palautuskoodit, tallennettu tiivisteinä.
- Hidas, valvottu palautus: viive, ilmoitus kaikkiin kanaviin,
  arkaluonteiset toiminnot estetty hetken palautuksen jälkeen.

## Käytännössä

- **Pääsyavaimet ensisijaisiksi**, TOTP varalle, tekstiviesti vain
  viimeisenä keinona. Pääsyavain korvaa usein salasanankin.
- **Kierrä istunto** MFA:n jälkeen (luku 5) ja vaadi MFA uudelleen
  arkaluonteisissa toiminnoissa.
- **Rajoita koodien arvailua** ja hylkää käytetyt koodit.
- **Valmis kirjasto** WebAuthnille: tarkistuksia on paljon, ja yksi
  puuttuva (esimerkiksi alkuperä) kumoaa kalastelunkestävyyden.
- **Hinta:** pääsyavaimet vähentävät tukipyyntöjä ja
  salasananvaihtoja, mutta vaativat huolellisen palautusprosessin ja
  käyttöliittymän, joka ohjaa käyttäjää.

## Itsearviointi

- Osaat vertailla MFA-menetelmiä kalastelunkestävyyden mukaan.
- Osaat toteuttaa TOTP-tarkistuksen kellon erolla ja uudelleenkäytön
  estolla.
- Osaat selittää, mihin pääsyavaimen kalastelunkestävyys perustuu.
- Osaat luetella, mitä palvelin tarkistaa WebAuthn-kirjautumisessa.
- Osaat suunnitella palautusprosessin, joka ei ohita MFA:ta.
