# Johdanto {.runko-johdanto}

Go on Googlella kehitetty, staattisesti tyypitetty ja käännettävä kieli.
Robert Griesemer, Rob Pike ja Ken Thompson aloittivat sen suunnittelun
vuonna 2007. Lähtökohtana olivat suurten C++- ja Java-palvelinohjelmien
ongelmat: hitaat käännökset, monimutkaiset riippuvuudet ja kielen
piirteet, joita kukin kehittäjä käytti eri tavalla. Go julkaistiin
avoimena lähdekoodina vuonna 2009, ja versio 1.0 ilmestyi vuonna 2012.

Go:n tavoite on yksinkertaisuus suuressa mittakaavassa. Kielessä on
vähän piirteitä, ja ne on valittu niin, että sadan kehittäjän koodi
näyttää samanlaiselta ja sen voi lukea ilman yllätyksiä. Rinnakkaisuus
on rakennettu kieleen (*goroutinet* ja *kanavat*), muistinhallinta on
automaattista (roskienkeruu), ja virheet ovat tavallisia paluuarvoja.

## Mihin Go sopii ja mihin ei

Go on vakiintunut pilvi-infrastruktuurin ja verkkopalvelujen kieleksi:

- pilvi- ja konttityökalut: Kubernetes, Docker, containerd, Terraform,
  Prometheus ja etcd on kirjoitettu Go:lla
- verkkopalvelut ja rajapinnat (REST, gRPC), välityspalvelimet
  (Caddy, Traefik) ja viestinvälitys (NATS)
- komentorivityökalut, jotka jaetaan yhtenä staattisesti linkattuna
  tiedostona (GitHub CLI, Hugo)
- tietokannat ja tallennusjärjestelmät (CockroachDB, InfluxDB,
  MinIO).

Go ei ole paras valinta, kun

- tarvitaan ennustettava viive mikrosekuntitasolla tai täysi hallinta
  muistiin: roskienkeruun tauot ovat lyhyitä mutta olemassa, joten
  kovat reaaliaikajärjestelmät, pelimoottorit ja ajurit kirjoitetaan
  C:llä, C++:lla tai Rustilla
- ohjelma on pieni sulautettu laite ilman käyttöjärjestelmää (TinyGo
  kattaa osan mikrokontrollereista, mutta ei koko kieltä)
- tehtävä on data-analyysiä tai koneoppimista, joiden ekosysteemi on
  Pythonissa
- ongelma vaatii ilmaisuvoimaista tyyppijärjestelmää (algebralliset
  tietotyypit, kattava hahmontunnistus). Go valitsee tietoisesti
  yksinkertaisuuden ilmaisuvoiman sijaan.

## Versiot ja yhteensopivuus

Go julkaisee uuden version puolen vuoden välein (helmi- ja elokuussa).
*Go 1 -yhteensopivuuslupaus* takaa, että Go 1.0:lle kirjoitettu koodi
kääntyy edelleen. Tärkeimmät muutokset version 1.0 jälkeen ovat
moduulit (1.11–1.16), geneerisyys (1.18), silmukkamuuttujan
uusi merkitys ja `range` kokonaisluvun yli (1.22) sekä omat iteraattorit
(1.23).

Tämän tutoriaalin esimerkit on testattu Go 1.23:lla, joka on Ubuntu
24.04:n pakettivarastossa. Uudemmat versiot kääntävät ne sellaisinaan.
Kun uudempi versio tarjoaa tässä opetetulle tavalle paremman
vaihtoehdon, teksti mainitsee sen versionumeroineen (esimerkiksi
vertailuajojen `b.Loop` ja `go.mod`-tiedoston `tool`-rivi, molemmat
Go 1.24). Kieli on määritelty spesifikaatiossa (*The Go
Programming Language Specification*). Päätoteutus on Googlen `gc`.
Muita toteutuksia ovat GCC:n `gccgo` ja mikrokontrollereille ja
WebAssemblylle tarkoitettu TinyGo.

## Työkalut

Go:n työkalut ovat yhdessä `go`-komennossa:

| Komento | Tehtävä |
|---------|---------|
| `go build`, `go run` | käännös ja käännös + ajo |
| `go test` | testit, vertailuajot, fuzz-testaus, kattavuus |
| `go vet` | staattinen analyysi yleisille virheille |
| `gofmt`, `go fmt` | koodin muotoilu, ainoa hyväksytty tyyli |
| `go mod` | moduulit ja riippuvuudet |
| `go doc` | dokumentaatio komentoriviltä |
| `go tool pprof` | profiilien analyysi |

