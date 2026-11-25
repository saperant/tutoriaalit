# SBOM ja haavoittuvuustiedot

Kun laajalti käytetystä kirjastosta julkaistaan vakava haavoittuvuus,
kuten Log4Shell joulukuussa 2021, jokainen organisaatio kysyy saman
kysymyksen: missä tätä käytetään? Ilman ajantasaista luetteloa
vastaaminen vie päiviä. **SBOM** (*software bill of materials*,
ohjelmiston osaluettelo) on tuo luettelo koneluettavassa muodossa.

## SBOM-muodot

Kaksi standardimuotoa ovat vakiintuneet:

| Muoto | Ylläpitäjä | Painopiste |
|-------|-----------|------------|
| CycloneDX | OWASP, ECMA-424 | tietoturva: komponentit, riippuvuudet, haavoittuvuudet, palvelut |
| SPDX | Linux Foundation, ISO/IEC 5962 | lisenssit ja tekijänoikeudet, myös tietoturva |

Kummassakin komponentti tunnistetaan **pURL**-tunnisteella (*package
URL*), esimerkiksi `pkg:pypi/requests@2.31.0` tai
`pkg:maven/org.apache.logging.log4j/log4j-core@2.14.1`. pURL on
ekosysteemistä riippumaton tapa nimetä paketti, ja haavoittuvuustietokannat
käyttävät samaa tunnistetta.

EU:n kyberkestävyyssäädös (CRA) velvoittaa digitaalisia tuotteita
markkinoille tuovat valmistajat laatimaan SBOM:n vähintään tuotteen
ylimmän tason riippuvuuksista; velvoitteita sovelletaan joulukuusta
2027 alkaen. Yhdysvaltain liittovaltion hankinnat
vaativat SBOM:ia jo aiemmin.

## SBOM:n tuottaminen

SBOM tuotetaan buildissa koneellisesti lukitustiedostosta tai valmiista
artefaktista, ei käsin. Pieni CycloneDX-generaattori näyttää rakenteen:

```{.python tiedosto="esimerkit/06-sbom.py" osa="sbom"}
```

Sarjanumero on johdettu sisällöstä, joten sama syöte tuottaa saman
SBOM:n. Tämä on pieni yksityiskohta mutta tärkeä: kun SBOM on
toistettava, sen muutos kertoo, että ohjelmiston osat muuttuivat.
Kahden version vertailu näyttää muutokset suoraan:

```{.python tiedosto="esimerkit/06-sbom.py" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/06-sbom.odotettu"}
```

Vertailu sopii julkaisun tarkistukseksi: uusi komponentti (`+`) on uusi
riippuvuus, jonka joku hyväksyi, ja jokainen versiomuutos (`~`) on
selitettävissä päivityspyynnöllä.

Valmiita työkaluja ovat esimerkiksi **Syft** (kontit, tiedostojärjestelmät
ja paketit), **cdxgen** ja ekosysteemien omat (`cyclonedx-py`,
`cyclonedx-npm`, CycloneDX:n Maven- ja Gradle-liitännäiset). Konttikuvan
SBOM on erityisen hyödyllinen, koska se kattaa myös käyttöjärjestelmän
paketit, joita lukitustiedosto ei tunne.

## Haavoittuvuustiedot

Haavoittuvuustietokannat kertovat, mitkä versiot ovat haavoittuvia:

- **CVE** antaa haavoittuvuudelle tunnisteen, ja **NVD** lisää
  vakavuusarvion (CVSS).
- **OSV** (*Open Source Vulnerabilities*) kokoaa ekosysteemien
  tiedotteet (GitHub Advisory Database, PyPA, RustSec, Go) yhteiseen
  muotoon, joka ilmaisee haavoittuvat versiovälit paketin
  omassa versiomuodossa.
- **GitHub Advisory Database** on Dependabotin ja `npm audit`in lähde.

OSV-tiedote kertoo paketin ja välin "haavoittuvuus alkaa versiosta X,
korjattu versiossa Y". Vertailu SBOM:iin on periaatteessa yksinkertainen:

```{.python tiedosto="esimerkit/06-haavoittuvuudet.py" osa="tieto"}
```

```{.python tiedosto="esimerkit/06-haavoittuvuudet.py" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/06-haavoittuvuudet.odotettu"}
```

Esimerkin tiedotteet ovat keksittyjä (`ESIM-`), mutta rakenne on sama
kuin oikeissa. Viimeinen rivi näyttää klassisen virheen: versionumerot
on verrattava osina, ei merkkijonoina. Kukin ekosysteemi määrittelee
omat vertailusääntönsä (PEP 440, SemVer, Debianin versiot), joten
oikeassa työkalussa vertailu on ekosysteemikohtainen.

Valmiita työkaluja ovat **osv-scanner**, **pip-audit**, **npm audit**,
**Grype** (konttikuvat ja SBOM:t), **Trivy** ja koodialustojen omat
(Dependabot-hälytykset).

## Haavoittuvuusskannauksen rajat

Skannerin raportti ei ole tietoturva-arvio. Sen rajat on tunnettava,
jotta raporttia osaa käyttää:

- **Saavutettavuus.** Raportti kertoo, että haavoittuva versio on
  asennettu, ei sitä, kutsuuko koodi haavoittuvaa funktiota. Suurin osa
  löydöksistä ei ole hyödynnettävissä juuri tässä sovelluksessa.
  Jotkin työkalut (govulncheck, Snykin ja GitHubin saavutettavuusanalyysi)
  tarkistavat kutsupolut.
