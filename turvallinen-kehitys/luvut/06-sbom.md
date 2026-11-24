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
