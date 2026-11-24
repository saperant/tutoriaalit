# Pienet ja turvalliset kuvat

Jokainen kuvaan jäävä tiedosto maksaa: se pidentää latausaikaa, vie
levyä jokaisella koneella ja voi sisältää haavoittuvuuden. Kuori,
paketinhallinta ja `curl` ovat myös hyökkääjän työkaluja: jos niitä ei
ole kuvassa, murtautuja ei saa niitä käyttöönsä.

## Peruskuvan valinta

| Peruskuva | Koko | Sisältää | Sopii |
|-----------|------|----------|-------|
| `debian`, `ubuntu` | ~ 80–120 Mt | täysi käyttäjätila | kehitys, vianetsintä |
| `python:3.12-slim` | ~ 120 Mt | Debian + Python | tulkatut kielet |
| `alpine` | ~ 8 Mt | musl, BusyBox, apk | pienet kuvat, varoen |
| distroless | 2–80 Mt | vain ajonaikaiset kirjastot | tuotanto |
| `scratch` | 0 | ei mitään | staattiset binäärit |

*Distroless*-kuvissa (Googlen ylläpitämät `gcr.io/distroless/*`) ei ole
kuorta eikä paketinhallintaa, vain ajoon tarvittavat kirjastot,
CA-varmenteet ja aikavyöhyketiedot. `:nonroot`-muunnelmissa on valmiina
käyttäjä 65532.

## Staattinen binääri distroless-kuvaan

Go kääntää ohjelman yhdeksi staattiseksi binääriksi, joten
ajokuvaan ei tarvita edes C-kirjastoa. Palvelu on pieni:

```{.go tiedosto="esimerkit/staattinen/main.go"}
```

Huomaa valitsin `-terveys`: koska kuvassa ei ole `curl`ia, binääri
osaa tarkistaa itse oman terveytensä. Dockerfile kääntää ohjelman
ensimmäisessä vaiheessa ja kopioi binäärin distroless-kuvaan:

```{.dockerfile tiedosto="esimerkit/staattinen/Dockerfile"}
```

- `CGO_ENABLED=0` tuottaa staattisen binäärin, joka ei tarvitse
  glibc:tä.
- `-trimpath` poistaa rakennuskoneen polut binääristä, ja
  `-ldflags="-s -w"` jättää pois debug-tiedot. Kuva pienenee, ja sama
  lähde tuottaa saman binäärin.
- Lopullisessa kuvassa on yksi tiedosto, jonka omistaa
  käyttäjä 65532.

Testi vertaa kuvien kokoja (tiedosto `testit/docker.odotettu`, luku 6):
Go-palvelun kuva on alle 20 Mt, ja Python-kuva on yli viisi kertaa
suurempi. Ero ei johdu kielestä vaan siitä, mitä ajoon tarvitaan:
tulkattu kieli tarvitsee tulkin ja sen kirjastot.

## Tarkistus ennen rakennusta: hadolint

*hadolint* jäsentää Dockerfilen ja tarkistaa siinä ajettavat
kuorikomennot ShellCheckillä. Tässä Dockerfilessä on tavallisimmat
virheet:

```{.dockerfile tiedosto="esimerkit/huono/Dockerfile"}
```

hadolint löytää ne (rivi, sääntö, vakavuus):

```{.tuloste tiedosto="esimerkit/huono/hadolint.odotettu"}
```

| Sääntö | Ongelma | Korjaus |
|--------|---------|---------|
| DL3007 | `latest` vaihtuu huomaamatta | kiinteä tagi ja digest |
| DL3009 | pakettiluettelot jäävät kuvaan | `rm -rf /var/lib/apt/lists/*` samassa käskyssä |
| DL3059 | peräkkäiset `RUN`-käskyt | yhdistä, jotta välimuisti ei vanhene |
| DL3008, DL3013 | versiot kiinnittämättä | kiinteät versiot tai lukitustiedosto |
| DL3015 | suositellut paketit mukaan | `--no-install-recommends` |
| DL3020 | `ADD` purkaa ja lataa salaa | `COPY` |
| DL3042 | pipin välimuisti kuvaan | `--no-cache-dir` |
| DL3025 | kuorimuoto, SIGTERM ei perillä | exec-muoto |

Erillinen `RUN apt-get update` on vaarallinen myös välimuistin takia:
jos rivi on välimuistissa, myöhempi asennus käyttää vanhentuneita
pakettiluetteloita. Päivitys ja asennus kuuluvat samaan käskyyn.

Molemmat esimerkkien oikeat Dockerfilet läpäisevät hadolintin ilman
huomautuksia, ja CI-putki (luku 11) ajaa saman tarkistuksen.

## Haavoittuvuudet, SBOM ja allekirjoitukset

Kuvan tarkistus ei pääty rakennukseen:

- **Haavoittuvuusskannaus.** Trivy, Grype ja rekisterien omat skannerit
  vertaavat kuvan paketteja haavoittuvuustietokantoihin. Skannaus
  ajetaan putkessa ja säännöllisesti jo julkaistuille kuville, koska
  uusia haavoittuvuuksia löytyy vanhoistakin kuvista.
- **SBOM** (*software bill of materials*) luettelee kuvan komponentit
  versioineen (SPDX- tai CycloneDX-muodossa). Kun uusi haavoittuvuus
  julkaistaan, SBOMista näkee heti, mitkä kuvat ovat alttiina.
- **Allekirjoitus ja alkuperä.** Sigstoren cosign allekirjoittaa kuvan
  digestin, ja *provenance*-tieto (SLSA) kertoo, mikä putki rakensi
  kuvan mistäkin lähteestä. Klusteri voi hyväksyä vain allekirjoitetut
  kuvat.

Luvun 11 putki tuottaa SBOMin ja alkuperätiedon rakennuksen
yhteydessä. Tietoturvan prosessit kehitystyössä ovat taidossa
*Tietoturva kehitystyössä*.

## Käytännössä

- **Pienin kuva, jossa sovellus toimii.** Staattisille binääreille
  distroless tai `scratch`, tulkatuille kielille `slim` tai distroless.
  Älä tavoittele kokoa vaihtamalla glibc musliin, jos sovellus ei ole
  sitä varten testattu.
- **Vianetsintä ilman kuorta.** Distroless-kontin tutkimiseen ei
  tarvita kuorta kuvaan: `kubectl debug` ja `docker debug` liittävät
  työkalukontin samoihin nimiavaruuksiin.
- **hadolint putkeen.** Se on nopea ja löytää virheet, jotka muuten
  huomataan vasta tuotannossa.
- **Skannaus ja SBOM osaksi julkaisua.** Haavoittuvuustieto vanhenee,
  kuva ei. Tieto siitä, mitä kuvassa on, on edellytys sille, että
  haavoittuvuuteen voi reagoida.

## Itsearviointi

- Osaat valita peruskuvan sovelluksen kielen ja ajotarpeen mukaan ja
  perustella valinnan.
- Osaat kirjoittaa monivaiheisen rakennuksen, jonka lopullisessa
  kuvassa on vain ajoon tarvittavat tiedostot.
- Osaat lukea hadolintin huomautukset ja korjata tavallisimmat
  Dockerfilen virheet.
- Osaat kertoa, mitä haavoittuvuusskannaus, SBOM ja kuvan allekirjoitus
  tuovat toimitusketjun turvallisuuteen.
