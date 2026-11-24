# Säteenseuranta ja fysikaalinen valaistus

Tiivis suomenkielinen tutoriaali valon kulun simuloinnista:
säteen ja kappaleiden leikkaukset, kiihdytysrakenteet (BVH),
Whitted-säteenseuranta, radiometria ja renderöintiyhtälö, Monte
Carlo -integrointi, polunseuranta suoralla valaistuksella ja
venäläisellä ruletilla, monitärkeysnäytteistys, mikrofasettimateriaalit
(GGX) sekä näytteistys, kohinan poisto ja sävykuvaus. Kaikki
toteutetaan pienenä C++23-renderöijänä ilman ulkoisia kirjastoja.

Valmis dokumentti:
[sateenseuranta.pdf](https://saperant.github.io/tutoriaalit/materiaalit/sateenseuranta.pdf),
pikaopas:
[sateenseuranta-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/sateenseuranta-pikaopas.pdf).

## Esimerkit

Esimerkit ovat hakemistossa `esimerkit/` ja yhteinen kirjasto
hakemistossa `esimerkit/yhteinen/`. Testeissä jokainen esimerkki
käännetään GCC 14:llä ja Clang 20:llä sanitoijien kanssa, ja
molempien tulosteen (kuvien tarkistussummat, virheet ja tilastot) on
oltava sama kuin tiedostossa `<nimi>.odotettu`. Satunnaisuus on
toistettavaa: kiinteät siemenet ja oma PCG32-generaattori.

```text
make testaa   # rakenne ja esimerkit
make pdf      # PDF:t
make kuvat    # kuvitus kuvat/*.png esimerkkien PPM-kuvista
```

Kehityskontissa (`.devcontainer/sateenseuranta`) on kääntäjät ja
dokumenttityökalut.

## Lisenssi

CC BY-SA 4.0.
