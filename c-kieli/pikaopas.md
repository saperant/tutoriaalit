---
title: C-kieli
subtitle: Pikaopas kokeneelle kehittäjälle · C17/C23 · GCC 14, Clang 20
---

# Kääntäminen ja työkalut

| Tarkoitus | Komento |
|-----------|---------|
| Kehitysversio | `gcc-14 -std=c23 -Wall -Wextra -Wpedantic -g -fsanitize=address,undefined x.c -lm` |
| Julkaisuversio | `gcc-14 -std=c23 -O2 -DNDEBUG x.c -o x` |
| Lisävaroitukset | `-Wconversion -Wshadow -Wformat=2 -Wnull-dereference` |
| Säikeet | `-fsanitize=thread` (POSIX-säikeillä; ei glibc:n `<threads.h>`) |
| Staattinen analyysi | `gcc -fanalyzer`, `clang-tidy x.c --`, `cppcheck .` |
| Debuggaus | `gdb ./x` → `break f`, `run`, `bt`, `print *p`, `next`, `step` |
| Profilointi | `perf record ./x && perf report` |
| Esikäsittely, objekti | `gcc -E x.c`, `gcc -c x.c` |

# Tyypit ja muotoilu

- Koot vaihtelevat alustoittain: kiinteä koko `<stdint.h>`-tyypeillä
  (`int32_t`, `uint8_t`), koot ja indeksit `size_t`.
- `bool`, `true`, `false`, `nullptr`, `constexpr`, `typeof`, `auto` ovat
  C23:ssa avainsanoja; `{}` nollaa kaiken.

```{.c tiedosto="esimerkit/pikaopas.c" osa="tyypit"}
```

- Bitit etumerkittömillä: aseta `x | m`, nollaa `x & ~m`, vaihda `x ^ m`,
  testaa `(x & m) != 0`, kenttä `(x >> siirto) & maski`.
- Vertailu sitoo tiukemmin kuin `&`, `^` ja `|`: sulkeet aina.

| Määre | Tyyppi | Määre | Tyyppi |
|-------|--------|-------|--------|
| `%d %i` | `int` | `%zu` | `size_t` |
| `%u %x` | `unsigned` | `%td` | `ptrdiff_t` |
| `%ld %lld` | `long`, `long long` | `%f %g %e` | `double` |
| `%c %s` | `char`, merkkijono | `%p` | `void *` |
| `"%" PRId32` | `int32_t` | `%.*s` | pituus + osoitin |

# Osoittimet ja taulukot

- `T *p` osoitin, `&x` osoite, `*p` dereferointi, `p[i] == *(p + i)`.
- Taulukko muuntuu osoittimeksi, kun se välitetään funktiolle: koko
  on välitettävä erikseen (`const T *t, size_t n`).
- `const T *p`: dataa ei muuteta; `T *const p`: osoitinta ei siirretä.

```{.c tiedosto="esimerkit/pikaopas.c" osa="taulukot"}
```

# Merkkijonot turvallisesti

- Merkkijono on `char`-taulukko, joka päättyy `'\0'`. `strlen` ei laske
  päätettä; `sizeof` laskee taulukon koon.
- Vertailu `strcmp(a, b) == 0`, ei `a == b`.
- Muodosta `snprintf`illä, lue `fgets`illä, muunna `strtol`/`strtod`.
  Vältä `gets`, `strcpy`, `strcat`, `sprintf`, `atoi`.

```{.c tiedosto="esimerkit/pikaopas.c" osa="merkkijonot"}
```

# Muisti

- `malloc` (alustamaton), `calloc` (nollattu), `realloc` (apumuuttujaan!),
  `free` (myös `free(nullptr)` sallittu). Koko muodossa `n * sizeof *p`.
- Sovi omistus: kuka vapauttaa. Usein: luoja palauttaa, kutsuja vapauttaa.

```{.c tiedosto="esimerkit/pikaopas.c" osa="muisti"}
```

# Virheenkäsittelyn mallit

Virhekoodi paluuarvona, tulos tulosparametriin:

```{.c tiedosto="esimerkit/pikaopas.c" osa="virhekoodi"}
```

Resurssien vapautus yhdessä paikassa (`goto`-siivous):

```{.c tiedosto="esimerkit/pikaopas.c" osa="siivous"}
```

```{.c tiedosto="esimerkit/pikaopas.c" osa="virheet"}
```

```{.tuloste tiedosto="esimerkit/pikaopas.odotettu"}
```

# Esikääntäjä

- Makron parametrit ja koko lauseke sulkeisiin: `#define SQ(x) ((x) * (x))`.
- Usean lauseen makro: `do { ... } while (0)`.
- Otsikko suojataan: `#ifndef X_H` / `#define X_H` / `#endif`.
- Vakiot mieluummin `constexpr` tai `enum`; funktiot `static inline`.
- X-makro: lista kerran, monta näkymää.

```{.c tiedosto="esimerkit/09-xmakrot.c" osa="xmakro"}
```

# Hinnat

| Halpaa | Kallista tai piilossa |
|--------|------------------------|
| Funktiokutsu, osoitinaritmetiikka | `malloc`/`free` (lukot, pirstaloituminen) |
| Rakenteen välitys osoittimena | Iso rakenne arvona (kopio) |
| Pinomuuttujat, taulukot | `strlen` silmukassa (O(n) joka kierros) |
| `static inline` -funktiot | Välimuistia hajottava muistin käyttö |
| Ehdot, joita kääntäjä ennustaa | Lukot kuumassa silmukassa |

# Sudenkuopat (määrittelemätön käyttäytyminen)

- Taulukon tai varauksen rajojen ylitys; `t + n` saa laskea, ei lukea.
- Vapautetun, tyhjän tai alustamattoman osoittimen käyttö.
- Etumerkillisen kokonaisluvun ylivuoto (tarkista `ckd_add`, `ckd_mul`).
- `-1 < 1u` on epätosi: etumerkillinen muuttuu etumerkittömäksi.
- `fgetc` palauttaa `int`in: `EOF` ei mahdu `char`iin.
- `<ctype.h>`-funktioille `(unsigned char)c`.
- Argumenttien laskentajärjestys on määräämätön: ei sivuvaikutuksia
  samaan muuttujaan saman lausekkeen sisällä.
- Merkkijonoliteraalia ei saa muuttaa: `const char *s = "..."`.
