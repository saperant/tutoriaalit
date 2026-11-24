# Lainsäädäntö ja etiikka

Tietoturva ei ole vain tekninen kysymys. Lainsäädäntö asettaa
vähimmäisvaatimukset, määrää ilmoitusvelvollisuudet ja rajaa, mitä
tietoturvatutkija saa tehdä. Tämä luku on tiivis yleiskuva, ei
oikeudellinen neuvo. Säädösten tarkat sisällöt ja soveltamisalat
tarkistetaan lähteistä, ja organisaatiossa tulkinnasta vastaa
lakiasiantuntija.

## Keskeiset säädökset

| Säädös | Koskee | Tietoturvan kannalta olennaista |
|--------|--------|---------------------------------|
| **Tietosuoja-asetus** (GDPR, EU 2016/679) | henkilötietojen käsittely | asianmukaiset turvatoimet (art. 32), sisäänrakennettu tietosuoja (art. 25), tietoturvaloukkauksesta ilmoitus 72 tunnissa (art. 33) ja tarvittaessa rekisteröidyille (art. 34) |
| **NIS2-direktiivi** (EU 2022/2555) ja **kyberturvallisuuslaki** (124/2025) | keskeisten alojen keskisuuret ja suuret toimijat (energia, liikenne, terveys, digitaalinen infrastruktuuri ym.) | riskienhallintatoimet, johdon vastuu, merkittävistä poikkeamista ilmoitukset viranomaiselle |
| **Kyberkestävyyssäädös** (CRA, EU 2024/2847) | tuotteet, joissa on digitaalisia osia | tietoturva suunnittelussa, haavoittuvuuksien käsittely koko tuen ajan, aktiivisesti hyödynnetyistä haavoittuvuuksista ilmoitukset (11.9.2026 alkaen), täysi soveltaminen 11.12.2027 |
| **Rikoslaki** 38 luku | kaikki | tietomurto (8 §), viestintäsalaisuuden loukkaus, tietoliikenteen häirintä, rikoksen valmistelu |

NIS2 ja CRA siirtävät vastuuta: kyberturvallisuus on johdon
vastuulla, ja tuotteen valmistaja vastaa sen haavoittuvuuksista koko
tukijakson ajan. Ohjelmistokehittäjälle tämä tarkoittaa, että
uhkamallinnus, riippuvuuksien seuranta (SBOM), haavoittuvuuksien
vastaanotto ja tietoturvapäivitykset ovat lakisääteisiä tehtäviä
monissa organisaatioissa.

## Ilmoitusten määräajat

Poikkeaman sattuessa määräajat alkavat kulua siitä, kun organisaatio
saa tiedon tapahtumasta, ja ne kulkevat myös viikonloppuisin.
Määräaikojen laskeminen kuuluu valmistautumiseen:

```{.python tiedosto="esimerkit/12-maaraajat.py" osa="maaraajat"}
```

```{.tuloste tiedosto="esimerkit/12-maaraajat.odotettu"}
```

Suomessa NIS2:n mukaiset ilmoitukset tehdään Traficomin
Kyberturvallisuuskeskukselle tai alan valvontaviranomaiselle, ja
GDPR:n mukaiset ilmoitukset tietosuojavaltuutetun toimistolle. Sama
poikkeama voi laukaista useita ilmoituksia eri viranomaisille.
Varhainen varoitus on tarkoituksella kevyt: siinä ei tarvitse vielä
tietää kaikkea.

## Vastuullinen haavoittuvuuksien ilmoittaminen

Kun tutkija tai käyttäjä löytää haavoittuvuuden toisen järjestelmästä,
**koordinoitu haavoittuvuuksien julkistaminen** (CVD, *coordinated
vulnerability disclosure*) on vakiintunut toimintatapa:

1. Ilmoitus tehdään valmistajalle sen ilmoittamaa kanavaa pitkin.
   Monella organisaatiolla on verkkosivuillaan tiedosto
   `/.well-known/security.txt` (RFC 9116), joka kertoo yhteystiedon.
