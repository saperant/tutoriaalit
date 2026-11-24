# Johdanto {.runko-johdanto}

C++:n lupaus on *nollakustannusperiaate* (engl. zero-overhead
principle): mitä et käytä, siitä et maksa, ja minkä käytät, sitä et
voisi käsin kirjoittaa paremmin. Lupaus pitää yllättävän usein:
`std::vector`, `std::sort` lambdan kanssa ja `std::unique_ptr` kääntyvät
samaksi konekoodiksi kuin huolella kirjoitettu C. Yhtä usein se
rikkoutuu huomaamatta. Yksi puuttuva `&` kopioi tuhat merkkijonoa,
puuttuva `noexcept` kopioi koko vektorin sen kasvaessa, ja
`std::function` estää kääntäjää näkemästä kutsun läpi.

Tämä tutoriaali käy läpi C++:n omat hinnat: mitä abstraktiot,
poikkeukset, muistinvaraukset, kopiot ja siirrot sekä datan asettelu
maksavat, ja miten niiden hinta mitataan. Yleiset suorituskyvyn
menetelmät, kuten mittaamisen tilastot, profilointi, välimuistit,
haarautumisen ennustus, vektorointi ja kääntäjän optimointitasot,
opetetaan taidossa *Suorituskyvyn analyysi ja optimointi*, ja tässä
niihin viitataan. Kielen perusteet, kuten siirtosemantiikka, RAII,
mallit ja rangesit, ovat taidossa *Moderni C++*.

## Huomaamaton kopio

Seuraava funktio laskee nimien yhteispituuden. Se näyttää harmittomalta:

```{.cpp tiedosto="esimerkit/01-kopiot.cpp" osa="hidas"}
```

Parametri on arvo, joten kutsu kopioi koko vektorin. Silmukkamuuttuja on
arvo, joten jokainen nimi kopioidaan vielä uudelleen. Pitkä merkkijono
varaa kopiolle muistia keosta. Korjaus on kaksi merkkiä `&` ja yksi
`const`:

```{.cpp tiedosto="esimerkit/01-kopiot.cpp" osa="nopea"}
```

Tämän tutoriaalin esimerkit mittaavat hinnan ensisijaisesti
deterministisillä laskureilla. Tässä laskuri on korvattu
`operator new`, joka laskee muistinvaraukset (luku 2):

```{.cpp tiedosto="esimerkit/01-kopiot.cpp" osa="testi"}
```

```{.tuloste tiedosto="esimerkit/01-kopiot.odotettu"}
```

Tuhannen nimen vektori: tuhat varausta parametrin kopiolle, tuhat
silmukkamuuttujalle ja yksi vektorin puskurille. Ajoitus samalla
koodilla optimoituna sadalletuhannelle nimelle:

```{.tuloste tiedosto="esimerkit/tulokset/01-kopiot.txt"}
```

Ajat on mitattu kirjoittajan koneella, joka oli mittausten aikana
muun työn kuormittama. Kaikki tämän tutoriaalin ajat ovat siksi
suuntaa-antavia: suhteiden suunta ja suuruusluokka pätevät, tarkat
luvut eivät.

## Kolme mittaria

Ajoitus vaihtelee koneen, kuorman ja kääntäjän mukaan, joten
tutoriaali käyttää kolmea mittaria, joista kaksi on deterministisiä:

| Mittari | Työkalu | Mitä kertoo | Toistettava |
|------------------|---------------------------|----------------------------|-----------------|
| Muistinvaraukset | korvattu `operator new` | kopiot, kasvu, solmusäiliöt | aina |
| Käskyt ja hudit | Valgrind Cachegrind | tehdyn työn määrä | samalla käännöksellä |
| Aika | `steady_clock` | kokonaisvaikutus | ei |

Muistinvarausten määrä riippuu vain koodista ja standardikirjaston
toteutuksesta: GCC ja Clang käyttävät tässä samaa libstdc++:aa, joten
luvut ovat samat. Cachegrind laskee suoritetut käskyt ja simuloi
välimuistin, joten sen tulokset eivät riipu koneen kuormasta. Aika on
lopullinen totuus, mutta vain samalla koneella toistettuna.

## Esimerkit

Jokainen esimerkki toimii kolmessa tilassa:

- **Ilman argumentteja** se ajaa toiminnallisen testin: optimoitu ja
  perusversio antavat saman tuloksen, ja laskurit tulostetaan.
  Testaaja kääntää esimerkit GCC 14:llä ja Clang 20:llä
  (`-std=c++23 -Wall -Wextra -Wpedantic -Werror`, AddressSanitizer
  ja UndefinedBehaviorSanitizer) ja vertaa tulosteen tiedostoon
  `.odotettu`.
- **Argumentilla `--kerran TAPA K`** se toistaa yhtä tapaa K kertaa
  Cachegrindia varten.
- **Argumentilla `--mittaa`** se mittaa ajat suuremmalla syötteellä.

Esimerkkihakemiston Makefile kääntää ohjelmat optimoituina
(`g++-14 -O2`) ja ajaa deterministiset tarkistukset, jotka
varmistavat tekstin väitteet: esimerkiksi että virtuaalikutsu tekee
enemmän käskyjä kuin devirtualisoitu kutsu tai että LTO poistaa
kutsun. Ajoitukset tulostetaan, mutta niitä ei verrata mihinkään.

```text
make testaa                   # rakenne, esimerkit ja tarkistukset
make -C esimerkit tarkista    # Cachegrind- ja konekoodin tarkistukset
make -C esimerkit mittaa      # ajoitusmittaukset
make -C esimerkit tulokset    # kirjan tulosteet omalla koneella
```

## Tutoriaalin rakenne

Johdannon jälkeen luvut etenevät näin:

2. **Mittaaminen C++:ssa**: kääntäjän poistama mittaus, sen estäminen,
   varauslaskuri ja Cachegrind.
3. **Virtuaalikutsut**: virtuaalitaulu, devirtualisointi, `final`,
   `std::variant` ja CRTP.
4. **Funktiot arvoina ja tyyppien pyyhintä**: malliparametri,
   funktio-osoitin, `std::function`, `std::any` ja pienen olion puskuri.
5. **Poikkeukset ja `noexcept`**: nollakustannusmalli, heittämisen
   hinta, `std::expected` ja siirto vektorin kasvaessa.
6. **Muistinvaraukset**: `reserve`, lyhyen merkkijonon optimointi,
   `std::pmr` ja oma allokaattori.
7. **Siirrot ja kopioiden poisto**: paluuarvot, `emplace`, näkymät ja
   elinaikojen sudenkuopat.
8. **Datan asettelu**: täyte ja tasaus, `std::vector<bool>`, AoS ja
   SoA sekä solmupohjaiset ja litteät säiliöt.
9. **Käännös**: `inline` ja ODR, LTO ja PGO, käännösaikainen laskenta
   ja otsakkeiden hinta.
10. **Mikrovertailut ja perf**: mittauksen sudenkuopat, toistojen
    kalibrointi, Google Benchmark ja laitteistolaskurit.
11. **Tapaustutkimus**: sanojen esiintymien laskenta neljässä vaiheessa.
12. **Lopuksi**: hintojen yhteenveto, nyrkkisäännöt, jatkotaidot ja
    lähteet.

Esitiedot ovat *Moderni C++* ja *Suorituskyvyn analyysi ja
optimointi*. Rinnakkaisuuden hinnat (lukot, atomiset operaatiot,
väärä jakaminen) käsitellään taidossa *Rinnakkaisohjelmointi*.
