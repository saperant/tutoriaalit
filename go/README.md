# Go

Tiivis suomenkielinen Go-tutoriaali ohjelmoinnin perusteet osaavalle
(Go 1.23). Valmis dokumentti: [go.pdf](https://saperant.github.io/tutoriaalit/materiaalit/go.pdf), pikaopas:
[go-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/go-pikaopas.pdf).

## Sisältö

1. Johdanto – käyttökohteet, versiot, työkalut, ensimmäinen ohjelma
2. Go kokeneelle – ajattelutapa, vastaavuudet C:hen, Javaan ja
   Pythoniin, hinnat, sudenkuopat
3. Tyypit, lausekkeet ja syöte – nolla-arvot, muunnokset, rakenne ja
   metodi, `iota`, `fmt`, `bufio.Scanner`, tiedostot ja `flag`
4. Ohjausrakenteet ja funktiot – `defer`, sulkeumat, tilakone
5. Muisti, osoittimet ja allokaatiot – arvot ja viitteet,
   pakoanalyysi, roskienkeruu
6. Viipaleet, kartat ja merkkijonot – `append`-sudenkuoppa, UTF-8,
   iteraattorit, `slices` ja `container/heap`
7. Rakenteet, rajapinnat ja geneerisyys – upotus, pienet rajapinnat,
   nil-rajapinta, funktionaaliset optiot
8. Virheenkäsittely – `%w`, `errors.Is`/`As`, `errors.Join`, paniikki
9. Paketit ja moduulit – näkyvyys, `internal`, `go.mod`,
   dokumentaatiokommentit ja `go doc`, riippuvuudet
10. Goroutinet, kanavat ja context – ajastimet, työntekijäallas,
    vuodot, putki, kilpailutilanteet
11. Verkkopalvelut `net/http`-paketilla – reititys, JSON, välikerros,
    `httptest`, hallittu sammutus
12. Työkalut, testaus ja laatu – taulukkotestit, esimerkkifunktiot,
    fuzz, vertailuajot, `pprof`, `slog`
13. Lopuksi – mallit, nyrkkisäännöt, hinnat, kirjastot ja lähteet

## Rakentaminen

```text
make testaa   # gofmt, go vet, käännös ja ajo; moduulin testit -race
make pdf      # rakentaa go.pdf:n ja go-pikaopas.pdf:n
```

Esimerkit ovat hakemistossa `esimerkit/`. Yksittäiset ohjelmat
käännetään ilman moduulia; `esimerkit/09-kauppa` on oikea moduuli
testeineen, ja `esimerkit/Makefile` ajaa sen testit,
kilpailutilanteiden tunnistimen ja `go doc` -tarkistuksen. Riippuvuudet on lueteltu repositorion
juuren README-tiedostossa. Kehityskontti: `.devcontainer/go`.

Esimerkkien avaaminen kehityskontissa ja ajaminen: ks. [Kehitysympäristöt ja Dev Containers](../kehitysymparistot/), luku 2.
