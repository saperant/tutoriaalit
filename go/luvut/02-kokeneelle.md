# Go kokeneelle {.runko-kokeneelle}

Tämä luku on tarkoitettu kehittäjälle, joka osaa C:tä, C++:aa, Javaa
tai Pythonia ja haluaa päästä Go:ssa nopeasti tuottavaksi. Luku kokoaa
Go:n ajattelutavan, vastaavuudet, hinnat ja tärkeimmät sudenkuopat.

## Ajattelutapa

- **Yksinkertaisuus on tavoite.** Go:sta puuttuu tietoisesti
  periytyminen, poikkeukset, ylikuormitus, oletusparametrit,
  makrot ja implisiittiset tyyppimuunnokset. Puute on valinta:
  koodi on pidempää mutta helpompaa lukea, ja sama asia tehdään
  yleensä yhdellä tavalla.
- **Virheet ovat arvoja.** Funktio palauttaa virheen viimeisenä
  paluuarvonaan, ja kutsuja tarkistaa sen heti: `if err != nil`.
  Paniikki on varattu ohjelmointivirheille (luku 8).
- **Nolla-arvo on käyttökelpoinen.** Jokaisella tyypillä on nolla-arvo
  (`0`, `""`, `nil`, nollattu rakenne), eikä alustamatonta muistia ole.
  Hyvin suunniteltu tyyppi, kuten `sync.Mutex` tai `bytes.Buffer`, toimii
  sellaisenaan ilman konstruktoria.
- **Rajapinnat toteutetaan implisiittisesti.** Tyyppi toteuttaa
  rajapinnan, jos sillä on rajapinnan metodit; `implements`-sanaa ei
  ole. Siksi rajapinta määritellään käyttäjän puolelle ja pidetään
  pienenä (luku 7).
- **Koostaminen periytymisen sijaan.** Rakenteen voi upottaa toiseen,
  jolloin sen metodit näkyvät ulommassa. Tämä on delegointia, ei
  alityypitystä.
- **Rinnakkaisuus on halpaa.** Goroutine on kevyt säie (muutama
  kilotavu pinoa), ja niitä voi olla satoja tuhansia. Ajonaikainen
  ympäristö jakaa ne käyttöjärjestelmän säikeille. Kanavat välittävät
  dataa goroutinejen välillä: "älä viesti jakamalla muistia, vaan
  jaa muisti viestimällä".
- **Työkalut ovat osa kieltä.** `gofmt` päättää muotoilun, `go vet`
  tarkistaa yleiset virheet, ja `go test` on vakiotestikehys. Kääntäjä
  hylkää käyttämättömät muuttujat ja tuonnit:

```{.go tiedosto="esimerkit/02-kayttamaton.ei-kaanny.go"}
```

```
./02-kayttamaton.ei-kaanny.go:5:2: "os" imported and not used
./02-kayttamaton.ei-kaanny.go:10:2: declared and not used: virheita
```

Tämän kirjan `.ei-kaanny`-esimerkeissä virheellinen rivi on merkitty
kommentilla `@virhe`. Testeissä varmistetaan, että tiedosto ei läpäise
tarkistusta (`gofmt`, `go vet` ja käännös) sellaisenaan mutta läpäisee,
kun merkityt rivit poistetaan.

## Vastaavuudet

| Asia | C/C++ | Java | Python | Go |
|------------|------------|------------|------------|------------|
| Dynaaminen taulukko | `std::vector` | `ArrayList` | `list` | viipale `[]T` |
| Hajautustaulu | `unordered_map` | `HashMap` | `dict` | `map[K]V` |
| Joukko | `unordered_set` | `HashSet` | `set` | `map[K]struct{}` |
| Luokka | `class` | `class` | `class` | `struct` + metodit |
| Rajapinta | abstrakti luokka | `interface` | protokolla | `interface`, implisiittinen |
| Periytyminen | `: public B` | `extends` | `class A(B)` | upotus (koostaminen) |
| Virhe | poikkeus, paluuarvo | poikkeus | poikkeus | `error`-paluuarvo |
| Siivous | hajotin, RAII | `try`-`finally` | `with` | `defer` |
| Säie | `std::thread` | `Thread` | `threading` | `go f()` |
| Säieturvallinen jono | itse tehty | `BlockingQueue` | `queue.Queue` | kanava `chan T` |
| Geneerisyys | `template` | `<T>` | tyyppivihjeet | `[T any]` |
| Näkyvyys | `public`, `private` | `public`, `private` | `_`-etuliite | iso alkukirjain |
| Paketit | CMake, Conan | Maven | pip | `go mod` |

