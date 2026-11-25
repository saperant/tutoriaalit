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
aikalaskurista, ja tuloksesta poimitaan kuusi numeroa. *Tietoturvan
perusteet* laski koodin käyttäjän puolelta; tässä on palvelimen
puoli, jossa olennaista on se, mitä koodin tarkistus sallii ja
muistaa.

```{.typescript tiedosto="esimerkit/src/07-mfa/totp.ts" osa="totp"}
```

Palvelin sallii yhden aika-askeleen eron kumpaankin suuntaan, koska
puhelimen ja palvelimen kellot eroavat. Käytetty askel muistetaan,
jotta kalastelija ei voi käyttää samaa koodia uudelleen:

```{.typescript tiedosto="esimerkit/src/07-mfa/totp.ts" osa="tarkistus"}
```

```{.typescript tiedosto="esimerkit/src/07-mfa/totp.test.ts" osa="testi"}
```

Näytösajossa `T` on koodin laskentahetki. Sama koodi kelpaa kerran,
vaikka se olisi vielä aikaikkunassa:

```{.tuloste tiedosto="esimerkit/naytos/07-totp.odotettu"}
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

```{.dot otsikko="Pääsyavaimen rekisteröinti ja kirjautuminen. Yksityinen avain ei poistu todentimesta. Selain lisää allekirjoitettaviin asiakastietoihin sivun alkuperän (6), joten toisella sivulla pyydetty allekirjoitus ei kelpaa palvelimelle."}
digraph {
  layout=neato; splines=false;
  node [shape=point, width=0.01, height=0.01, style=invis];
  edge [arrowsize=0.7];
  d0 [label="todennin (laite)", shape=box, style="rounded,filled", width=0, height=0.3, pos="0.00,0!"];
  dL [pos="0.00,-4.00!"];
  d0 -> dL [arrowhead=none, style=dotted];
  s0 [label="selain", shape=box, style="rounded,filled", width=0, height=0.3, pos="2.35,0!"];
  sL [pos="2.35,-4.00!"];
  s0 -> sL [arrowhead=none, style=dotted];
  p0 [label="palvelin", shape=box, style="rounded,filled", width=0, height=0.3, pos="4.70,0!"];
  pL [pos="4.70,-4.00!"];
  p0 -> pL [arrowhead=none, style=dotted];
  o1 [shape=plain, style="", fontsize=9, label=<<i>rekisteröinti</i>>, pos="1.18,-0.51!"];
  p2 [pos="4.70,-0.87!"]; s2_ [pos="2.35,-0.87!"];
  p2 -> s2_ [];
  t2 [shape=plain, style="", fontsize=9, label="1. haaste, sivuston nimi (RP ID)", pos="3.53,-0.77!"];
  s3 [pos="2.35,-1.23!"]; d3_ [pos="0.00,-1.23!"];
  s3 -> d3_ [];
  t3 [shape=plain, style="", fontsize=9, label="2. luo avainpari tälle sivustolle", pos="1.18,-1.13!"];
  d4 [pos="0.00,-1.59!"]; s4_ [pos="2.35,-1.59!"];
  d4 -> s4_ [];
  t4 [shape=plain, style="", fontsize=9, label="3. julkinen avain", pos="1.18,-1.49!"];
  s5 [pos="2.35,-1.95!"]; p5_ [pos="4.70,-1.95!"];
  s5 -> p5_ [];
  t5 [shape=plain, style="", fontsize=9, label="4. julkinen avain + asiakastiedot", pos="3.53,-1.85!"];
  o6 [shape=plain, style="", fontsize=9, label=<<i>kirjautuminen</i>>, pos="1.18,-2.31!"];
  p7 [pos="4.70,-2.67!"]; s7_ [pos="2.35,-2.67!"];
  p7 -> s7_ [];
  t7 [shape=plain, style="", fontsize=9, label="5. uusi haaste", pos="3.53,-2.57!"];
  s8 [pos="2.35,-3.03!"]; d8_ [pos="0.00,-3.03!"];
  s8 -> d8_ [];
  t8 [shape=plain, style="", fontsize=9, label="6. allekirjoita: haaste + sivun alkuperä", pos="1.18,-2.93!"];
  d9 [pos="0.00,-3.39!"]; s9_ [pos="2.35,-3.39!"];
  d9 -> s9_ [];
  t9 [shape=plain, style="", fontsize=9, label="7. allekirjoitus (käyttäjä varmistettu)", pos="1.18,-3.29!"];
  s10 [pos="2.35,-3.75!"]; p10_ [pos="4.70,-3.75!"];
  s10 -> p10_ [];
  t10 [shape=plain, style="", fontsize=9, label="8. allekirjoitus + asiakastiedot", pos="3.53,-3.65!"];
}
```

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

Kolmas rivi on kalasteluyritys: selain kieltäytyy jo ennen kuin
todentimelta kysytään mitään, koska sivun alkuperä ei vastaa avaimen
sivustoa.

```{.tuloste tiedosto="esimerkit/naytos/07-paasyavain.odotettu"}
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
