# Moderni C++

Tiivis suomenkielinen johdatus C++11–C++23-standardien ohjelmointiin.
Valmis dokumentti: [moderni-cpp.pdf](moderni-cpp.pdf).

## Sisältö

1. Johdanto – standardit, työkalut, ensimmäinen ohjelma
2. Kielen perusteet modernisti – `auto`, yhtenäinen alustus,
   rakenteiset sidonnat, `enum class`, `nullptr`
3. Funktiot ja lambdat – sieppaukset, sulkeumat, `std::function`,
   `[[nodiscard]]`
4. Luokat – `operator<=>`, `std::formatter`, `= default`/`= delete`,
   `explicit`, `override`/`final`
5. Resurssienhallinta – RAII, `unique_ptr`, `shared_ptr`, `weak_ptr`
6. Siirtosemantiikka – rvalue-viittaukset, viiden ja nollan sääntö,
   `noexcept`
7. Standardikirjaston sanastotyypit – `string_view`, `optional`,
   `variant`, `span`, säiliöt
8. Algoritmit ja ranges – projektiot, näkymät, laiska laskenta
9. Mallit ja konseptit – CTAD, `if constexpr`, variadiset mallit,
   konseptit
10. Käännösaikainen laskenta – `constexpr`, `consteval`, `constinit`
11. Virheenkäsittely – poikkeukset, `noexcept`, `std::expected`
12. Rinnakkaisuus – `jthread`, lukot, atomiset muuttujat,
    pysäyttäminen, `async`
13. Lopuksi – moduulit, korutiinit, C++26, nyrkkisäännöt, lähteet

## Rakentaminen

```text
make testaa   # kääntää ja ajaa esimerkit (GCC 14 ja Clang 20)
make pdf      # rakentaa moderni-cpp.pdf:n
```

Riippuvuudet on lueteltu repositorion juuren README-tiedostossa.
