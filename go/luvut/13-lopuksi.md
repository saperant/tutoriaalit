# Lopuksi {.runko-kaytannot .runko-lahteet}

## Mallit ja idiomit

| Malli | Mitä se ratkaisee | Luku |
|-------|-------------------|------|
| Hyödyllinen nolla-arvo | tyyppi toimii ilman konstruktoria | 3, 7 |
| Konstruktorifunktio `UusiX` | invariantti, joka nolla-arvosta puuttuu | 7 |
| Varhainen paluu | virhepolku käsitellään heti, onnistunut polku vasemmalla | 4 |
| `defer` heti resurssin jälkeen | vapautus kaikilla paluupoluilla | 4 |
| Virheen kääriminen `%w` | kontekstia sisältävä, tutkittava virheketju | 8 |
| Vartijavirhe ja virhetyyppi | kutsuja reagoi virheen lajiin | 8 |
| Pieni rajapinta kuluttajan puolella | löyhä kytkentä ja helppo testaus | 7 |
| Ota rajapinta, palauta rakenne | joustava kutsu, laajennettava tulos | 7 |
| Koristelija `io.Writer`in ympärillä | toiminto lisätään koostamalla | 7 |
| Upotus | delegointi ilman välitysmetodeja | 7 |
| Funktionaaliset optiot | laajennettava konstruktori | 7 |
| Täysi viipalelauseke `s[a:b:b]` | `append` ei kirjoita toisen datan päälle | 6 |
| Joukko `map[K]struct{}` | jäsenyys ilman arvoja | 6 |
| Iteraattori `iter.Seq` | läpikäynti paljastamatta rakennetta | 6 |
| Työntekijäallas | rajattu rinnakkaisuus | 10 |
| Putki ja ryhmän peruutus | vaiheet, jotka lopettavat yhdessä | 10 |
| `context` ensimmäisenä parametrina | peruutus ja aikarajat kutsuketjun läpi | 10 |
| Välikerros | lokitus, tunnistautuminen ja paniikit yhdessä kohdassa | 11 |
| Hallittu sammutus | käynnissä olevat pyynnöt valmistuvat | 11 |
| Ohut `main`, `run(io.Reader, io.Writer) error` | ohjelma on testattavissa | 9, 12 |
| Taulukkotesti | uusi testitapaus on yksi rivi | 12 |
| Kultainen tiedosto | pitkät tulosteet versionhallintaan | 12 |

## Nyrkkisäännöt

1. Selkeä on parempi kuin näppärä. Kirjoita koodi niin, että sen voi
   lukea ilman muuta tiedostoa.
2. Tarkista jokainen virhe. Käsittele se tai palauta se kontekstin
   kanssa, mutta älä molempia.
3. Älä aloita goroutinea tietämättä, miten se päättyy.
4. Rajapinta kuvaa tarpeen, ei toteutusta. Mitä suurempi rajapinta,
   sitä heikompi abstraktio.
5. Kanava omistuksen siirtoon ja tapahtumiin, lukko jaettuun tilaan.
6. Kopio on halvempi kuin riippuvuus: pieni apufunktio kannattaa
   kirjoittaa itse.
7. `gofmt`-muotoilu ei ole kenenkään suosikki, mutta se on kaikkien
   tyyli.
8. Ei paniikkia normaalissa ohjelmankulussa.
9. Dokumentoi jokainen julkinen nimi kommentilla, joka alkaa nimellä.
10. Mittaa ennen optimointia; optimoi allokaatiot ensin.

## Hinnat lyhyesti

| Halpaa | Kallista |
|--------|----------|
| Pinomuuttujat, rakenteet arvoina | Kekoallokaatio ja roskienkeruun työ |
| Funktiokutsu, inline-laajennettu metodi | Rajapintakutsu kuumassa silmukassa |
| Virheen palautus | Paniikki ja `recover` |
| Goroutine (verrattuna säikeeseen) | Miljoona goroutinea tai vuotavat goroutinet |
| `sync/atomic`, kilpailematon lukko | Kanava hienojakoiseen tilaan, kilpailtu lukko |
| `append` esivaratulla kapasiteetilla | `+=` merkkijonoihin silmukassa |
| `strings.Builder`, `strconv` | `fmt.Sprintf` kuumassa polussa |
| Geneerinen `[]T` | `[]any` ja tyyppivarmistukset |
| Käännös ja ristikäännös | cgo-kutsut ja heijastus (`reflect`) |

## Yleiset kirjastot

| Tarkoitus | Kirjasto |
|-----------|----------|
| Rinnakkaisuus | `golang.org/x/sync/errgroup`, `semaphore` |
| HTTP-reititys | `github.com/go-chi/chi` (tai standardi `ServeMux`) |
| gRPC | `google.golang.org/grpc`, `protobuf` |
| PostgreSQL | `github.com/jackc/pgx` |
| SQL-koodin tuottaminen | `sqlc` |
| Komentorivi | `github.com/spf13/cobra`, standardi `flag` |
| Asetukset | ympäristömuuttujat ja `flag`; `github.com/spf13/viper` |
| Testaus | standardi `testing`; `github.com/stretchr/testify` |
| Laatu | `staticcheck`, `golangci-lint`, `govulncheck` |
| Lokitus | standardi `log/slog` |
| Telemetria | `go.opentelemetry.io/otel` |

## Lähteet ja jatkolukeminen

Ensisijaiset lähteet:

- *The Go Programming Language Specification*:
  <https://go.dev/ref/spec>
- *Effective Go*: <https://go.dev/doc/effective_go>
- Go Code Review Comments:
  <https://go.dev/wiki/CodeReviewComments>
- Go-muistimalli: <https://go.dev/ref/mem>
- Standardikirjaston dokumentaatio: <https://pkg.go.dev/std>
- Go-blogi, erityisesti kirjoitukset virheiden käärimisestä,
  viipaleista, kontekstista, iteraattoreista ja
  rinnakkaisuusmalleista: <https://go.dev/blog/>
- Moduulien ohjeet: <https://go.dev/doc/modules/>
- Diagnostiikka ja profilointi: <https://go.dev/doc/diagnostics>

Kirjat ja kurssit:

- Alan A. A. Donovan ja Brian W. Kernighan: *The Go Programming
  Language*. Addison-Wesley, 2015. Perusteos; geneerisyys puuttuu.
- Teiva Harsanyi: *100 Go Mistakes and How to Avoid Them*. Manning,
  2022. Sudenkuopat ja hinnat perusteluineen.
- Katherine Cox-Buday: *Concurrency in Go*. O'Reilly, 2017.
- Jon Bodner: *Learning Go*, 2. painos. O'Reilly, 2024.
- *Learn Go with Tests*: <https://quii.gitbook.io/learn-go-with-tests>
  (testivetoinen johdatus, MIT-lisenssi).
- Uber Go Style Guide: <https://github.com/uber-go/guide>
  (CC BY 4.0).

Taitopuussa Go:sta jatketaan taitoihin *Taustapalvelut*,
*Verkko-ohjelmointi*, *Säiliöt ja pilvi-infrastruktuuri* ja
*Hajautetut järjestelmät*.
Rinnakkaisuuden teoria on taidossa *Rinnakkaisohjelmointi* ja
suorituskyvyn mittaaminen taidossa *Suorituskyvyn analyysi ja
optimointi*.
