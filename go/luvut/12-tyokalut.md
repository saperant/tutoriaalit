# Työkalut, testaus ja laatu {.runko-tyokalut}

Go:n työkalut tulevat kielen mukana, ja niiden käyttö on yhtenäistä
kaikissa projekteissa: `go build`, `go test`, `go vet` ja `gofmt` toimivat
samoin jokaisessa moduulissa ilman asetustiedostoja.

## Käännös

| Komento | Tehtävä |
|---------|---------|
| `go build ./...` | kääntää kaikki paketit |
| `go build -o bin/kauppa ./cmd/kauppa` | ohjelma nimettyyn tiedostoon |
| `GOOS=linux GOARCH=arm64 go build` | ristikäännös, ei lisätyökaluja |
| `CGO_ENABLED=0 go build` | täysin staattinen ohjelma ilman C-kirjastoja |
| `go build -ldflags "-X main.versio=1.2.0"` | muuttujan arvo käännöksessä |
| `go build -trimpath` | poistaa paikalliset polut, toistettava käännös |
| `go build -gcflags=-m` | pakoanalyysin ja inline-laajennusten raportti |
| `go install ./cmd/kauppa` | kääntää ja asentaa hakemistoon `$GOBIN` |

Ristikäännös on Go:n vahvuus: yksi komento tuottaa ohjelman toiselle
käyttöjärjestelmälle ja arkkitehtuurille. Konttikuvaan riittää yksi
staattinen tiedosto ilman käyttöjärjestelmän kirjastoja.

## Laadun tarkistus

`gofmt` muotoilee koodin. Muotoilusta ei ole valintoja, joten CI
tarkistaa vain, että `gofmt -l .` ei tulosta mitään. `goimports` tekee
saman ja järjestää tuonnit.

`go vet` etsii virheitä, jotka kääntyvät mutta ovat lähes varmasti
vääriä: muotoilujonon ja argumenttien ristiriidat, lukon kopioinnin,
saavuttamattoman koodin ja väärin kirjoitetut testifunktiot.

```{.go tiedosto="esimerkit/12-vet.ei-kaanny.go"}
```

```
./12-vet.ei-kaanny.go:7:2: fmt.Printf format %d has arg nimi of wrong
type string
```

Laajempi analyysi tehdään `staticcheck`-työkalulla tai
`golangci-lint`-kokoelmalla, joka ajaa kymmeniä analysaattoreita, kuten
käsittelemättömien virheiden etsijän `errcheck`. `govulncheck`
tarkistaa, kutsuuko ohjelma riippuvuuksien tunnettuja haavoittuvia
funktioita.

## Testit

Testit ovat samassa hakemistossa tiedostoissa `*_test.go`. Testifunktio
on `func TestXxx(t *testing.T)`. `t.Error` ja `t.Errorf` merkitsevät
testin epäonnistuneeksi ja jatkavat, `t.Fatal` ja `t.Fatalf` lopettavat
testin heti. Kirjastoja ei tarvita: vertailu on tavallinen `if`.

### Taulukkotestit

Go-testien vakiomalli on *taulukkotesti* (*table-driven test*): tapaukset
ovat rakenneviipaleessa, ja `t.Run` ajaa jokaisen omana alitestinään.
Epäonnistunut tapaus näkyy nimellään, ja yksittäisen tapauksen voi ajaa
lipulla `-run 'TestNormalisoi/ei_viivaa'`.

```{.go tiedosto="esimerkit/09-kauppa/internal/tunnus/tunnus_test.go" osa="taulukko"}
```

Testi voi olla paketin sisällä (`package tunnus`), jolloin se näkee
sisäiset nimet, tai ulkoisessa testipaketissa (`package varasto_test`),
jolloin se käyttää vain julkista rajapintaa kuten oikea kutsuja.
Testiapuri merkitään `t.Helper()`-kutsulla, jotta virheilmoitus osoittaa
kutsuvaa riviä:

```{.go tiedosto="esimerkit/09-kauppa/varasto/varasto_test.go" osa="apu"}
```

```{.go tiedosto="esimerkit/09-kauppa/varasto/varasto_test.go" osa="ota"}
```

`t.Parallel()` ajaa alitestit rinnakkain. Se nopeuttaa hitaita testejä
ja paljastaa jaetun tilan, kun testit ajetaan lipulla `-race`:

```{.go tiedosto="esimerkit/09-kauppa/varasto/varasto_test.go" osa="rinnakkain"}
```

### Esimerkkifunktiot ja kultaiset tiedostot

Esimerkkifunktio `ExampleXxx` on dokumentaatiota, joka näkyy
`go doc`-tulosteessa ja pkg.go.dev-sivustolla. `go test` ajaa sen ja
vertaa tulostetta `Output:`-kommenttiin, joten dokumentaatio ei
vanhene:

```{.go tiedosto="esimerkit/09-kauppa/varasto/varasto_test.go" osa="esimerkki"}
```

Pitkät odotetut tulosteet ovat tiedostoissa hakemistossa `testdata`.
Lippu `-paivita` kirjoittaa ne uudelleen, kun muutos on tarkoituksellinen,
ja muutos tarkistetaan versionhallinnan erona:

```{.go tiedosto="esimerkit/09-kauppa/cmd/kauppa/main_test.go" osa="kulta"}
```

### Fuzz-testaus

