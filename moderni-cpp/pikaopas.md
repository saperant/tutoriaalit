---
title: Moderni C++
subtitle: Pikaopas kokeneelle kehittäjälle · C++23, GCC 14 ja Clang 20 · CC BY-SA 4.0
---

# Kääntäminen ja työkalut

```text
g++-14 -std=c++23 -Wall -Wextra -Wpedantic -g \
       -fsanitize=address,undefined ohjelma.cpp -o ohjelma
cmake -S . -B build -G Ninja && cmake --build build
gdb ./ohjelma          perf record ./ohjelma && perf report
clang-tidy ohjelma.cpp -- -std=c++23   clang-format -i *.cpp
```

# Alustus ja tyypit

```{.cpp tiedosto="esimerkit/pikaopas.cpp" osa="tyyppi"}
```

```{.cpp tiedosto="esimerkit/pikaopas.cpp" osa="alustus"}
```

`{}` estää kaventavat muunnokset; `std::vector<int>(3, 1)` vs.
`std::vector<int>{3, 1}`. Merkkijonoliteraali on `const char*`, `"…"s`
on `std::string` ja `"…"sv` `std::string_view`.

# Luokka ja nollan sääntö

```{.cpp tiedosto="esimerkit/pikaopas.cpp" osa="luokka"}
```

Yksiparametrinen muodostin `explicit`. Kantaluokalla `virtual ~T() =
default` ja kopiointi `= delete`; korvaavat funktiot `override`.

# Omistus

```{.cpp tiedosto="esimerkit/pikaopas.cpp" osa="omistus"}
```

| Parametri | Merkitys |
|-----------|----------|
| `T` | pieni arvo, tai tallennetaan ja siirretään |
| `const T&` | luetaan, ei kopioida |
| `T&` | muutetaan kutsujan oliota |
| `std::unique_ptr<T>` | omistus siirtyy funktiolle |
| `T*` | lainaus, voi olla tyhjä |
| `std::string_view`, `std::span<T>` | luetaan yhtenäistä dataa |

# Kokoelmat ja algoritmit

```{.cpp tiedosto="esimerkit/pikaopas.cpp" osa="kokoelmat"}
```

`vector` oletuksena, `reserve` kun koko tiedetään. Haku `find`,
`contains` tai `at`; `operator[]` lisää puuttuvan avaimen. Näkymät ovat
laiskoja ja viittaavat lähteeseen: `std::ranges::to<std::vector>(näkymä)`
kopioi.

# Lambdat

```{.cpp tiedosto="esimerkit/pikaopas.cpp" osa="lambdat"}
```

Tallennettu tai säikeelle annettu lambda sieppaa arvolla.
Takaisinkutsu malliparametrina (nopea) tai `std::function` (tallennus).

# Virheet

```{.cpp tiedosto="esimerkit/pikaopas.cpp" osa="virheet"}
```

```{.cpp tiedosto="esimerkit/pikaopas.cpp" osa="virheet-kaytto"}
```

`optional`: arvo voi puuttua. `expected`: odotettava virhe syineen.
Poikkeus: harvinainen virhe, käsitellään kaukana. Heitä arvona,
sieppaa `const&`. `noexcept` siirroille ja `swap`ille.

# Mallit ja konseptit

```{.cpp tiedosto="esimerkit/pikaopas.cpp" osa="mallit"}
```

```{.cpp tiedosto="esimerkit/pikaopas.cpp" osa="mallit-kaytto"}
```

# Säikeet

```{.cpp tiedosto="esimerkit/pikaopas.cpp" osa="saikeet"}
```

Ehtomuuttuja aina predikaatin kanssa; `atomic` laskureille ja lipuille;
ThreadSanitizer testeihin.

# Hinnat

| Operaatio | Hinta |
|-----------|-------|
| Poikkeuksen heitto | kallis; onnistunut polku lähes ilmainen |
| Virtuaalikutsu | epäsuora hyppy, ei sisällytystä |
| Malli, lambda algoritmille | sisällytettävissä, ei ajonaikaista hintaa |
| `new`, säiliön kasvu | keosta varaus |
| `shared_ptr`-kopio | atominen laskurin päivitys |
| `std::function` | epäsuora kutsu, voi varata muistia |
| `unordered_map`, `map` | varaus alkiota kohti |

# Sudenkuopat

- Roikkuva `string_view`, `span` tai viittaus väliaikaiseen olioon.
- Iteraattorit ja viittaukset mitätöityvät, kun `vector` kasvaa.
- Viipaloituminen: johdettu olio kopioituu kantaluokan arvoksi.
- Argumenttien laskentajärjestys ei ole määrätty.
- Etumerkillisen ja etumerkittömän vertailu; etumerkillinen ylivuoto on UB.
- `std::move` paluuarvoon estää kopion poiston; `const`-oliota ei siirretä.
- Säikeestä karkaava poikkeus kutsuu `std::terminate`a.
