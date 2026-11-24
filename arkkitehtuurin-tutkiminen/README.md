# Arkkitehtuurin mallinnus ja suunnittelutilan tutkiminen

Tiivis suomenkielinen tutoriaali arkkitehtuurivaihtoehtojen
vertailuun suorituskyky-, pinta-ala- ja tehomallien avulla: kuormien
karakterisointi, analyyttiset mallit ja jonoteoria, tapahtuma- ja
syklipohjainen simulointi SystemC:llä, intervallimalli ja näytteistys,
laitteisto–ohjelmisto-jako, teho- ja pinta-alamallit sekä
suunnittelutilan läpikäynti ja tulosten raportointi. Valmis dokumentti:
[arkkitehtuurin-tutkiminen.pdf](https://saperant.github.io/tutoriaalit/materiaalit/arkkitehtuurin-tutkiminen.pdf),
pikaopas
[arkkitehtuurin-tutkiminen-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/arkkitehtuurin-tutkiminen-pikaopas.pdf).

## Sisältö

1. Johdanto – mallien tarkkuustasot, työnkulku, työkalut
2. Kuormien karakterisointi – käskyjakauma, muistijäljet,
   uudelleenkäyttöetäisyys, hutikäyrät, työjoukko
3. Analyyttiset suorituskykymallit – Hill ja Marty, hierarkkinen
   roofline, Littlen laki, CPI-pino
4. Jonoteoria – M/M/1, M/D/1, M/M/c, simulointi, suljettu
   järjestelmä ja MVA
5. Tapahtuma- ja syklipohjainen simulointi – LT-, varaus- ja
   syklimalli SystemC:llä, tarkkuus ja nopeus
6. Intervallimalli ja näytteistys – muistitason rinnakkaisuus,
   riippuvuudet, SimPoint
7. Laitteisto–ohjelmisto-jako – kiihdyttimen hyötymalli ja
   virtuaaliprototyyppi
8. Pinta-ala ja teho – dynaaminen teho ja vuoto, DVFS, energia
   operaatiota kohden, välimuistin koko
9. Suunnittelutilan tutkiminen – ruudukko, otanta, latinalainen
   hyperkuutio, Pareto-rintama, herkkyys
10. Validointi, toistettavuus ja raportointi – luottamusvälit,
    kalibrointi, koetiedostot
11. Lopuksi – työnkulku, nyrkkisäännöt, lähteet

## Rakentaminen

```text
make testaa   # ruff, mypy --strict, pytest, ShellCheck ja esimerkit
make pdf      # rakentaa PDF:t (ne eivät ole versionhallinnassa)
make kuvat    # piirtää kuvat uudelleen (kuvat commitoidaan)
```

Esimerkit tarvitsevat GCC 14:n (`g++-14`), SystemC 2.3:n
(`libsystemc-dev`), `pkg-config`in, Python 3.12:n, ruffin, mypyn,
pytestin ja ShellCheckin; kuvat lisäksi matplotlibin. SystemC-ohjelmat
käännetään valitsimella `-std=c++17`, muut C++-ohjelmat C++20:lla ja
sanitoijilla. Python-esimerkit ovat tiedostoja `esimerkit/NN-nimi.py`,
ja niiden yhteinen kirjasto on `esimerkit/arkki/`. C++- ja
SystemC-esimerkit ovat hakemistoja `esimerkit/NN-nimi/`, jotka
`esimerkit/testaa.sh` kääntää ja ajaa. Jokaisen esimerkin tulostetta
verrataan tallennettuun. Kehityskontti on hakemistossa
`.devcontainer/arkkitehtuurin-tutkiminen`.

## Lisenssi

Creative Commons Nimeä–JaaSamoin 4.0 (CC BY-SA 4.0), myös esimerkit.