Esimerkki näyttää monta paluuarvoa, virheen käärimisen ja implisiittisen
rajapinnan:

```{.go tiedosto="esimerkit/02-vastaavuudet.go" osa="virhe"}
```

```{.go tiedosto="esimerkit/02-vastaavuudet.go" osa="rajapinta"}
```

```{.go tiedosto="esimerkit/02-vastaavuudet.go" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/02-vastaavuudet.odotettu"}
```

## Hinnat

Go:n suorituskyky on lähellä Javaa ja selvästi Pythonia parempi, mutta
C:hen ja Rustiin verrattuna seuraavat asiat maksavat:

| Toiminto | Hinta | Huomio |
|----------|-------|--------|
| Kekoallokaatio | kymmeniä ns + roskienkeruun työ | kääntäjän pakoanalyysi päättää (luku 5) |
| Rajapintakutsu | epäsuora kutsu, estää usein inline-laajennuksen | kuumissa silmukoissa konkreettinen tyyppi |
| Arvo rajapinnaksi | allokaatio, jos arvo ei mahdu osoittimeen | `any`-parametrit, `fmt.Println` |
| `defer` | muutama ns (1.14 alkaen lähes ilmainen) | ei silmukassa: ajetaan vasta funktion lopussa |
| Goroutine | ~1 µs ja 2–8 kt pinoa | halpa mutta ei ilmainen; vuoto kerryttää muistia |
| Kanava | ~50–100 ns lähetys ja vastaanotto | mutex on halvempi yksinkertaiseen tilaan |
| `string(b)`, `[]byte(s)` | kopio ja allokaatio | `strings.Builder`, `bytes`-paketti |
| `append` | kasvattaa kapasiteettia ~1,25–2-kertaiseksi | `make([]T, 0, n)`, kun koko tiedetään |
| Heijastus (`reflect`) | hidas, ei tyyppitarkistusta | `encoding/json` käyttää sitä |
| Paniikki ja `recover` | kallis, kuten poikkeus | vain virhetilanteisiin |
| cgo-kutsu | ~tuhat kertaa Go-funktiokutsun hinta | vältä hienojakoisia kutsuja |

Roskienkeruu on rinnakkainen merkitse ja pyyhi -keruu, jonka tauot ovat
tyypillisesti alle millisekunnin. Sen kokonaiskuorma riippuu
allokaatioiden määrästä. Siksi Go:n optimointi on enimmäkseen
allokaatioiden vähentämistä.

## Tärkeimmät sudenkuopat

1. **Nil-osoitin rajapinnassa ei ole nil.** Funktio, joka palauttaa
   `error`-tyyppinä nil-arvoisen `*OmaVirhe`-osoittimen, palauttaa
   rajapinnan, joka ei ole `nil` (luku 7).
2. **`append` voi kirjoittaa toisen viipaleen päälle.** Viipaleet
   jakavat taustataulukon, kunnes `append` varaa uuden (luku 6).
3. **Kirjoitus nil-karttaan kaatuu.** Kartta on alustettava `make`- tai
   literaalilauseella; lukeminen nil-kartasta on sallittua.
4. **Goroutine-vuodot.** Goroutine, joka odottaa kanavaa, jota kukaan ei
   enää lue, ei pääty koskaan (luku 10).
5. **Kartan läpikäyntijärjestys on satunnainen.** Järjestä avaimet,
   jos tuloste tai testi riippuu järjestyksestä.
6. **Datakilpailu.** Jaettua muuttujaa ei saa käyttää useasta
   goroutinesta ilman synkronointia; aja testit `-race`-lipulla.
7. **Kartan ja viipaleen arvot ovat kopioita.** `for _, x := range s`
   antaa kopion alkiosta, ja kartan rakenne-arvon kenttää ei voi
   muuttaa paikallaan.
8. **`http.Client` ilman aikakatkaisua** odottaa ikuisesti. Oletusasiakas
   `http.DefaultClient` on sellainen (luku 11).

## Lukuohje

Lue ensin lukujen *Itsearviointi*-osiot ja ohita luvut, joiden asiat
osaat. Lähes kaikille uusia ovat luvut 6 (viipaleet), 7 (rajapinnat),
8 (virheet) ja 10 (rinnakkaisuus). C-ohjelmoijalle luku 5 kertoo,
mitä roskienkeruu muuttaa; Java-ohjelmoijalle luku 7 kertoo, miksi
rajapinnat kirjoitetaan toisin. Pikaopas tiivistää syntaksin ja
idiomit.
