# Lopuksi {.runko-lahteet}

C++:n suorituskyky ei ole erillinen kieli tai joukko temppuja. Se on
tietoa siitä, mitä kukin rakenne maksaa, ja tapa tarkistaa se
mittaamalla. Tämän tutoriaalin hinnat toistuvat lähes jokaisessa
ohjelmassa:

| Hinta | Mistä tunnistaa | Keino |
|--------------------------|----------------------------------|------------------------------------|
| Kopio | `auto` ilman `&`, parametri arvona | `const&`, näkymä, siirto |
| Muistinvaraus | merkkijono yli 15 merkkiä, solmusäiliö, kasvu | `reserve`, `pmr`, vektori, SSO |
| Epäsuora kutsu | `virtual`, `std::function`, funktio-osoitin | malliparametri, `final`, `std::variant` |
| Poikkeuksen heitto | `throw` normaalissa ohjausvuossa | `std::expected`, `std::optional` |
| Puuttuva `noexcept` | oma siirto tai purkaja | nollan sääntö, `static_assert` |
| Osoittimien seuraaminen | `std::map`, `std::list`, `unique_ptr`-vektori | yhtenäinen data, SoA |
| Näkymätön funktio | runko toisessa käännösyksikössä | otsake, LTO |
| Virta | `<<`, `>>`, `std::stringstream` | `std::to_chars`, `std::format` |

## Nyrkkisäännöt

1. **Mittaa ensin.** Varauslaskuri ja Cachegrind kertovat
   deterministisesti, mitä muutos poisti; kello kertoo, kannattiko se.
2. **Kirjoita yksinkertaisesti ja halvasti oletuksena**: `const&`
   ja näkymät parametreina, arvot paluuarvoina, `std::vector`
   oletussäiliönä, nollan sääntö tyypeissä. Nämä eivät ole optimointeja
   vaan hyvää C++:aa, eikä niistä tarvitse maksaa luettavuudella.
3. **Säästä abstraktiot rajoille**: virtuaalifunktio, `std::function`
   ja `pmr` kuuluvat paikkoihin, joissa joustavuus on tarpeen ja kutsun
   takana on paljon työtä.
4. **Optimoi kuumat polut datasta käsin**: asettelu, säiliö ja
   varausstrategia vaikuttavat enemmän kuin yksittäiset käskyt.
5. **Pidä yksinkertainen versio testinä** jokaiselle optimoidulle.

## Jatkotaidot

- **Rinnakkaisohjelmointi**: säikeet, muistimalli, atomiset operaatiot
  ja väärän jakamisen mittaaminen.
- **GPU-laskenta**: laskentavarjostimet ja rinnakkaiset primitiivit
  näytönohjaimella.
- **Arkkitehtuurin tutkiminen**: suorituskykymallit ja simulaattorit,
  joilla laitteiston valintoja arvioidaan.
- **Edistyneet algoritmit ja tietorakenteet**: välimuistitietoiset
  rakenteet, kuten B-puut.

## Lähteet

Standardi ja dokumentaatio:

- ISO/IEC 14882:2024, *Programming languages — C++* (C++23). Luonnokset
  ovat saatavilla osoitteessa <https://eel.is/c++draft/>.
- cppreference.com: <https://en.cppreference.com/>. Säiliöiden
  takuut, `std::pmr`, `std::expected`, `std::to_chars` ja
  kopion poiston säännöt.
- GCC:n käsikirja: optimointivalitsimet, LTO ja PGO.
  <https://gcc.gnu.org/onlinedocs/gcc/Optimize-Options.html>
- Itanium C++ ABI: virtuaalitaulut ja poikkeusten käsittely.
  <https://itanium-cxx-abi.github.io/cxx-abi/>
- Valgrindin käyttöohje: Cachegrind ja Callgrind.
  <https://valgrind.org/docs/manual/>
- perf-wiki: <https://perf.wiki.kernel.org/>

Kirjat ja artikkelit:

- Bjarne Stroustrup: *The C++ Programming Language*, 4. painos.
  Addison-Wesley 2013. Nollakustannusperiaate.
- Kurt Guntheroth: *Optimized C++*. O'Reilly 2016.
- Fedor G. Pikus: *The Art of Writing Efficient Programs*. Packt 2021.
  Mikrovertailut, muistimalli ja kääntäjän optimoinnit.
- Scott Meyers: *Effective Modern C++*. O'Reilly 2014. Siirrot,
  `noexcept` ja `emplace`.
- Agner Fog: *Optimizing software in C++*. <https://www.agner.org/optimize/>
- ISO C++ -komitean tekninen raportti TR 18015, *Technical Report on
  C++ Performance* (2006). Poikkeusten ja abstraktioiden hinnat.
- Chandler Carruth: *Efficiency with Algorithms, Performance with Data
  Structures*. CppCon 2014 -esitelmä.

Työkalut ja kirjastot:

- Google Benchmark (Apache 2.0): <https://github.com/google/benchmark>
- nanobench (MIT): <https://github.com/martinus/nanobench>
- Compiler Explorer: <https://godbolt.org/>
- Abseil (Apache 2.0), `flat_hash_map`: <https://abseil.io/>
- heaptrack (LGPL): <https://github.com/KDE/heaptrack>
