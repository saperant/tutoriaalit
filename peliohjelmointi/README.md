# Peliohjelmointi

Tiivis suomenkielinen tutoriaali pelien rakentamisesta C++23:lla:
pelisilmukka ja kiinteä aika-askel, syöte, tilakoneet, 2D-grafiikka,
entiteetit ja ECS, törmäykset, fysiikka, resurssit, ääni ja
käyttöliittymä. Lopuksi kootaan pieni peli, *Kipinä*, jolle tehdään
SDL2-etupää.

Valmis dokumentti:
[peliohjelmointi.pdf](https://saperant.github.io/tutoriaalit/materiaalit/peliohjelmointi.pdf),
pikaopas:
[peliohjelmointi-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/peliohjelmointi-pikaopas.pdf).

## Esimerkit

Esimerkit ovat hakemistossa `esimerkit/`. Pelilogiikan esimerkit
käännetään testeissä GCC 14:llä ja Clang 20:llä sanitoijien kanssa, ja
molempien tulosteen on oltava sama. SDL2-etupää ja suorituskykymittaus
ajetaan esimerkkihakemiston Makefilellä:

```text
make -C esimerkit          # SDL2-testi (ilman näyttöä) ja mittaus
make -C esimerkit pelaa    # Kipinä ikkunassa (vaatii näytön)
make testaa                # kaikki testit
make pdf                   # PDF:t
make kuvat                 # Kipinän kuvitus kuvat/kipina.png
```

Kehityskontissa (`.devcontainer/peliohjelmointi`) on kääntäjät ja
SDL2:n kehityspaketti.

## Lisenssi

CC BY-SA 4.0.
