# C++:n suorituskyky

Tiivis suomenkielinen tutoriaali siitä, mitä C++:n abstraktiot
maksavat ja miten hinta mitataan: virtuaalikutsut ja devirtualisointi,
`std::function` ja tyyppien pyyhintä, poikkeukset ja `noexcept`,
muistinvaraukset (`reserve`, lyhyen merkkijonon optimointi, `std::pmr`,
oma allokaattori), siirrot ja kopioiden poisto, datan asettelu ja
säiliöt, sisällyttäminen, LTO, PGO ja käännösaikainen laskenta sekä
mikrovertailut ja perf. Lopuksi sanojen esiintymien laskenta
nopeutetaan vaihe vaiheelta.
Valmiit dokumentit:
[cpp-suorituskyky.pdf](https://saperant.github.io/tutoriaalit/materiaalit/cpp-suorituskyky.pdf)
ja pikaopas
[cpp-suorituskyky-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/cpp-suorituskyky-pikaopas.pdf).

Esitiedot: Moderni C++ (siirtosemantiikka, RAII, mallit) ja
Suorituskyvyn analyysi ja optimointi (mittaaminen, profilointi,
välimuistit, kääntäjän optimoinnit).

## Sisältö

1. Johdanto – nollakustannusperiaate, huomaamaton kopio, kolme
   mittaria ja esimerkkien kolme tilaa
2. Mittaaminen C++:ssa – kääntäjän poistama mittaus, `pida` ja
   `piilota`, mittauskehys, varauslaskuri, käskyt operaatiota kohden
3. Virtuaalikutsut – virtuaalitaulu, spekulatiivinen devirtualisointi,
   `final`, `std::variant` ja CRTP
4. Funktiot arvoina ja tyyppien pyyhintä – malliparametri,
   funktio-osoitin, `std::function`, `std::any`, pienen olion puskuri
5. Poikkeukset ja `noexcept` – nollakustannusmalli, heittämisen hinta,
   `std::expected`, siirto vektorin kasvaessa
6. Muistinvaraukset – `reserve`, SSO, `std::pmr`, oma allokaattori
7. Siirrot ja kopioiden poisto – paluuarvot, `return std::move`,
   `emplace`, näkymät, elinaika
8. Datan asettelu – täyte, `[[no_unique_address]]`,
   `std::vector<bool>`, AoS ja SoA, säiliöt
9. Käännös – `inline` ja ODR, LTO, PGO, `consteval`, otsakkeiden hinta
10. Mikrovertailut ja perf – sudenkuopat, kalibrointi, luvun
    muotoilun kuusi tapaa, Google Benchmark, laitteistolaskurit
11. Tapaustutkimus – sanojen esiintymät neljässä vaiheessa
12. Lopuksi – hintojen yhteenveto, nyrkkisäännöt ja lähteet

## Esimerkit

Esimerkit ovat hakemistossa `esimerkit/`, ja ne toimivat kolmessa
tilassa. Ilman argumentteja ne ajavat toiminnallisen testin: testaaja
kääntää ne GCC 14- ja Clang 20 -kääntäjillä
(`-std=c++23 -Wall -Wextra -Wpedantic -Werror`, AddressSanitizer ja
UndefinedBehaviorSanitizer) ja vertaa tulosteet `.odotettu`-tiedostoihin.
Tulosteissa on vain deterministisiä lukuja: muistinvaraukset
(korvattu `operator new`), kopiot ja siirrot sekä tulokset.
Argumentilla `--kerran TAPA K` ohjelma toistaa yhtä tapaa
Cachegrindia varten, ja argumentilla `--mittaa` se mittaa ajat.

`esimerkit/Makefile` kääntää ohjelmat optimoituina, laskee
Cachegrindilla käskyt ja välimuistihudit operaatiota kohden
(`tyokalut/kaskyt.py`) ja tutkii konekoodia objdumpilla. Se tarkistaa
niistä tekstin väitteet, esimerkiksi että `final` poistaa kutsun ja että
LTO sisällyttää toisen käännösyksikön funktion. Ajoitukset tulostetaan
mutta niitä ei verrata. Kirjassa näytetyt tulokset ovat hakemistossa
`esimerkit/tulokset/`; niiden ajat on mitattu kuormitetulla koneella ja
ovat suuntaa-antavia.

```text
make testaa                   # rakenne, esimerkit ja tarkistukset
make pdf                      # tutoriaali ja pikaopas PDF:ksi
make -C esimerkit tarkista    # Cachegrind- ja konekoodin tarkistukset
make -C esimerkit mittaa      # ajoitusmittaukset
make -C esimerkit tulokset    # kirjan tulosteet omalla koneella
```

Tarvittavat työkalut: GCC 14, Clang 20, Valgrind, binutils (objdump,
nm) ja Python 3. Kehityskontti: `.devcontainer/cpp-suorituskyky`.

## Lisenssi

CC BY-SA 4.0.