Editoreissa kielipalvelin on `gopls`. Tämän tutoriaalin esimerkit ovat
yksittäisiä ohjelmatiedostoja, jotka tarkistetaan ja käännetään näin:

```
gofmt -l 01-sanalaskuri.go       # ei tulostetta = muotoilu kunnossa
go vet 01-sanalaskuri.go
go run 01-sanalaskuri.go < 01-sanalaskuri.syote
```

Moduuli ja testit esitellään luvuissa 9 ja 12. Kehityskontissa
(`.devcontainer/go`) työkalut ovat valmiina; kontin avaaminen neuvotaan
taidossa *Kehitysympäristöt ja Dev Containers*. Komento `make testaa`
paketin juuressa tarkistaa, kääntää ja ajaa kaikki esimerkit ja vertaa
tulosteet tallennettuihin.

## Ensimmäinen ohjelma

Ohjelma lukee tekstiä syötteestä ja tulostaa viisi yleisintä sanaa.

```{.go tiedosto="esimerkit/01-sanalaskuri.go"}
```

Syöte ja tuloste:

```{.tuloste tiedosto="esimerkit/01-sanalaskuri.syote"}
```

```{.tuloste tiedosto="esimerkit/01-sanalaskuri.odotettu"}
```

- Jokainen tiedosto kuuluu pakettiin. Suoritettava ohjelma on paketti
  `main`, ja se alkaa funktiosta `main`.
- `import` tuo standardikirjaston paketit. Käyttämätön tuonti on
  käännösvirhe.
- `:=` esittelee muuttujan ja päättelee sen tyypin. `make` luo kartan
  (`map`) ja viipaleen (*slice*), jonka kapasiteetti tiedetään.
- `bufio.Scanner` lukee syötettä paloina, tässä sanoina. Lukuvirhe
  tarkistetaan silmukan jälkeen `Err`-metodilla: virheet ovat
  arvoja, eivät poikkeuksia.
- Puuttuvan avaimen arvo kartassa on nolla, joten `maarat[sana]++`
  toimii ilman alustusta.
- `slices.SortFunc` lajittelee vertailufunktiolla. `cmp.Or` palauttaa
  ensimmäisen nollasta poikkeavan vertailun: määrän mukaan laskevasti,
  tasatilanteessa aakkosjärjestyksessä.
- Koodi on `gofmt`-muotoiltu: sisennys sarkaimin ja kentät tasattu.
  Muotoilusta ei väitellä Go-projekteissa.

## Esitiedot ja rajaus

Esitieto on taito *Ohjelmoinnin perusteet (Python)*: lukijan oletetaan
osaavan muuttujat, ehdot, silmukat, funktiot ja listojen ja sanakirjojen
käytön jollakin kielellä. Osoittimia tai käännettäviä kieliä ei
tarvitse tuntea ennalta; ne esitellään luvuissa 3–5.

Tutoriaali opettaa kielen, sen standardikirjaston ytimen ja työkalut.
Yleiset aiheet käsitellään omissa taidoissaan, ja luvut viittaavat
niihin:

| Aihe | Taito |
|------|-------|
| tietorakenteiden ja algoritmien teoria | *Tietorakenteet*, *Algoritmit* |
| kilpailutilanteet, lukot ja muistimallit yleisesti | *Rinnakkaisohjelmointi* |
| HTTP, soketit ja protokollat | *Verkko-ohjelmointi* |
| REST-rajapinnat, tietokannat ja tunnistautuminen | *Taustapalvelut* |
| testauksen ja CI:n yleiset käytännöt | *Käännösjärjestelmät, testaus ja CI* |
| dokumentaation suunnittelu ja julkaisu | *Tekninen dokumentaatio* |

## Tutoriaalin rakenne

Luku 2 on tarkoitettu kokeneelle kehittäjälle, joka osaa jonkin toisen
kielen. Luvut 3–8 käsittelevät tyypit, ohjausrakenteet, muistimallin,
kokoelmat, omat tyypit ja rajapinnat sekä virheenkäsittelyn. Luku 9
esittelee paketit ja moduulit, luku 10 rinnakkaisuuden, luku 11
`net/http`-paketin ja luku 12 työkalut ja testauksen. Luku 13 kokoaa
idiomit, hinnat ja lähteet.
