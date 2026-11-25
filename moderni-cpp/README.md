# Moderni C++

Tiivis suomenkielinen johdatus C++11–C++23-standardien ohjelmointiin.
Valmis dokumentti: [moderni-cpp.pdf](https://saperant.github.io/tutoriaalit/materiaalit/moderni-cpp.pdf).

## Sisältö

Paketti noudattaa kielipakettien yhteistä rakennetta
([`yhteiset/KIELIPAKETTI.md`](../yhteiset/KIELIPAKETTI.md)). Lukujen
lopussa on *Käytännössä*- ja *Itsearviointi*-osiot.

1. Johdanto – historia, käyttökohteet, standardit, työkalut
2. C++ kokeneelle – ajattelutapa, vastaavuudet, hinnat, sudenkuopat
3. C:stä C++:aan – viittaukset, kuormitus, nimiavaruudet, `std::string`,
   `std::vector`, iteraattorit, poikkeusten perusmuoto
4. Luokan perusteet – jäsenfunktiot, näkyvyys, muodostin, hajotin,
   operaattorien kuormitus
5. Kielen perusteet modernisti – alustus, tyypit, ohjausrakenteet,
   syötteen ja tiedostojen lukeminen
6. Funktiot ja lambdat – parametrit ja paluuarvot, sieppaukset
7. Luokat – invariantit, `explicit`, periytyminen, `<=>`, muotoilija,
   vahvat tyypit
8. Resurssienhallinta – RAII ja älykkäät osoittimet
9. Siirtosemantiikka – viiden ja nollan sääntö, `noexcept`
10. Standardikirjaston sanastotyypit – säiliöt, `string_view`, `span`,
    `optional`, `variant`
11. Algoritmit ja ranges
12. Mallit ja konseptit – tyyppien pyyhintä
13. Käännösaikainen laskenta
14. Ohjelman rakenne ja modulit – ODR, nimiavaruudet, rajapinnan
    dokumentointi, pimpl, riippuvuudet
15. Virheenkäsittely – poikkeukset, `std::expected`, takuut
16. Rinnakkaisuus – säikeet, lukot, ehtomuuttujat ja työjono
17. Työkalut ja testaus – CMake, gdb, sanitoijat, clang-tidy, perf,
    yksikkötestit
18. Lopuksi – idiomit ja mallit, nyrkkisäännöt, lähteet

Lisäksi `moderni-cpp-pikaopas.pdf` on kolmen sivun pikaopas kokeneelle
kehittäjälle.

## Rakentaminen

```text
make testaa   # kääntää ja ajaa esimerkit (GCC 14 ja Clang 20)
make pdf      # rakentaa moderni-cpp.pdf:n ja pikaoppaan
```

Riippuvuudet on lueteltu repositorion juuren README-tiedostossa.

Esimerkkien avaaminen kehityskontissa ja ajaminen: ks. [Kehitysympäristöt ja Dev Containers](../kehitysymparistot/), luku 2.
