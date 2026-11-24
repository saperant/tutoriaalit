# Rinnakkaisohjelmointi

Tiivis suomenkielinen tutoriaali moniydinsuorittimien hyödyntämisestä
C++:lla: säikeet ja tehtävät, säiepooli, C++:n muistimalli ja
litmus-testit, atomiset operaatiot, lukot ja odotusvälineet, lukottomat
tietorakenteet ja muistin takaisinotto, rinnakkaiset algoritmit ja
työnjako sekä rinnakkaisuusvirheiden etsintä ThreadSanitizerilla.

Valmis dokumentti:
[rinnakkaisohjelmointi.pdf](https://saperant.github.io/tutoriaalit/materiaalit/rinnakkaisohjelmointi.pdf),
pikaopas:
[rinnakkaisohjelmointi-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/rinnakkaisohjelmointi-pikaopas.pdf).

## Esimerkit

Esimerkit ovat hakemistossa `esimerkit/`, ja säiepooli on hakemistossa
`esimerkit/yhteinen/`. Testeissä jokainen esimerkki käännetään GCC 14:llä
ja Clang 20:llä AddressSanitizerin ja UBSanin kanssa ja ajetaan, ja
merkinnällä `// TSAN` varustetut lisäksi ThreadSanitizerilla. Tulosteen on
oltava sama kuin tiedostossa `<nimi>.odotettu`; koneesta riippuvat
mittaukset menevät virhetulosteeseen.

Hakemiston `esimerkit/tsan/` ohjelmissa on tarkoituksellinen
rinnakkaisuusvirhe. `esimerkit/Makefile` ajaa ne ThreadSanitizerilla ja
tarkistaa, että raportissa on tiedoston `<nimi>.raportti` rivit.

```text
make testaa   # rakenne, esimerkit ja ThreadSanitizer-raportit
make pdf      # PDF:t
```

Kehityskontissa (`.devcontainer/rinnakkaisohjelmointi`) ovat kääntäjät,
sanitoijat ja dokumenttityökalut.

## Lisenssi

CC BY-SA 4.0.
