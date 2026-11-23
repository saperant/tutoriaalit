# Paketit ja moduulit {.runko-modulit}

Go-koodi jakautuu *paketteihin* ja paketit *moduuleihin*. Paketti on
hakemisto, jonka kaikki `.go`-tiedostot kuuluvat samaan pakettiin ja
näkevät toistensa nimet. Moduuli on joukko paketteja, jotka
versioidaan ja julkaistaan yhdessä; sen juuressa on `go.mod`-tiedosto.

## Näkyvyys

Näkyvyyttä on kaksi tasoa, ja ne päätetään nimen alkukirjaimesta:

- `Varasto`, `Lisaa`, `ErrMaara` alkavat isolla kirjaimella ja näkyvät
  paketin ulkopuolelle (*exported*).
- `saldot`, `tarkista` alkavat pienellä ja näkyvät vain paketin sisällä.

Luokka- tai tiedostokohtaista näkyvyyttä ei ole: paketti on
kapseloinnin yksikkö. Hakemiston `internal` alla olevat paketit voi
tuoda vain hakemiston `internal` vanhemman alta, joten niillä
jaetaan koodia moduulin sisällä julkaisematta sitä.

## Esimerkki: moduuli

Esimerkkimoduuli `09-kauppa` on pieni varastopalvelu. Sen rakenne
noudattaa yleistä Go-projektien käytäntöä:

```
09-kauppa/
  go.mod                     moduulin nimi ja Go-versio
  varasto/                   julkinen kirjasto: example.com/kauppa/varasto
    varasto.go
    varasto_test.go
  internal/tunnus/           moduulin sisäinen paketti
    tunnus.go
    tunnus_test.go
  cmd/kauppa/                suoritettava ohjelma
    main.go
    main_test.go
  testdata/                  testien aineisto; go-työkalu ohittaa sen
```

```{.text tiedosto="esimerkit/09-kauppa/go.mod"}
```

Moduulin nimi on sen tuontipolun alku. Julkaistun moduulin nimi on sen
lähdekoodin osoite, kuten `github.com/yritys/kauppa`, jolloin `go`-työkalu
osaa hakea sen. Rivi `go 1.23` kertoo kielen version, jonka mukaan
moduulin koodi käännetään.

Paketin nimi on sen hakemiston viimeinen osa, ja tuonti viittaa
pakettiin koko polulla:

```{.go tiedosto="esimerkit/09-kauppa/varasto/varasto.go" osa="tuonnit"}
```

```{.go tiedosto="esimerkit/09-kauppa/varasto/varasto.go" osa="tyyppi"}
```

```{.go tiedosto="esimerkit/09-kauppa/varasto/varasto.go" osa="ota"}
```

Sisäinen paketti validoi tuotetunnukset. Sen dokumentaatiokommentti
alkaa sanoilla `Package tunnus`, ja jokaisella julkisella nimellä on
kommentti, joka alkaa nimellä:

```{.go tiedosto="esimerkit/09-kauppa/internal/tunnus/tunnus.go"}
```

Ohjelma on paketti `main` hakemistossa `cmd/kauppa`. Sen `main` on ohut:
varsinainen työ on funktiossa, joka ottaa syötteen ja tulosteen
rajapintoina ja jota voi siksi testata (luku 12):

```{.go tiedosto="esimerkit/09-kauppa/cmd/kauppa/main.go" osa="main"}
```

```
$ cd 09-kauppa
$ go build ./...                 # kaikki paketit
$ go run ./cmd/kauppa < testdata/komennot.txt
```

```{.tuloste tiedosto="esimerkit/09-kauppa/testdata/komennot.txt"}
```

```{.tuloste tiedosto="esimerkit/09-kauppa/testdata/odotettu.txt"}
```

## Riippuvuudet

Ulkoinen riippuvuus lisätään komennolla `go get`, joka päivittää
`go.mod`-tiedoston ja tarkistussummat tiedostoon `go.sum`:

```
$ go get github.com/jackc/pgx/v5@v5.7.1
$ go mod tidy        # lisää puuttuvat, poistaa käyttämättömät
$ go list -m all     # kaikki riippuvuudet versioineen
$ go mod why -m golang.org/x/text
```

