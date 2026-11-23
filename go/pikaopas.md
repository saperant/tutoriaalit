---
title: Go
subtitle: Pikaopas kokeneelle kehittäjälle · Go 1.23
---

# Työkalut

| Tarkoitus | Komento |
|-----------|---------|
| Moduuli | `go mod init example.com/nimi`, `go mod tidy` |
| Käännös, ajo | `go build ./...`, `go run ./cmd/ohjelma` |
| Ristikäännös | `GOOS=linux GOARCH=arm64 go build` |
| Laatu | `gofmt -l .`, `go vet ./...`, `staticcheck ./...` |
| Testit | `go test -race -count=1 ./...`, `-run 'TestX/ali'` |
| Kattavuus | `go test -cover ./...` |
| Vertailuajo | `go test -run '^$' -bench . -benchmem` |
| Fuzz | `go test -fuzz=FuzzX ./paketti` |
| Profiili | `go tool pprof -http=:8080 cpu.out` |
| Pakoanalyysi | `go build -gcflags=-m` |
| Dokumentaatio | `go doc strings.Cut` |

# Perussyntaksi

```{.go tiedosto="esimerkit/pikaopas.go" osa="perus"}
```

- Nolla-arvot: `0`, `""`, `false`, `nil`; ei alustamatonta muistia.
- Ei implisiittisiä muunnoksia: `float64(n)`, `int64(x)`.
  Kokonaisluvun ylivuoto kiertää hiljaa.
- Käyttämätön muuttuja tai tuonti on käännösvirhe; `_` hylkää arvon.
- `for` on ainoa silmukka; `range` viipaleen, kartan, merkkijonon,
  kanavan, kokonaisluvun ja `iter.Seq`-funktion yli.
- `switch` ei valu seuraavaan haaraan; `switch {}` ilman ehtoa.
- `defer` ajetaan funktion lopussa käänteisessä järjestyksessä;
  argumentit lasketaan heti.

# Tyypit, metodit ja rajapinnat

```{.go tiedosto="esimerkit/pikaopas.go" osa="tyypit"}
```

- Iso alkukirjain = julkinen paketin ulkopuolelle.
- Osoitinvastaanottaja, kun metodi muuttaa tilaa tai tyypissä on lukko.
  Vain `*T` toteuttaa rajapinnan, jos metodi on `*T`:llä.
- Rajapinta kuluttajan puolelle, 1–3 metodia. Ota rajapinta, palauta
  rakenne. `var _ I = (*T)(nil)` tarkistaa toteutuksen.
- Upotus = delegointi, ei periytymistä.
- Rajoitteet: `any`, `comparable`, `cmp.Ordered`, `~int | ~float64`.

# Virheet

```{.go tiedosto="esimerkit/pikaopas.go" osa="virheet"}
```

| Tarve | Keino |
|-------|-------|
| uusi virhe | `errors.New("...")`, `fmt.Errorf("...: %w", err)` |
| virheen laji | vartija `var ErrX = errors.New(...)`, `errors.Is` |
| virheen tiedot | tyyppi + `Unwrap()`, `errors.As(err, &kohde)` |
| useita | `errors.Join(e1, e2)` |
| ohjelmointivirhe | `panic`; rajalla `defer` + `recover()` |

- Käsittele tai palauta, ei molempia. Viesti pienellä, ei pistettä.
- Palauta `nil`-literaali, ei nil-osoitinta `error`-tyyppinä.

# Kokoelmat

```{.go tiedosto="esimerkit/pikaopas.go" osa="kaytto"}
```

| Toiminto | Kirjoitus |
|----------|-----------|
| esivaraus | `make([]T, 0, n)`, `make(map[K]V, n)` |
| kopio | `slices.Clone(s)`, `maps.Clone(m)` |
| lajittelu | `slices.Sort(s)`, `slices.SortFunc(s, cmp)` |
| avaimet järjestyksessä | `slices.Sorted(maps.Keys(m))` |
| haku | `slices.Index`, `Contains`, `BinarySearch` |
| joukko | `map[K]struct{}` |
| merkkijonon kokoaminen | `strings.Builder`, `strings.Join` |
| jako | `strings.Cut`, `Fields`, `Split` |
| merkit | `for i, r := range s`, `utf8.RuneCountInString` |

# Rinnakkaisuus

```{.go tiedosto="esimerkit/pikaopas.go" osa="rinnakkaisuus"}
```

```{.tuloste tiedosto="esimerkit/pikaopas.odotettu"}
```

| Tarve | Väline |
|-------|--------|
| odota goroutinet | `sync.WaitGroup`, `errgroup.Group` |
| jaettu tila | `sync.Mutex`, `sync.RWMutex` |
| laskuri, lippu | `atomic.Int64`, `atomic.Bool` |
| kertaalustus | `sync.Once`, `sync.OnceValue` |
| peruutus, aikaraja | `context.WithCancel`, `WithTimeout` |
| rajattu rinnakkaisuus | työntekijäallas, `chan struct{}` semaforina |
| aikakatkaisu | `select` + `ctx.Done()` tai `time.After` |

- Lähettäjä sulkee kanavan. Lähetys suljettuun = paniikki,
  `nil`-kanava odottaa ikuisesti.
- Jokaisella goroutinella on lopetusehto; `ctx` ensimmäinen parametri,
  `defer cancel()`. Testit aina `-race`-lipulla.

# Hinnat

| Halpaa | Kallista |
|--------|----------|
| arvot pinossa, rakenteet arvoina | kekoallokaatio + roskienkeruu |
| virheen palautus | `panic`/`recover` |
| `strconv`, `strings.Builder` | `fmt.Sprintf`, `+=` silmukassa |
| geneerinen `[]T` | `[]any`, rajapintakutsut kuumassa silmukassa |
| goroutine (~1 µs, kt:ja) | vuotavat goroutinet |
| atominen, vapaa lukko | kilpailtu lukko, kanava pieneen tilaan |
| ristikäännös | cgo-kutsu, `reflect`, `encoding/json` |

# Sudenkuopat

- `append` voi kirjoittaa toisen viipaleen datan päälle: `s[a:b:b]`.
- Kirjoitus nil-karttaan kaatuu; kartan järjestys on satunnainen.
- Nil-osoitin rajapinnassa `!= nil`.
- `defer` silmukassa ajetaan vasta funktion lopussa.
- Lukkoa sisältävää rakennetta ei kopioida (`go vet` copylocks).
- `http.Client{}` ilman `Timeout`-kenttää odottaa ikuisesti; sulje
  aina `resp.Body`.
- Paniikki goroutinessa kaataa koko ohjelman; `recover` vain samassa.
