# Algoritmit

Tiivis suomenkielinen tutoriaali algoritmien suunnittelusta ja
analyysista C23:lla: aika- ja tilavaativuus, lajittelu ja sen
alaraja, binäärihaku, hajota ja hallitse, ahneet algoritmit,
dynaaminen ohjelmointi sekä graafialgoritmit. Menetelmiä sovelletaan
reitinhakuun kartalla, käännösriippuvuuksien järjestämiseen,
diff-työkalun ytimeen ja Huffman-pakkaukseen. Jokainen algoritmi
testataan tunnetuilla tuloksilla, raakaa referenssiä vastaan
satunnaisilla syötteillä ja sanitoijilla. Valmiit dokumentit:
[algoritmit.pdf](https://saperant.github.io/tutoriaalit/materiaalit/algoritmit.pdf)
ja pikaopas
[algoritmit-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/algoritmit-pikaopas.pdf).

Esitiedot: Tietorakenteet (dynaaminen taulukko, keot, graafien
esitystavat) ja diskreetti matematiikka (rekursioyhtälöt,
master-lause, induktio). Jatkotaidot: Edistyneet algoritmit ja
tietorakenteet, Kääntäjätekniikka, Hajautetut järjestelmät,
Säteenseuranta ja fysikaalinen valaistus sekä Suorituskyvyn analyysi
ja optimointi.

## Sisältö

1. Johdanto – suurin osasumma kolmella algoritmilla, oikeellisuus,
   testausmalli
2. Aika- ja tilavaativuus – O, Ω ja Θ, silmukat ja rekursiot, pahin,
   keskimääräinen ja tasoitettu tapaus, kasvun mittaus laskureilla
3. Lajittelun perusteet – lisäyslajittelu ja inversiot,
   lomituslajittelu, vakaus
4. Pikalajittelu ja kekolajittelu – Lomuton jako, pahin tapaus,
   satunnainen jakoalkio, kolmijako, introsort
5. Alaraja ja lineaarinen lajittelu – päätöspuu, vertailijan
   ylivuoto, laskemis- ja kantalukulajittelu, ajoitusmittaus
6. Binäärihaku – ala- ja yläraja, keskikohdan ylivuoto, haku
   vastauksen arvoalueelta
7. Hajota ja hallitse – inversioiden laskeminen, Karatsuban
   kertolasku, rekursion hinta
8. Ahneet algoritmit – aikataulutus ja vaihtoargumentti, kolikot,
   Huffmanin koodaus ja tiedoston pakkaus
9. Dynaaminen ohjelmointi – muistiinpano ja taulukointi,
   reppuongelma ja rekonstruktio
10. Osajonot ja editointietäisyys – LCS, Levenshtein, diff
11. Leveys- ja syvyyshaku – reitti ruutukartalla, syklit,
    topologinen järjestys
12. Painotetut graafit – Dijkstra keolla, negatiiviset painot ja
    Bellman–Ford, Kruskal ja union-find, Prim
13. Lopuksi – menetelmän valinta, nyrkkisäännöt, jatkotaidot ja
    lähteet

## Esimerkit

Esimerkit ovat hakemistossa `esimerkit/`. Testaaja kääntää ne GCC 14-
ja Clang 20 -kääntäjillä (`-std=c23 -Wall -Wextra -Wpedantic -Werror`,
AddressSanitizer ja UndefinedBehaviorSanitizer) ja vertaa tulosteita
`.odotettu`-tiedostoihin. Kaksi `.kaatuu`-esimerkkiä näyttää
sanitoijan pysäyttämän etumerkillisen ylivuodon vertailijassa ja
binäärihaun keskikohdassa. Työmäärä mitataan omilla laskureilla, ja
satunnaisuus tulee omasta generaattorista (`satunnainen.h`) kiinteällä
siemenellä, joten tulosteet ovat samat joka koneella. Lajittelujen
ajoitusmittaus (`esimerkit/mittaus/`) käännetään erikseen
optimoinneilla ja tulostaa vain väljän vertailun tuloksen.

```text
make testaa                 # rakenteen tarkistus, esimerkit, mittaus
make pdf                    # tutoriaali ja pikaopas PDF:ksi
make -C esimerkit           # pelkkä ajoitusmittaus
```

Kehityskontti: `.devcontainer/algoritmit`.

## Lisenssi

CC BY-SA 4.0.