- **Semanttinen versiointi ja tuontipolku.** Yhteensopimaton
  pääversio (v2 ja uudemmat) on eri tuontipolku: `.../pgx/v5`. Saman
  kirjaston eri pääversiot voivat olla samassa ohjelmassa.
- **Pienin versio (*minimal version selection*).** Go valitsee
  jokaisesta riippuvuudesta pienimmän version, joka täyttää kaikki
  vaatimukset, ei uusinta. Käännös on toistettava ilman lukitustiedostoa.
- **Tarkistussummat.** `go.sum` ja julkinen tarkistussummatietokanta
  (`sum.golang.org`) varmistavat, että sama versio on aina sama koodi.
  `go.sum` kuuluu versionhallintaan.
- **Välityspalvelin.** Moduulit haetaan oletuksena
  `proxy.golang.org`-palvelimelta. Yksityiset moduulit merkitään
  muuttujalla `GOPRIVATE`, ja `go mod vendor` kopioi riippuvuudet
  projektiin, jos verkkoa ei ole.
- **Työtilat.** `go work` yhdistää useita paikallisia moduuleja
  kehityksen ajaksi muuttamatta niiden `go.mod`-tiedostoja.

Tämän tutoriaalin muut esimerkit ovat yksittäisiä tiedostoja, jotka
käännetään ilman moduulia (`GO111MODULE=off`). Oikea projekti alkaa
aina komennolla `go mod init`.

## Alustus

Pakettitason muuttujat alustetaan riippuvuusjärjestyksessä, ja sen
jälkeen ajetaan paketin `init`-funktiot. Tuodut paketit alustetaan
ennen tuojaa. `init` on hyödyllinen harvoin, esimerkiksi ajurin
rekisteröintiin (`import _ "github.com/lib/pq"`). Piilotettu alustus
vaikeuttaa testausta, joten riippuvuudet välitetään mieluummin
parametreina.

## Käytännössä

- **Paketti tarjoaa yhden asian, ja sen nimi kertoo mitä.** Lyhyt
  yksikkömuotoinen nimi pienillä kirjaimilla (`varasto`, `tunnus`),
  ei `util`, `common` tai `helpers`.
- **Ei toistoa nimissä.** Kutsuja kirjoittaa `varasto.Varasto` ja
  `tunnus.Normalisoi`, joten nimeä `varasto.VarastoVarasto` tai
  `tunnus.NormalisoiTunnus` ei tarvita.
- **Pieni julkinen rajapinta.** Kaikki julkinen on lupaus
  yhteensopivuudesta. Aloita sisäisellä ja julkaise tarpeen mukaan;
  `internal` pitää moduulin yhteisen koodin piilossa.
- **Ohut `main`.** Pääohjelma lukee asetukset, kokoaa riippuvuudet ja
  kutsuu funktiota, joka palauttaa virheen. Testattava logiikka on
  paketeissa.
- **Riippuvuudet harkiten.** Go:n standardikirjasto kattaa HTTP:n,
  JSONin, kryptografian, testauksen ja lokituksen. Jokainen
  riippuvuus on ylläpito- ja tietoturvavastuu; `govulncheck` tarkistaa
  tunnetut haavoittuvuudet.
- **Ei syklisiä tuonteja.** Kääntäjä kieltää ne. Sykli korjataan
  siirtämällä yhteinen osa kolmanteen pakettiin tai kääntämällä
  riippuvuus rajapinnalla.
- **Hinta.** Paketit käännetään erikseen ja tulokset tallennetaan
  välimuistiin, joten käännös on nopea. Valmis ohjelma on yksi
  staattisesti linkattu tiedosto, jonka koko on muutamasta megatavusta
  ylöspäin.

## Itsearviointi

- Osaat jakaa koodin paketteihin ja hallita näkyvyyttä nimen
  alkukirjaimella ja `internal`-hakemistolla.
- Osaat luoda moduulin, lisätä ja päivittää riippuvuuksia ja kertoa,
  mitä `go.mod` ja `go.sum` sisältävät.
- Osaat selittää tuontipolun pääversion ja pienimmän version
  valinnan.
- Osaat järjestää projektin `cmd`-, `internal`- ja kirjastopaketteihin
  niin, että pääohjelma on ohut ja logiikka testattavissa.
