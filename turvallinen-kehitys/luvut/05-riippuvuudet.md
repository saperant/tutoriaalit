# Riippuvuudet ja toimitusketju

Tyypillisessä sovelluksessa omaa koodia on alle kymmenesosa;
loput on avoimen lähdekoodin riippuvuuksia ja niiden riippuvuuksia.
Jokainen niistä ajetaan samoilla oikeuksilla kuin oma koodi, ja moni
ajaa koodia jo asennuksen aikana. **Toimitusketjun hyökkäys**
(*supply chain attack*) kohdistuu tähän ketjuun: hyökkääjä ei murtaudu
kohteeseen, vaan kohde asentaa hyökkääjän koodin itse.

## Hyökkäystavat

| Hyökkäys | Miten se toimii | Tunnettu tapaus |
|----------|-----------------|-----------------|
| ylläpitäjän tilin kaappaus | oikeaan pakettiin julkaistaan haitallinen versio | event-stream (npm, 2018) |
| pitkäjänteinen soluttautuminen | luotetuksi ylläpitäjäksi vuosien aikana | xz-utils (2024) |
| kirjoitusvirhepaketti (*typosquatting*) | nimi muistuttaa suosittua pakettia | lukuisia PyPI:ssä ja npm:ssä |
| riippuvuussekaannus (*dependency confusion*) | julkiseen rekisteriin sisäisen paketin nimellä korkeampi versio | Birsanin tutkimus (2021) |
| kaapattu CI-toiminto | suosittuun toimintoon lisätään salaisuuksia vuotava koodi | tj-actions/changed-files (2025) |
| kaapattu build | julkaisu rakennetaan saastuneessa ympäristössä | SolarWinds (2020) |

Puolustus on kerroksellinen: lukitse ja tarkista, mitä asennat;
tiedä, mitä sinulla on (SBOM, seuraava luku); varmista, kuka teki ja
mistä se rakennettiin (allekirjoitukset, luku 7).

## Lukitus ja tiivisteet

**Lukitustiedosto** kiinnittää koko riippuvuuspuun tarkat versiot:
`package-lock.json`, `poetry.lock`, `uv.lock`, `Cargo.lock`,
`go.sum`, `gradle.lockfile`. Ilman sitä jokainen asennus voi saada eri
version, myös juuri kaapatun. Pelkkä versio ei kuitenkaan riitä:
sisäinen rekisteri tai konttirekisterin tagi voi saada saman version
uudelleen, ja peili tai välimuisti voi tarjota muokatun paketin. Siksi
lukitustiedostossa on myös **paketin tiiviste**, ja asennus tarkistaa
sen:

```{.python tiedosto="esimerkit/05-lukitus.py" osa="tarkistus"}
```

```{.python tiedosto="esimerkit/05-lukitus.py" osa="peukalointi"}
```

```{.tuloste tiedosto="esimerkit/05-lukitus.odotettu"}
```

Oikeat työkalut tekevät saman: `npm ci` ja `pip install
--require-hashes` hylkäävät paketin, jonka tiiviste ei täsmää, ja
Go:n `go.sum` sekä tarkistussummatietokanta (`sum.golang.org`)
varmistavat, että kaikki saavat saman sisällön. CI:ssä käytetään aina
lukitustiedoston mukaista asennusta (`npm ci`, ei `npm install`), jotta
CI ei hiljaa päivitä riippuvuuksia.

Lukitus ei tee päivityksistä tarpeettomia, vaan hallittuja. Päivitys
tehdään pull requestina (Dependabot, Renovate), jolloin testit ajetaan
ja muutos katselmoidaan. Uuden version voi myös jättää odottamaan
muutamaksi päiväksi (*cooldown*): useimmat kaapatut versiot
havaitaan ja poistetaan rekisteristä tunneissa.

## Kirjoitusvirhepaketit

Hyökkääjä julkaisee paketin, jonka nimi on kirjoitusvirheen päässä
suositusta paketista, ja odottaa. Uuden riippuvuuden nimen voi
tarkistaa samaan tapaan kuin oikolukija:

```{.python tiedosto="esimerkit/05-typosquat.py" osa="etaisyys"}
```

```{.python tiedosto="esimerkit/05-typosquat.py" osa="arvio"}
```

```{.tuloste tiedosto="esimerkit/05-typosquat.odotettu"}
```

