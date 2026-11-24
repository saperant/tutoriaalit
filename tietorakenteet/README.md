# Tietorakenteet

Tiivis suomenkielinen tutoriaali ohjelmoinnin perustietorakenteista
C23:lla: rajapinnat ja omistajuus, dynaaminen taulukko, linkitetyt
listat, pinot, jonot ja rengaspuskurit, hajautustaulut, binäärihakupuut,
keot, graafien esitystavat sekä välimuistin vaikutus datan asetteluun.
Jokainen rakenne testataan satunnaistetulla vertailutestillä,
invarianttifunktiolla ja sanitoijilla. Valmiit dokumentit:
[tietorakenteet.pdf](https://saperant.github.io/tutoriaalit/materiaalit/tietorakenteet.pdf)
ja pikaopas
[tietorakenteet-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/tietorakenteet-pikaopas.pdf).

Esitiedot: C-kieli (osoittimet, muistinhallinta) ja diskreetti
matematiikka (graafit, puut, rekursio). Jatkotaito: Algoritmit.

## Sisältö

1. Johdanto – miksi rakenteella on väliä, abstrakti tietotyyppi ja
   toteutus, testausmalli
2. Abstraktit tietotyypit ja rajapinnat – läpinäkymätön osoitin,
   virhekoodit, omistajuus, invariantti
3. Dynaaminen taulukko – kasvatusstrategiat, tasoitettu aika
   kopioina, roikkuvat osoittimet
4. Linkitetyt listat – yksöis- ja kaksoislinkitetty, tunnussolmu,
   LRU-välimuisti, tunkeileva lista
5. Pinot, jonot ja rengaspuskurit – täysi/tyhjä-erotus, kahden
   indeksin malli
6. Hajautustaulut – FNV-1a, ketjutus, kuormituskerroin ja
   uudelleenhajautus
7. Avoin osoitteistus – lineaarinen kokeilu, hautakivet,
   vertailutesti, kuormituksen mittaus
8. Binäärihakupuut – lisäys, haku, poisto, läpikäynnit, epätasapaino
9. Keot ja prioriteettijonot – binäärikeko taulukossa, kekoutus
10. Graafien esitystavat – matriisi, vierekkäisyyslistat, CSR
11. Välimuisti ja datan asettelu – rivinvaihtojen laskenta, ajoitus,
    AoS ja SoA
12. Lopuksi – valintataulukko, nyrkkisäännöt, jatkotaidot ja lähteet

## Esimerkit

Esimerkit ovat hakemistossa `esimerkit/`. Testaaja kääntää ne GCC 14-
ja Clang 20 -kääntäjillä (`-std=c23 -Wall -Wextra -Wpedantic -Werror`,
AddressSanitizer ja UndefinedBehaviorSanitizer) ja vertaa tulosteita
`.odotettu`-tiedostoihin. Satunnaisuus tulee omasta generaattorista
(`satunnainen.h`) kiinteällä siemenellä, joten tulosteet ovat samat
joka koneella. Välimuistin ajoitusmittaus (`esimerkit/mittaus/`)
käännetään erikseen optimoinneilla ja tulostaa vain väljän vertailun
tuloksen.

```text
make testaa                 # rakenteen tarkistus, esimerkit, mittaus
make pdf                    # tutoriaali ja pikaopas PDF:ksi
make -C esimerkit           # pelkkä ajoitusmittaus
```

Kehityskontti: `.devcontainer/tietorakenteet`.

## Lisenssi

CC BY-SA 4.0.
