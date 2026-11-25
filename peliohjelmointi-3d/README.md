# 3D-peliohjelmointi

Tiivis suomenkielinen tutoriaali kolmiulotteisen pelin rakenteesta
C++23:lla: orientaatiot ja kvaterniot, muunnoshierarkia, törmäysmuodot
ja säteenheitto, laaja vaihe (BVH), ensimmäisen ja kolmannen persoonan
kamerat, hahmon liike kolmioverkossa, näkyvyyskarsinta,
luurankoanimaatio ja glTF-resurssit. Lopuksi osat kootaan pieneksi
kolmannen persoonan peliksi, *Lyhdyksi*.

Valmis dokumentti:
[peliohjelmointi-3d.pdf](https://saperant.github.io/tutoriaalit/materiaalit/peliohjelmointi-3d.pdf),
pikaopas:
[peliohjelmointi-3d-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/peliohjelmointi-3d-pikaopas.pdf).

Esitiedot: taidot *Peliohjelmointi* ja *Renderöinnin perusteet*.

## Esimerkit

Esimerkit ovat hakemistossa `esimerkit/` ja niiden yhteinen koodi
hakemistossa `esimerkit/yhteinen/`. Esimerkit käännetään testeissä GCC
14:llä ja Clang 20:llä sanitoijien kanssa, ja molempien tulosteen on
oltava sama. Ikkunaa tai näytönohjainta ei tarvita: kuvat piirtää
paketin oma pieni ohjelmistorenderöijä.

glTF-resurssit (`esimerkit/resurssit/`) tuotetaan skriptillä
`tee_resurssit.py`, ja esimerkkien Makefile tarkistaa, että
versionhallinnassa olevat tiedostot vastaavat sitä.

## Rakentaminen

```text
make testaa                 # rakenne, esimerkit ja resurssien tarkistus
make pdf                    # PDF:t
make kuvat                  # kuvitus esimerkkiohjelmista (kuvat/)
make -C esimerkit resurssit # glTF-resurssit uudelleen
```

Kuvat tuotetaan ajamalla esimerkit kuvitustilassa skriptillä
`kuvat/piirra.py` (Matplotlib ja NumPy); PNG-tiedostot ovat
versionhallinnassa.

Riippuvuudet: GCC 14 ja Clang 20, JSON-kirjasto `nlohmann-json3-dev`
sekä Python 3 resurssiskriptiä varten. Kehityskontissa
(`.devcontainer/peliohjelmointi-3d`) ne ovat asennettuina.

Esimerkkien avaaminen kehityskontissa ja ajaminen: ks. [Kehitysympäristöt ja Dev Containers](../kehitysymparistot/), luku 2.

## Lisenssi

CC BY-SA 4.0.