Nimien normalisointi on tärkeää: PyPI:ssä `PyYAML`, `pyyaml` ja
`py_yaml` ovat sama nimi (PEP 503), joten vertailu tehdään
normalisoiduilla nimillä. Etäisyysvertailu tuottaa myös vääriä
hälytyksiä (`urllib` on oikea standardikirjaston moduli, mutta PyPI:ssä
samanniminen paketti olisi epäilyttävä). Siksi tarkistus on katselmoijan
apu: se kertoo, että nimi kannattaa tarkistaa käsin.

Uuden riippuvuuden arviossa katsotaan nimen lisäksi ylläpitäjät,
paketin ikä ja aktiivisuus, lataukset, lisenssi ja se, ajaako paketti
koodia asennuksessa. OpenSSF Scorecard kokoaa monia näistä yhdeksi
arvioksi. Paras riippuvuus on usein se, jota ei tarvita: kymmenen rivin
apufunktio kannattaa kirjoittaa itse.

## Riippuvuussekaannus

Yritys julkaisee sisäiset kirjastonsa omaan pakettirekisteriinsä ja
käyttää samalla julkista rekisteriä. Jos asennustyökalu hakee
molemmista ja valitsee korkeimman version, hyökkääjä voi julkaista
julkiseen rekisteriin sisäisen paketin nimellä version 99.0.0:

```{.bash tiedosto="esimerkit/05-sekaannus.sh" osa="lahteet"}
```

```{.bash tiedosto="esimerkit/05-sekaannus.sh" osa="haku"}
```

```{.tuloste tiedosto="esimerkit/05-sekaannus.odotettu"}
```

Ilman kiinnitystä pip valitsee hyökkääjän version, koska se ei
priorisoi lähteitä. Kiinnitetty versio ja tiiviste valitsevat oikean
paketin. Jos sisäinen lähde ei vastaa ja julkisessa on sama versio,
asennus epäonnistuu tiivisteen takia: virhe on parempi kuin hyökkääjän
koodi.

Varsinaiset torjuntakeinot ovat rakenteellisia:

- **Yksi lähde.** Kaikki paketit haetaan yhden sisäisen välityspalvelun
  kautta (Artifactory, Nexus, devpi), joka hakee julkisista
  rekistereistä vain sallitut nimet.
- **Nimiavaruudet.** npm:n scope (`@yritys/laskutus`) ja Mavenin
  ryhmätunnus sitovat nimen omistajaan. Varaa organisaation nimi
  julkisista rekistereistä, vaikka et julkaisisi niihin.
- **Lähteen kiinnitys paketille.** Esimerkiksi uv:n `tool.uv.sources`
  ja Gradlen `exclusiveContent` sanovat, että tietty paketti haetaan
  vain tietystä lähteestä.

## Asennusaikainen koodi

Monet pakettityökalut ajavat paketin koodia jo asennuksessa: npm:n
`postinstall`-skriptit, Pythonin `setup.py` lähdekoodijakeluissa,
Gradlen ja Mavenin liitännäiset. Kaapattu paketti pääsee siis
koneelle jo `install`-komennolla. Torjunta: asennukset kontissa tai
CI:ssä eikä kehittäjän päätilillä, npm:ssä `--ignore-scripts` tai
sallittujen skriptien lista, Pythonissa valmiit wheel-paketit
(`--only-binary :all:`).

## Käytännössä

- **Lukitustiedosto aina repositorioon** ja CI:ssä asennus sen mukaan
  (`npm ci`, `pip install --require-hashes`, `uv sync --locked`).
- **Päivitykset pull requesteina** automaattisesti, testattuina ja
  pienellä viiveellä.
- **Uusi riippuvuus on päätös.** Nimi, ylläpitäjät, aktiivisuus ja
  tarve arvioidaan; tarkistus voi olla valmiin määritelmän sääntö
  (luku 2).
- **Yksi pakettilähde ja nimiavaruudet** estävät riippuvuussekaannuksen
  rakenteellisesti.
- **Asennukset eristettyinä.** Asennusaikainen koodi ajetaan kontissa,
  ei kehittäjän tilillä, jolla on pääsy SSH-avaimiin.

## Itsearviointi

- Osaat kuvata toimitusketjun hyökkäystavat ja tunnettuja tapauksia.
- Osaat selittää, miksi lukitustiedostossa on tiivisteet, ja käyttää
  lukittua asennusta CI:ssä.
- Osaat tunnistaa kirjoitusvirhepaketin ja arvioida uuden riippuvuuden.
- Osaat selittää riippuvuussekaannuksen ja sen rakenteelliset torjunnat.
- Osaat rajata asennusaikaisen koodin riskin.
