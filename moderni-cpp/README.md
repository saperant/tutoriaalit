# Moderni C++

Tiivis suomenkielinen johdatus C++11–C++23-standardien ohjelmointiin.
Valmis dokumentti: [moderni-cpp.pdf](https://saperant.github.io/tutoriaalit/materiaalit/moderni-cpp.pdf).

## Sisältö

Paketti noudattaa kielipakettien yhteistä rakennetta
([`yhteiset/KIELIPAKETTI.md`](../yhteiset/KIELIPAKETTI.md)). Lukujen
lopussa on *Käytännössä*- ja *Itsearviointi*-osiot.

1. Johdanto – historia, käyttökohteet, standardit, työkalut
2. C++ kokeneelle – ajattelutapa, vastaavuudet, hinnat, sudenkuopat
3. Kielen perusteet modernisti – alustus, tyypit, ohjausrakenteet,
   syötteen lukeminen
4. Funktiot ja lambdat
5. Luokat – `<=>`, muotoilija, `explicit`, periytyminen, vahvat tyypit
6. Resurssienhallinta – RAII ja älykkäät osoittimet
7. Siirtosemantiikka – viiden ja nollan sääntö, `noexcept`
8. Standardikirjaston sanastotyypit – `string_view`, `optional`,
   `variant`, `span`, säiliöt
9. Algoritmit ja ranges
10. Mallit ja konseptit – tyyppien pyyhintä
11. Käännösaikainen laskenta
12. Ohjelman rakenne ja modulit – ODR, nimiavaruudet, pimpl, riippuvuudet
13. Virheenkäsittely – poikkeukset, `std::expected`, takuut
14. Rinnakkaisuus – säikeet, lukot, työjono
15. Työkalut ja testaus – CMake, gdb, sanitoijat, clang-tidy, perf,
    yksikkötestit
16. Lopuksi – idiomit ja mallit, nyrkkisäännöt, lähteet

Lisäksi `moderni-cpp-pikaopas.pdf` on kolmen sivun pikaopas kokeneelle
kehittäjälle.

## Rakentaminen

```text
make testaa   # kääntää ja ajaa esimerkit (GCC 14 ja Clang 20)
make pdf      # rakentaa moderni-cpp.pdf:n ja pikaoppaan
```

Riippuvuudet on lueteltu repositorion juuren README-tiedostossa.
