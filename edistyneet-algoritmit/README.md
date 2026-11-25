# Edistyneet algoritmit ja tietorakenteet

Tiivis suomenkielinen tutoriaali tasapainotetuista ja erikoistuneista
tietorakenteista, merkkijonoalgoritmeista, verkkovirtauksista,
satunnaistetuista algoritmeista ja laskennallisesta vaativuudesta
C++23:lla. Jokainen rakenne testataan satunnaistetulla
vertailutestillä yksinkertaista mallia vastaan, ja sen invariantit
tarkistetaan jokaisen operaation jälkeen. Valmiit dokumentit:
[edistyneet-algoritmit.pdf](https://saperant.github.io/tutoriaalit/materiaalit/edistyneet-algoritmit.pdf)
ja pikaopas
[edistyneet-algoritmit-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/edistyneet-algoritmit-pikaopas.pdf).

Esitiedot: Algoritmit (vaativuus, lajittelu, dynaaminen ohjelmointi,
graafialgoritmit). Hyödyllisiä: Tietorakenteet, Moderni C++,
Diskreetti matematiikka ja Todennäköisyys.

## Sisältö

1. Johdanto – aiheet, esitiedot, kieli ja testausmalli
2. Satunnaistettu vertailutestaus – malli, toistettava satunnaisuus,
   invariantit, virheen pienentäminen
3. Tasapainotetut hakupuut – 2-3-puut, vasemmalle kallistuva
   punamusta puu, invarianttien tarkistus, treap ja järjestystilastot
4. B-puut – halkaisu matkalla alas, lohkoluvut ja vertailut,
   B+-puut ja välimuistitietoisuus
5. Tasoitettu analyysi – kokonais-, kirjanpito- ja
   potentiaalimenetelmä, dynaaminen taulukko, kutistus ja hystereesi,
   binäärilaskuri
6. Union-find – polun tiivistys ja tasot, käänteinen Ackermannin
   funktio, perkolaatio
7. Fenwick-puu ja segmenttipuu – etuliitesummat, käänteishaku ja
   persentiilit, liitännäiset välikyselyt, laiska päivitys
8. Merkkijonohaku – KMP, Z-algoritmi, Rabin–Karp ja hajautuksen
   törmäykset
9. Trie ja suffiksitaulukko – etuliitekyselyt, etuliitteiden tuplaus,
   Kasain LCP
10. Verkkovirtaukset – Edmonds–Karp, Dinic, minimileikkaus,
    kaksijakoinen paritus, Königin lause
11. Satunnaistetut algoritmit – Las Vegas ja Monte Carlo, skip-lista,
    pikavalinta, Freivaldsin tarkistus
12. Todennäköisyyspohjaiset tiivistelmät – Bloom-suodatin, Count-Min,
    säiliöotanta
13. NP-täydellisyys ja reduktiot – P ja NP, 3-SAT riippumattomaksi
    joukoksi, reduktion testaus
14. Approksimointi ja tarkka haku – solmu- ja joukkopeite,
    kauppamatkustaja (Held–Karp, heuristiikat, 2-opt), haarautuminen ja
    karsinta
15. Lopuksi – rakenteen valinta, nyrkkisäännöt, jatkotaidot ja lähteet

## Esimerkit

Esimerkit ovat hakemistossa `esimerkit/`. Testaaja kääntää ne GCC 14-
ja Clang 20 -kääntäjillä (`-std=c++23 -Wall -Wextra -Wpedantic
-Werror`, AddressSanitizer ja UndefinedBehaviorSanitizer) ja vertaa
tulosteita `.odotettu`-tiedostoihin. `.kaatuu`-esimerkki näyttää
invarianttien tarkistuksen pysäyttävän virheellisen punamustan puun.
Satunnaisuus tulee omasta generaattorista (`testaus.hpp`) kiinteällä
siemenellä, ja työmäärä mitataan laskureilla, joten tulosteet ovat
samat joka koneella.

Virtausverkon, reduktion ja Fenwick-puun kaaviot tuotetaan esimerkkien
tulosteista (`kaaviot/tee.py`), ja `make testaa` tarkistaa, että
tallennetut kaaviot vastaavat tulosteita.

```text
make testaa                 # rakenteen tarkistus ja esimerkit
make pdf                    # tutoriaali ja pikaopas PDF:ksi
python3 kaaviot/tee.py      # kaaviot uudelleen esimerkkien tulosteista
```

Kehityskontti: `.devcontainer/edistyneet-algoritmit`.
Esimerkkien avaaminen kehityskontissa ja ajaminen: ks.
[Kehitysympäristöt ja Dev Containers](../kehitysymparistot/), luku 2.

## Lisenssi

CC BY-SA 4.0.
