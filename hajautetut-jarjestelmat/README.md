# Hajautetut järjestelmät

Tiivis suomenkielinen tutoriaali useasta solmusta koostuvien
järjestelmien periaatteista: vikamallit ja vikailmaisimet, fyysiset ja
loogiset kellot (Lamport, vektorikello, hybridikello), replikointi
johtajalla ja kvoorumeilla, CRDT:t, konsistenssimallit ja
linearisoituvuuden tarkistin, Raft-konsensus, CAP ja PACELC,
kaksivaiheinen sitoutuminen ja idempotenssi sekä deterministinen
simulointitestaus. Kaikki toteutetaan C++23:lla deterministisessä
verkkosimulaattorissa ilman ulkoisia kirjastoja.

Valmis dokumentti:
[hajautetut-jarjestelmat.pdf](https://saperant.github.io/tutoriaalit/materiaalit/hajautetut-jarjestelmat.pdf),
pikaopas:
[hajautetut-jarjestelmat-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/hajautetut-jarjestelmat-pikaopas.pdf).

## Esimerkit

Esimerkit ovat hakemistossa `esimerkit/` ja simulaattori sekä yhteiset
osat hakemistossa `esimerkit/yhteinen/`. Testeissä jokainen esimerkki
käännetään GCC 14:llä ja Clang 20:llä sanitoijien kanssa, ja molempien
tulosteen on oltava sama kuin tiedostossa `<nimi>.odotettu`. Viiveet,
katoamiset, monistumiset, kaatumiset ja verkon jaot arvotaan
siemenestä, joten jokainen suoritus on toistettava.

```text
make testaa   # rakenne ja esimerkit
make pdf      # PDF:t
```

Kehityskontissa (`.devcontainer/hajautetut-jarjestelmat`) on kääntäjät ja
dokumenttityökalut.

## Lisenssi

CC BY-SA 4.0.
