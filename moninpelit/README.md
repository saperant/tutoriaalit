# Reaaliaikaiset moninpelit

Tiivis suomenkielinen tutoriaali verkkopelien arkkitehtuurista C++23:lla:
asiakas–palvelin, vertaisverkko ja isäntä, verkon viive ja häviö, oma
luotettavuuskerros UDP:n päälle, tilannevedokset ja delta-pakkaus,
asiakkaan ennustus ja täsmäytys, interpolointi, viiveen kompensointi,
lukitusaskel ja rollback, huijaamisen esto sekä pelipalvelimet ja
otteluiden muodostus. Lukitusaskel toteutetaan lisäksi oikean UDP:n
yli palvelimella ja kahdella asiakkaalla. Aikajanat ja kuvaajat on
piirretty esimerkkien omista simulaatiolokeista.

Esitiedot: *Peliohjelmointi* (determinismi, kiinteä aika-askel) ja
*Tietoverkot*.

Valmis dokumentti:
[moninpelit.pdf](https://saperant.github.io/tutoriaalit/materiaalit/moninpelit.pdf),
pikaopas:
[moninpelit-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/moninpelit-pikaopas.pdf).

## Esimerkit

Esimerkit ovat hakemistossa `esimerkit/`. Useimmat käyttävät
simuloitua verkkoa kiinteällä siemenellä (`esimerkit/yhteinen/`), joten
tulos on joka ajolla sama. Testeissä jokainen käännetään GCC 14:llä ja
Clang 20:llä sanitoijien kanssa, ja molempien tulosteen on oltava sama.
Oikea UDP-peli ajetaan esimerkkihakemiston Makefilellä:

```text
make -C esimerkit          # UDP-palvelin ja kaksi asiakasta
make testaa                # kaikki testit
make pdf                   # PDF:t
make kuvat                 # kuvat esimerkkien lokeista (kuvat/)
```

Kuvat tuotetaan skriptillä `kuvat/piirra.py` (Matplotlib), joka ajaa
esimerkit lokitilassa; PNG-tiedostot ovat versionhallinnassa.

Kehityskontissa (`.devcontainer/moninpelit`) on kääntäjät,
verkkotyökalut ja Matplotlib.

Esimerkkien avaaminen kehityskontissa ja ajaminen: ks. [Kehitysympäristöt ja Dev Containers](../kehitysymparistot/), luku 2.

## Lisenssi

CC BY-SA 4.0.
