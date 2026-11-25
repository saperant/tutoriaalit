# Renderöinnin perusteet

Tiivis suomenkielinen tutoriaali kolmiulotteisen kuvan muodostamisesta
alusta asti: kuvapuskuri ja sRGB, viivat ja kolmiot, muunnokset ja
perspektiivi, leikkaus, syvyyspuskuri, valaistus, tekstuurit,
reunanpehmennys ja koko grafiikkaputki. Kaikki toteutetaan pienenä
C++23-ohjelmistorasteroijana ilman ulkoisia kirjastoja.

Valmis dokumentti:
[renderoinnin-perusteet.pdf](https://saperant.github.io/tutoriaalit/materiaalit/renderoinnin-perusteet.pdf),
pikaopas:
[renderoinnin-perusteet-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/renderoinnin-perusteet-pikaopas.pdf).

## Esimerkit

Esimerkit ovat hakemistossa `esimerkit/` ja yhteinen kirjasto
hakemistossa `esimerkit/yhteinen/`. Testeissä jokainen esimerkki
käännetään GCC 14:llä ja Clang 20:llä sanitoijien kanssa, ja
molempien tulosteen (kuvien tarkistussummat ja tilastot) on oltava
sama kuin tiedostossa `<nimi>.odotettu`.

```text
make testaa   # rakenne ja esimerkit
make pdf      # PDF:t
make kuvat    # kuvitus: esimerkkien PPM-kuvat ja piirrokset (Matplotlib)
```

Esimerkkien avaaminen kehityskontissa ja ajaminen: ks.
[Kehitysympäristöt ja Dev Containers](../kehitysymparistot/), luku 2.

Kehityskontissa (`.devcontainer/renderoinnin-perusteet`) on kääntäjät
ja dokumenttityökalut.

## Lisenssi

CC BY-SA 4.0.