2. Valmistaja kuittaa ilmoituksen, korjaa haavoittuvuuden ja tiedottaa
   käyttäjille.
3. Haavoittuvuus julkistetaan sovitun ajan jälkeen (tyypillisesti 90
   päivää), yleensä CVE-tunnisteen kanssa.
4. Jos valmistajaa ei tavoiteta, Kyberturvallisuuskeskus toimii
   Suomessa koordinoijana.

Löytäjän on pysyttävä rajoissa: haavoittuvuuden olemassaolon
osoittaminen on eri asia kuin datan lataaminen, muokkaaminen tai
palvelun kaataminen. Monella organisaatiolla on
**haavoittuvuusohjelma** (*bug bounty*), joka kertoo, mitä saa
testata ja miten. Ohjelman ulkopuolella aktiivinen testaaminen ilman
lupaa voi täyttää tietomurron tunnusmerkistön.

Oma organisaatio tarvitsee vastaavan prosessin toiseen suuntaan:
kanavan, josta ulkopuoliset voivat ilmoittaa, ja käytännön, jolla
ilmoitukset käsitellään. CRA tekee tästä pakollista digitaalisten
tuotteiden valmistajille.

## Etiikka

Tietoturvaosaaminen on kaksiteräistä: samat taidot, joilla järjestelmiä
suojataan, mahdollistavat niihin hyökkäämisen. Ammattilaisen
eettinen perusta on yksinkertainen:

- **Lupa ensin.** Testaa vain järjestelmiä, joihin sinulla on
  kirjallinen lupa, ja pysy luvan rajoissa.
- **Vähimmän haitan periaate.** Kun löydät haavoittuvuuden, osoita se
  pienimmällä mahdollisella toimenpiteellä. Älä katso, kopioi tai
  muuta dataa enempää kuin on välttämätöntä.
- **Luottamuksellisuus.** Työssä nähdyt tiedot ja löydetyt
  haavoittuvuudet ovat luottamuksellisia, kunnes ne on korjattu ja
  julkistettu sovitusti.
- **Käyttäjien etu.** Tietoturvan tarkoitus on suojata ihmisiä. Myös
  valvonta ja lokitus ovat henkilötietojen käsittelyä, ja niiden on
  oltava oikeasuhtaisia.

## Käytännössä

- **Selvitä, mitkä säädökset koskevat sinua.** Henkilötietoja
  käsittelevä palvelu (GDPR), keskeisen alan toimija (NIS2) ja
  digitaalisten tuotteiden valmistaja (CRA) kohtaavat eri
  velvoitteet.
- **Valmistele ilmoitukset etukäteen.** Pohjat, yhteystiedot ja
  päätösvalta ovat valmiina ennen poikkeamaa, koska 24 tuntia kuluu
  nopeasti.
- **Julkaise `security.txt` ja ilmoitusprosessi.** Löytäjän on helppo
  tehdä oikein, kun kanava on selvä.
- **Dokumentoi turvatoimet.** Riskiarvio, uhkamallit ja tehdyt
  päätökset osoittavat valvojalle, että turvatoimet ovat asianmukaisia.
- **Kunnioita rajoja.** Uteliaisuus ei ole lupa. Harjoitteluun on
  tarkoitettuja ympäristöjä ja kilpailuja (CTF).

## Itsearviointi

- Osaat kertoa, mitä GDPR, NIS2, kyberturvallisuuslaki ja CRA
  edellyttävät tietoturvalta ja kenelle ne kuuluvat.
- Osaat laskea poikkeaman ilmoitusten määräajat ja kertoa, kenelle
  ilmoitukset tehdään.
- Osaat toimia vastuullisesti löytäessäsi haavoittuvuuden toisen
  järjestelmästä.
- Osaat perustella, missä kulkee raja luvallisen testauksen ja
  tietomurron välillä.
