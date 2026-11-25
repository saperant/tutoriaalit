# Diskreetti matematiikka

Tiivis suomenkielinen tutoriaali ohjelmoijan diskreetistä
matematiikasta: logiikka, joukot, relaatiot, todistaminen ja
invariantit, rekursioyhtälöt, kombinatoriikka, modulaariaritmetiikka
sekä graafit ja puut. Jokainen käsite kytketään ohjelmointitehtävään,
ja jokainen väite tarkistetaan Python-koodilla. Valmiit dokumentit:
[diskreetti-matematiikka.pdf](https://saperant.github.io/tutoriaalit/materiaalit/diskreetti-matematiikka.pdf)
ja pikaopas
[diskreetti-matematiikka-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/diskreetti-matematiikka-pikaopas.pdf).

## Sisältö

1. Johdanto – mitä diskreetti matematiikka on ja merkinnät
2. Propositiologiikka – totuustaulut, ekvivalenssit, normaalimuodot,
   ehtojen sieventäminen
3. Predikaatit ja SAT – kvanttorit ohjelmassa, DPLL-ratkaisija,
   ongelman koodaaminen SAT:ksi
4. Joukot ja funktiot – operaatiot, potenssijoukko, injektio ja
   bijektio, kardinaliteetti ja hajautus, kasvunopeus ja O-merkintä
5. Relaatiot – ominaisuudet, ekvivalenssiluokat, transitiivinen
   sulkeuma, Hassen kaavio, topologinen järjestys
6. Todistaminen ja invariantit – induktio, vahva induktio,
   silmukkainvariantit
7. Rekursio ja rekursioyhtälöt – Fibonacci, hajota ja hallitse,
   master-lause
8. Kombinatoriikka – permutaatiot, kombinaatiot, binomikertoimet,
   lokeroperiaate, inkluusio–ekskluusio
9. Modulaariaritmetiikka – Eukleides, käänteisalkiot, nopea potenssi,
   Fermat'n ja Eulerin lauseet, tarkisteet, kiinalainen jäännöslause
10. Graafit – esitystavat, komponentit, Euler ja Hamilton, väritys
11. Puut – ominaisuudet, Cayleyn kaava, juurelliset puut
12. Lopuksi – nyrkkisäännöt, jatkotaidot ja lähteet

## Esimerkit

Esimerkit ovat hakemistossa `esimerkit/` ja käyttävät vain Pythonin
standardikirjastoa. Ne tarkistetaan ruffilla ja mypyllä tiukassa
tilassa, ja niiden tulostetta verrataan `.odotettu`-tiedostoihin.
Kuvat piirtää `kuvat/piirra.py` (Matplotlib); kaaviot ovat lukujen
Graphviz-lohkoja.

```text
make testaa     # rakenteen tarkistus ja kaikki esimerkit
make pdf        # tutoriaali ja pikaopas PDF:ksi
make kuvat      # piirtää kuvat uudelleen (Matplotlib)
python3 esimerkit/03-dpll.py
```

Kehityskontti: `.devcontainer/diskreetti-matematiikka`.
Esimerkkien avaaminen kehityskontissa ja ajaminen: ks.
[Kehitysympäristöt ja Dev Containers](../kehitysymparistot/), luku 2.

## Lisenssi

CC BY-SA 4.0.
