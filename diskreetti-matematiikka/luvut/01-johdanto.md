# Johdanto {.runko-johdanto}

Diskreetti matematiikka tutkii erillisiä, laskettavia rakenteita:
totuusarvoja, kokonaislukuja, joukkoja, jonoja ja verkkoja. Jatkuvan
matematiikan raja-arvoja ja derivaattoja ei tarvita. Juuri nämä
rakenteet ovat ohjelmoinnin raaka-ainetta: ehtolauseke on
propositiologiikkaa, tietokannan kysely joukko-oppia, silmukan
oikeellisuus induktiota, salasanan vahvuus kombinatoriikkaa,
tarkistusnumero modulaariaritmetiikkaa ja reittihaku graafiteoriaa.

Tämä tutoriaali on ohjelmoijan diskreetti matematiikka. Jokainen
käsite kytketään ohjelmointitehtävään, ja jokainen väite tarkistetaan
koodilla: totuustaulu luetellaan, kombinatoriikan kaava verrataan
kaikkien vaihtoehtojen laskemiseen ja lukuteorian lause ajetaan
tuhansilla luvuilla. Koodi ei korvaa todistusta, mutta se paljastaa
väärän väitteen nopeasti ja tekee abstraktista kaavasta kouriintuntuvan.

## Esitiedot ja rajaus

Esitiedoksi riittää taito *Ohjelmoinnin perusteet*: lukija osaa
kirjoittaa ja lukea Python-ohjelmia, joissa on funktioita, silmukoita,
listoja ja sanakirjoja. Lukion pitkää matematiikkaa ei edellytetä,
mutta potenssit, logaritmit ja summamerkintä $\sum$ kannattaa muistaa.

Tutoriaali valmistaa taitoihin *Tietorakenteet*, *Algoritmit* ja
*Todennäköisyys ja tilastot*. Modulaariaritmetiikka on taidon
*Kryptografia* ja Boolen algebra taidon *Digitaalitekniikka* perusta.
Rajauksen ulkopuolelle jäävät

- todennäköisyyslaskenta, myös diskreetti (taito *Todennäköisyys ja
  tilastot*)
- algoritmien suunnittelu ja analyysi kasvunopeuden määritelmää
  pidemmälle (taidot *Tietorakenteet* ja *Algoritmit*)
- automaatit ja formaalit kielet (taito *Kääntäjätekniikka*)
- logiikkapiirien minimointi (taito *Digitaalitekniikka*).

| Luku | Kysymys | Ohjelmoinnissa |
|------|---------|----------------|
| Propositiologiikka | Milloin ehto on tosi? | ehtolauseet, refaktorointi |
| Predikaatit ja SAT | Päteekö väite kaikille? | `all`, `any`, ratkaisijat |
| Joukot ja funktiot | Mitä kokoelma sisältää? | `set`, hajautus, kasvunopeus |
| Relaatiot | Miten alkiot liittyvät toisiinsa? | riippuvuudet, ryhmittely |
| Todistaminen | Miksi algoritmi on oikein? | invariantit, `assert` |
| Rekursio | Miten tehtävä pilkotaan? | rekursio, vaativuus |
| Kombinatoriikka | Montako vaihtoehtoa on? | testitapaukset, salasanat |
| Modulaariaritmetiikka | Mitä jakojäännös kertoo? | tarkisteet, hajautus, salaus |
| Graafit ja puut | Miten asiat ovat yhteydessä? | verkot, hakemistot, aikataulut |

## Työkalut ja esimerkit

Esimerkit ovat Python-ohjelmia hakemistossa `esimerkit/`. Ne
käyttävät vain standardikirjastoa, erityisesti moduuleja `itertools`
(luettelointi), `math` (`comb`, `perm`, `gcd`) ja `functools`
(muistaminen). Esimerkit tarkistetaan ruffilla ja mypyllä tiukassa
tilassa, ja niiden tuloste verrataan talletettuun tulosteeseen.
Ensimmäinen esimerkki tulostaa kaavan totuustaulun käymällä läpi
kaikki muuttujien arvoyhdistelmät. Kaava on tässä implikaatio
”jos $p$, niin $q$”, jonka merkitykseen seuraava luku palaa:

```{.python tiedosto="esimerkit/02-totuustaulu.py" osa="taulu"}
```

```{.tuloste tiedosto="esimerkit/02-totuustaulu.odotettu" rivit="1-5"}
```

Kaaviot piirretään Graphvizilla tekstikuvauksista ja kuvat
Matplotlibilla skriptillä `kuvat/piirra.py` (`make kuvat`).

Kehityskontissa (`.devcontainer/diskreetti-matematiikka`) on Python
ja tarkistustyökalut. Esimerkki ajetaan komennolla
`python3 esimerkit/02-totuustaulu.py`, ja kaikki tarkistetaan
komennolla `make testaa`.

## Merkinnät

Tutoriaali käyttää vakiintuneita merkintöjä ja kertoo niiden
Python-vastineen ensimmäisellä käyttökerralla.

| Merkintä | Lue | Python |
|----------|-----|--------|
| $\neg p$, $p \land q$, $p \lor q$ | ei, ja, tai | `not p`, `p and q`, `p or q` |
| $p \to q$, $p \leftrightarrow q$ | jos–niin, jos ja vain jos | `(not p) or q`, `p == q` |
| $\forall x\, P(x)$, $\exists x\, P(x)$ | kaikilla, jollakin | `all(...)`, `any(...)` |
| $x \in A$, $A \subseteq B$ | kuuluu, osajoukko | `x in A`, `A <= B` |
| $A \cup B$, $A \cap B$, $A \setminus B$ | yhdiste, leikkaus, erotus | `A.union(B)`, `A & B`, `A - B` |
| $\lvert A \rvert$ | alkioiden määrä | `len(A)` |
| $a \equiv b \pmod{m}$ | kongruentti modulo $m$ | `a % m == b % m` |
| $\binom{n}{k}$ | $n$ yli $k$:n | `math.comb(n, k)` |