Fuzz-testi (Go 1.18) saa satunnaisia syötteitä ja tarkistaa
ominaisuuden, joka pätee kaikille syötteille. `go test` ajaa vain
siemenet ja aiemmin löydetyt virheelliset syötteet (hakemisto
`testdata/fuzz`); `go test -fuzz=FuzzNormalisoi` generoi uusia, kunnes
se keskeytetään.

```{.go tiedosto="esimerkit/09-kauppa/internal/tunnus/tunnus_test.go" osa="fuzz"}
```

### Komennot

```
$ go test ./...                      # kaikki paketit
$ go test -race -count=1 ./...       # kilpailut, ei välimuistia
$ go test -run TestOta/liikaa -v ./varasto
$ go test -cover ./...               # kattavuus prosentteina
$ go test -coverprofile=c.out ./... && go tool cover -html=c.out
$ go test -fuzz=FuzzNormalisoi -fuzztime=30s ./internal/tunnus
$ go test -short ./...               # testi voi tarkistaa testing.Short()
```

Tämän tutoriaalin `esimerkit/Makefile` ajaa moduulin testit,
fuzz-siemenet ja vertailuajot kilpailutilanteiden tunnistimen kanssa.

## Vertailuajot ja profilointi

Vertailuajo (*benchmark*) `func BenchmarkXxx(b *testing.B)` toistaa
mitattavaa koodia `b.N` kertaa. `b.ReportAllocs()` tai lippu `-benchmem`
raportoi allokaatiot:

```{.go tiedosto="esimerkit/09-kauppa/varasto/varasto_test.go" osa="vertailu"}
```

```
$ go test -run '^$' -bench . -benchmem ./varasto
BenchmarkLisaa-4   29735126    37.49 ns/op    0 B/op   0 allocs/op
```

Mittaukset vaihtelevat, joten muutosta verrataan useamman ajon
tilastolla: `go test -bench . -count=10 > uusi.txt` ja
`benchstat vanha.txt uusi.txt`.

Profiili kertoo, mihin aika ja muisti kuluvat:

| Komento | Tehtävä |
|---------|---------|
| `go test -cpuprofile cpu.out -bench .` | suoritinprofiili vertailuajosta |
| `go test -memprofile mem.out -bench .` | allokaatioprofiili |
| `go tool pprof -http=:8080 cpu.out` | liekkikaavio ja lähdekoodinäkymä selaimessa |
| `import _ "net/http/pprof"` | profiilit käynnissä olevasta palvelusta |
| `go test -trace trace.out` ja `go tool trace` | goroutinejen ja roskienkeruun aikajana |
| `dlv debug ./cmd/kauppa` | Delve-debuggeri |

Suunnatut optimoinnit (*profile-guided optimization*, Go 1.21): kun
tuotannosta kerätty profiili tallennetaan pääpaketin hakemistoon nimellä
`default.pgo`, kääntäjä laajentaa kuumat funktiot ja nopeuttaa ohjelmaa
tyypillisesti muutamia prosentteja.

## Lokitus

`log/slog` (Go 1.21) on standardikirjaston rakenteinen loki. Tietueet
ovat avain–arvo-pareja, jotka lokijärjestelmä voi hakea ja suodattaa.
`With` liittää kentät kaikkiin myöhempiin tietueisiin, esimerkiksi
pyynnön tunnisteen:

```{.go tiedosto="esimerkit/12-loki.go" osa="slog"}
```

```{.tuloste tiedosto="esimerkit/12-loki.odotettu"}
```

## Käytännössä

- **CI:n vähimmäistaso**: `gofmt -l`, `go vet ./...`,
  `go test -race ./...` ja `staticcheck` tai `golangci-lint`. Kaikki
  ovat nopeita, ja ne löytävät suurimman osan rutiinivirheistä.
- **Taulukkotestit ja alitestit** kaikkialla, missä on enemmän kuin
  kaksi tapausta. Uusi tapaus on yksi rivi.
- **Testaa julkista rajapintaa.** Ulkoinen testipaketti pitää testit
  irti toteutuksesta, ja esimerkkifunktiot toimivat samalla
  dokumentaationa.
- **Korvikkeet rajapinnoilla**, ei kirjastoilla. Kun koodi ottaa
  vastaan pienen rajapinnan, testi antaa sille käsin kirjoitetun
  toteutuksen. `testify` on suosittu väittämäkirjasto, mutta pelkkä
  `testing` riittää.
- **Ei aikaan perustuvia odotuksia testeissä.** `time.Sleep` tekee
  testeistä hitaita ja epävakaita; synkronoi kanavilla tai
  `WaitGroup`-laskurilla.
- **Mittaa ennen optimointia** ja vertaa `benchstat`-työkalulla.
  Optimointi Go:ssa on enimmäkseen allokaatioiden poistamista profiilin
  osoittamista paikoista.
- **Rakenteinen loki**, ei `fmt.Println`. Tuotannossa JSON-muoto ja
  pyyntökohtaiset kentät `With`-kutsulla.

## Itsearviointi

- Osaat kääntää ohjelman toiselle alustalle ja liittää siihen
  versiotiedon käännöksessä.
- Osaat kirjoittaa taulukkotestejä alitesteineen, testiapureita ja
  esimerkkifunktioita.
- Osaat käyttää kultaisia tiedostoja ja fuzz-testausta.
- Osaat kirjoittaa vertailuajon, mitata allokaatiot ja profiloida
  ohjelman `pprof`-työkalulla.
- Osaat ottaa käyttöön `go vet`-, `staticcheck`- ja `-race`-tarkistukset
  CI:ssä.
- Osaat käyttää `log/slog`-pakettia rakenteiseen lokitukseen.
