---
title: C++:n suorituskyky
subtitle: Pikaopas · abstraktiot, poikkeukset, varaukset, siirrot, asettelu ja käännös
---

# Mittaus

```{.cpp tiedosto="esimerkit/mittari.hpp" osa="pida"}
```

- Mittaa `-O2`/`-O3`, ei sanitoijia. 0 ms = kääntäjä poisti työn.
- Varauslaskuri: korvaa `operator new` yhdessä käännösyksikössä.
- Käskyt operaatiota kohden: Cachegrind toistoilla 0 ja K, erotus / K.
- Mikrovertailu: kalibroi toistot (≥ 20 ms), vaihteleva syöte,
  vahvista koko ohjelmalla. Kirjastot: Google Benchmark, nanobench.

```text
valgrind --tool=cachegrind --cache-sim=yes ./a.out
objdump -d -C --no-show-raw-insn a.out    # konekoodi nimineen
perf stat -e cycles,instructions,branch-misses ./a.out
```

# Hinnat

| Rakenne | Hinta | Halvempi |
|---------------------------|-------------------------------|--------------------------|
| `for (auto x : v)` | kopio joka alkiolle | `const auto&` |
| parametri `std::string` | kopio, varaus > 15 merkkiä | `std::string_view` |
| `virtual` sekalaisille | epäsuora hyppy, ohiarvaus | tyypeittäin, `variant` |
| `std::function` | epäsuora kutsu, varaus > 16 t | malliparametri |
| `std::any` | varaus > 8 tavua | `std::variant` |
| `throw` | ~14 000 käskyä | `std::expected` |
| siirto ilman `noexcept` | kopio vektorin kasvaessa | nollan sääntö |
| tyhjä purkaja | ei siirtoa lainkaan | ei purkajaa |
| `std::map`, `std::list` | varaus ja huti per alkio | vektori, `flat_map` |
| `std::ostringstream` | lokaali, virtuaalikutsut | `std::to_chars` |
| `std::endl` silmukassa | tyhjennys joka rivillä | `'\n'` |
| `shared_ptr` arvona | atominen laskuri ×2 | `const T&` |
| `dynamic_cast` | ~160 käskyä | virtuaalifunktio |
| funktio toisessa `.cpp` | ei sisällytystä | otsake, LTO |

# Virtuaalikutsut ja funktiot

```{.cpp tiedosto="esimerkit/03-kuviot.cpp" osa="variant"}
```

- `final` lehtiluokkaan → suora kutsu. GCC devirtualisoi
  spekulatiivisesti: vertailu + sisällytetty polku + epäsuora varakutsu.
- Malliparametri: oma instanssi, sisällytys. `std::function`: 32 t,
  sisäinen puskuri 16 t triviaalisti kopioitavalle.
- `std::move_only_function` (C++23), `std::function_ref` (C++26).

# Poikkeukset

```{.cpp tiedosto="esimerkit/05-jasennys.cpp" osa="expected"}
```

- Heittämätön polku on ilmainen (purkutaulut), heitto kallis.
- `static_assert(std::is_nothrow_move_constructible_v<T>)` vektorin
  alkioille.
- Poikkeus harvinaiseen ja kaukana käsiteltävään, paluuarvo odotettuun.

# Varaukset

- `reserve` kun koko tiedetään; `clear` säilyttää kapasiteetin.
- SSO: libstdc++ 15, libc++ 22 merkkiä. `sizeof(std::string)` = 32.
- `monotonic_buffer_resource` pinopuskurin päälle, ylävirtana
  `null_memory_resource`: ei varauksia keosta, vapautus kerralla.
- `unsynchronized_pool_resource` solmusäiliöille, `make_shared` yksi
  varaus, `extract`/`insert` siirtää solmun.

# Siirrot

| Paluu | Tulos |
|-------------------------|--------------------------|
| `return T{...};` | pakollinen poisto |
| `return x;` (yksi muuttuja) | NRVO |
| `return a;`/`return b;` | implisiittinen siirto |
| `return pari.first;` | kopio |
| `return std::move(x);` | siirto, `-Wpessimizing-move` |

- `emplace_back(argumentit)`, `try_emplace` karttaan.
- Näkymä tai `span` vektorin alkioon mitätöityy kasvussa (myös SSO).

# Asettelu

- Jäsenet tasauksen mukaan suurimmasta pienimpään (`bool, double,
  bool, int, bool` = 32 t, järjestettynä 16 t); `static_assert` koolle.
- `[[no_unique_address]]` tyhjälle jäsenelle, `alignas(64)` laskurille.
- `std::vector<bool>` on bittivektori proxy-alkioin.
- SoA + `std::views::zip`; kuumat ja kylmät kentät erilleen.

# Käännös

- LTO: `-flto=auto` (GCC), `-flto=thin` (Clang), CMake
  `INTERPROCEDURAL_OPTIMIZATION`. Sisällyttää toisen `.cpp`:n funktiot.
- `inline` = saa olla monessa käännösyksikössä (ODR), ei käsky.
- `consteval` taulukoille: vain data jää ohjelmaan.
- PGO: `-fprofile-generate`, edustava ajo, `-fprofile-use`.
- Käännösaika: ennakkoesittelyt, pimpl, PCH, modulit,
  Clangin `-ftime-trace`.

# Muotoilu ja haku

- `std::to_chars`/`from_chars` sarjallistukseen, `std::format`
  ihmisille, ei `std::ostringstream`.
- Hajautustaulun haku näkymällä: hajautin, jossa
  `using is_transparent = void;`, ja `std::equal_to<>`.
- Vain k ensimmäistä: `std::partial_sort`, `std::nth_element`.
