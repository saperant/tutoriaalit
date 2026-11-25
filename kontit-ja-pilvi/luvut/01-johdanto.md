# Johdanto {.runko-johdanto}

Kontti paketoi ohjelman ja kaiken, mitä se tarvitsee ajoon:
tulkin, kirjastot, asetusten oletukset ja käynnistyskomennon. Paketti
on *konttikuva* (*container image*), ja sama kuva käynnistyy samalla
tavalla kehittäjän kannettavalla, CI-putkessa ja tuotannon
klusterissa. Siksi kontit ovat pilvipalveluiden käyttöönoton
perusyksikkö.

Tämä tutoriaali kulkee yhdestä kuvasta palveluksi pilveen:

1. mitä kontti on käyttöjärjestelmän näkökulmasta,
2. miten hyvä konttikuva rakennetaan ja miksi se on pieni ja turvallinen,
3. miten sovellus kirjoitetaan konttiin sopivaksi (twelve-factor),
4. miten usean kontin sovellus ajetaan Composella,
5. miten sama sovellus kuvataan Kubernetesille ja paketoidaan Helmillä,
6. miten infrastruktuuri ja käyttöönotot hoidetaan koodina ja putkessa.

## Esimerkkisovellus

Koko tutoriaali käyttää samaa pientä sovellusta, *käyntilaskuria*. Siinä
on kaksi palvelua:

- **api** vastaa HTTP-pyyntöihin, kasvattaa laskuria ja kertoo
  käyntimäärän,
- **laskuri** säilyttää arvon levyllä, joten sillä on *tila*.

Molemmat ovat Pythonin vakiokirjastolla kirjoitettuja ohjelmia, jotta
huomio pysyy konteissa eikä kehyksissä. Lisäksi luvussa 4 on pieni
Go-palvelu, jolla näytetään staattisen binäärin kuva. Taustapalvelujen
ohjelmointi on taidossa *Taustapalvelut*; tässä katsotaan, mitä
palvelulta vaaditaan, jotta sitä voi ajaa konteissa luotettavasti.

## Esitiedot ja rajaus

Tutoriaali olettaa taidon *Tietoverkot*: IP-osoitteet, portit, DNS,
HTTP ja TLS. Sen esitietona on *Komentorivi ja Linux*, joten kuoren
peruskäyttö oletetaan tutuksi. Kontin toteutus ytimessä (nimiavaruudet, cgroups,
seccomp) käydään läpi vain sen verran kuin konttien käyttäjä tarvitsee;
syvällisemmin se on taidossa *Virtualisointi*. Usean palvelun
arkkitehtuuri on taidossa *Palveluarkkitehtuurit* ja palvelinten
ylläpito taidossa *Palvelinympäristöt*. Luku 11 näyttää palvelun
putken konttien näkökulmasta; jatkuvan integraation ja toimituksen
käytännöt (trunk-pohjainen kehitys, ominaisuusliput, julkaisustrategiat
mitattuina) ovat taidossa *Jatkuva integraatio ja toimitus*.

## Mitä on testattu

Kaikki tutoriaalin tiedostot ovat oikeita ja testattuja, mutta eri
tavoin:

| Osa | Testaus |
|-----|---------|
| Palvelujen Python- ja Go-koodi | ruff, mypy, yksikkötestit, gofmt, go vet |
| Dockerfilet | hadolint; kuvat rakennetaan ja ajetaan Dockerilla |
| Compose-sovellus | skeemavalidointi; sovellus käynnistetään ja sitä kutsutaan |
| Kubernetes-manifestit | skeemavalidointi (Kubernetes 1.35), omat käytännöt |
| Helm-kaavio | lint, renderöinti ja renderöidyn tuloksen validointi |
| CI-putki | GitHub Actionsin skeemavalidointi |
| Infrastruktuuri koodina | Python-malli, jonka tuloste tarkistetaan |

Kuvat rakennetaan ja ajetaan siellä, missä Docker on käytettävissä:
kehittäjän koneella ja CI:ssä. Kubernetes-manifesteja ei ajeta oikeassa
klusterissa, vaan ne tarkistetaan Kubernetesin omia skeemoja vasten;
klusterin käyttöä varten luvussa 7 neuvotaan, miten paikallinen klusteri
(kind tai k3d) käynnistetään. Versio 1.35 on testin kiinnitys, ei
suositus: skeemat tarkistetaan sitä versiota vasten, jota oma klusteri
ajaa. Esimerkkien `make` ajaa kaikki
tarkistukset ja ohittaa ilmoituksella ne, joihin ympäristössä ei ole
välineitä.

## Työkalut

| Työkalu | Käyttö | Asennus |
|---------|--------|---------|
| Docker Engine ja Compose v2 | kuvien rakennus ja ajo | Docker Desktop tai Linuxin paketit |
| hadolint | Dockerfilen tarkistus | `pip install hadolint-bin` |
| kubernetes-validate | manifestien skeemat ilman klusteria | `pip install kubernetes-validate` |
| check-jsonschema | Compose- ja putkitiedostojen skeemat | `pip install check-jsonschema` |
| yamllint | YAML-tyyli | `pip install yamllint` |
| Helm 3 | kaaviot | `alpine/helm`-kuva tai helm.sh |
| kubectl, kind | oikea klusteri (valinnainen) | kubernetes.io, kind.sigs.k8s.io |

Kehityskontissa (`.devcontainer/kontit-ja-pilvi`) on Python-työkalut
valmiina. Kontin sisällä ei ole Dockeria, joten siellä ajetaan vain
staattiset tarkistukset.

```text
cd kontit-ja-pilvi/esimerkit
make              # kaikki tarkistukset ja ajot
make staattiset   # ilman Dockeria
make docker       # kuvat, Compose ja Helm
```

## Ensimmäinen kontti

Ennen omia kuvia kannattaa nähdä, mitä kontti tekee. Seuraava komento
käynnistää valmiin Python-kuvan, ajaa siinä yhden komennon ja poistaa
kontin:

```text
docker run --rm python:3.12-slim python -c "import sys; print(sys.version)"
```

Komento tulostaa kuvan Python-version. Koneelle ei asentunut Pythonia,
eikä komento muuttanut koneen
tiedostoja. Docker haki kuvan rekisteristä (Docker Hub), loi sen päälle
kirjoitettavan kerroksen, käynnisti prosessin eristettynä ja poisti
kaiken prosessin päätyttyä. Seuraavassa luvussa katsotaan, mitä
"eristettynä" tarkoittaa.