- **VEX** (*Vulnerability Exploitability eXchange*) on tapa kertoa
  SBOM:n rinnalla, että haavoittuvuus ei koske tuotetta, ja miksi
  ("haavoittuvaa koodia ei ladata"). Se on dokumentoitu perustelu, ei
  piilotus.
- **Puuttuva tieto.** Tietokanta tuntee vain julkaistut haavoittuvuudet.
  Puhdas raportti ei tarkoita turvallista koodia. Lisäksi omat ja
  kopioidut koodit sekä sisäänrakennetut kirjastot (*vendored*) jäävät
  usein SBOM:n ulkopuolelle.
- **Ei korjausta.** Kun korjattua versiota ei ole, vaihtoehdot ovat
  riskin rajaaminen (ominaisuus pois, syöte suodatettuna), toiseen
  kirjastoon siirtyminen tai korjauksen tekeminen itse.

## Kun haavoittuvuus on omassa tuotteessa

Edellä oltiin tiedotteiden vastaanottajia. Kun haavoittuvuus löytyy
omasta koodista, tiimi on se, jonka tiedotetta muut odottavat. EU:n
kyberkestävyyssäädös (CRA) tekee käsittelystä valmistajan velvollisuuden
koko tukiajan ajaksi, ja SSDF kuvaa sen käytäntöinä RV.1–RV.3. Vaiheet
ovat:

1. **Vastaanotto.** `SECURITY.md` ja `security.txt` kertovat
   yksityisen ilmoituskanavan (esimerkiksi koodialustan yksityinen
   haavoittuvuusilmoitus), ei julkista tikettiä. Ilmoitus kuitataan
   muutamassa päivässä, ja ilmoittajalle kerrotaan aikataulu.
2. **Toisto ja luokittelu.** Virhe toistetaan, sille määritetään
   vakavuus (CVSS) ja heikkousluokka (CWE) ja selvitetään, mistä
   versiosta alkaen se on koodissa.
3. **Korjaus yksityisesti.** Korjaus ja sen regressiotesti tehdään
   yksityisessä haarassa, jotta muutoshistoria ei paljasta virhettä
   ennen julkaisua. Korjaus **takaisinsovitetaan** (*backport*)
   jokaiseen tuettuun julkaisulinjaan.
4. **Tunniste.** CVE-tunniste pyydetään CVE-numerointiviranomaiselta
   (CNA), esimerkiksi koodialustan tietoturvatiedotteen kautta.
5. **Julkaisu ja tiedote.** Korjatut versiot julkaistaan yhtä aikaa.
   Tiedote kertoo haavoittuvat ja korjatut versiot, vakavuuden,
   mahdollisen kiertotavan ja kiittää löytäjää. Koneluettavana se
   julkaistaan OSV- tai CSAF-muodossa, ja linjoille, joita virhe ei
   koske, annetaan VEX-lausuma.
6. **Jälkikatsaus.** Miksi katselmointi ja tarkistukset eivät
   löytäneet virhettä, ja mikä testi tai linterisääntö löytää saman
   virheluokan ensi kerralla?

Vaiheet 2 ja 3 tuottavat suunnitelman, jonka voi laskea: mitkä linjat
korjataan, mihin mennessä ja mitä muista sanotaan.

```{.python tiedosto="esimerkit/06-kasittely.py" osa="tiedot"}
```

```{.python tiedosto="esimerkit/06-kasittely.py" osa="suunnitelma"}
```

```{.tuloste tiedosto="esimerkit/06-kasittely.odotettu"}
```

Linja 1.8 saa VEX-lausuman, koska asiakkaiden skannerit hälyttävät
siitä muuten turhaan. Linjan 2.4 tuki on päättynyt, joten sille ei
tehdä korjausta, mutta tiedote sanoo sen suoraan. Julkaistut
korjausajat ovat lupaus, jota mitataan. Jos haavoittuvuutta
hyödynnetään jo aktiivisesti, CRA edellyttää lisäksi ilmoitusta
viranomaiselle 24 tunnin kuluessa (taito *Tietoturvan perusteet*).
Löytäjän puoli samasta prosessista on taidossa *Haavoittuvuuksien
analyysi ja torjunta*.

## Käytännössä

- **SBOM buildin tuotteena.** Jokaisesta julkaisusta tuotetaan SBOM
  koneellisesti ja säilytetään julkaisun rinnalla.
- **Toistettava SBOM.** Sama syöte, sama tuloste; muutokset kertovat
  osien muuttuneen.
- **Jatkuva vertailu.** Haavoittuvuustiedot päivittyvät päivittäin, joten
  julkaistujen versioiden SBOM:t tarkistetaan uudelleen säännöllisesti,
  ei vain buildissa.
- **Priorisoi saavutettavuuden ja vakavuuden mukaan.** Hyödynnettävissä
  oleva haavoittuvuus internetiin näkyvässä palvelussa ensin.
- **Kirjaa päätökset.** "Ei koske meitä" on VEX-lausuma perusteluineen,
  ei hiljainen ohitus.

## Itsearviointi

- Osaat selittää, mikä SBOM on, ja nimetä CycloneDX:n, SPDX:n ja pURLin.
- Osaat tuottaa SBOM:n koneellisesti ja vertailla kahden julkaisun osia.
- Osaat verrata riippuvuuksia OSV-muotoiseen haavoittuvuustietoon ja
  välttää versiovertailun sudenkuopan.
- Osaat kertoa haavoittuvuusskannauksen rajat ja mitä VEX tarkoittaa.
- Osaat kuvata, miten omasta tuotteesta ilmoitettu haavoittuvuus
  käsitellään vastaanotosta tiedotteeseen, ja päättää, mitkä
  julkaisulinjat korjataan.
