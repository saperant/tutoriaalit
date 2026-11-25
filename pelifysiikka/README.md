# Pelifysiikka

Tiivis suomenkielinen tutoriaali pelien fysiikkasimulaatiosta
C++23:lla: jäykän kappaleen tila ja integrointi, kosketusten
muodostus, impulssivaste pyörimisen kanssa, kitka, rajoitteet ja
peräkkäisten impulssien ratkaisija, nivelet, pinot ja lepotila,
jatkuva törmäystunnistus, kangas sijaintipohjaisella dynamiikalla,
korkeuskenttävesi ja determinismi. Tavoite on uskottava ja stabiili
liike kiinteässä aikabudjetissa, ei tarkkuus.

Valmis dokumentti:
[pelifysiikka.pdf](https://saperant.github.io/tutoriaalit/materiaalit/pelifysiikka.pdf),
pikaopas:
[pelifysiikka-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/pelifysiikka-pikaopas.pdf).

Esitiedot: taito *3D-peliohjelmointi* ja sen kautta *Peliohjelmointi*.

## Esimerkit

Esimerkit ovat hakemistossa `esimerkit/` ja niiden yhteinen koodi,
pieni fysiikkamoottori, hakemistossa `esimerkit/yhteinen/`. Esimerkit
ovat fysiikkatestejä: ne tarkistavat liikemäärän ja
liikemäärämomentin säilymisen, sen, ettei energia kasva, pinon
pysymisen levossa, heilurin jakson analyyttista arvoa vastaan ja
simulaation toistumisen bitilleen. Ne käännetään testeissä GCC 14:llä
ja Clang 20:llä sanitoijien kanssa, ja molempien tulosteen on oltava
sama. Ikkunaa, näytönohjainta tai ulkoista fysiikkakirjastoa ei
tarvita: kuvat piirtää paketin oma pieni ohjelmistorenderöijä.

Otsakkeet `vektori.hpp`, `tulostus.hpp` ja `piirto.hpp` ovat kopioita
paketista `peliohjelmointi-3d`, jotta paketti on itsenäinen.

## Rakentaminen

```text
make testaa      # rakenne ja esimerkit
make pdf         # PDF:t
make kuvat       # kuvitus esimerkkiohjelmista (kuvat/)
make tiivisteet  # luvun 13 koe: tiiviste eri kääntäjillä ja lipuilla
```

Kuvat tuotetaan ajamalla esimerkit kuvitustilassa skriptillä
`kuvat/piirra.py` (Matplotlib ja NumPy); PNG-tiedostot ovat
versionhallinnassa.

Riippuvuudet: GCC 14 ja Clang 20. Kehityskontissa
(`.devcontainer/pelifysiikka`) ne ovat asennettuina.

Esimerkkien avaaminen kehityskontissa ja ajaminen: ks. [Kehitysympäristöt ja Dev Containers](../kehitysymparistot/), luku 2.

## Lisenssi

CC BY-SA 4.0.
