---
title: Suorituskyvyn analyysi ja optimointi
subtitle: Pikaopas · mittaus, profilointi, välimuistit, haarat, vektorointi ja kääntäjä
---

# Mittaus

```{.c tiedosto="esimerkit/mittari.h" osa="kellot"}
```

```{.c tiedosto="esimerkit/mittari.h" osa="kayta"}
```

- Toista, raportoi **mediaani, pienin ja MAD**; keskiarvo on herkkä
  häiriöille, jotka vain pidentävät aikaa.
- Lämmittely ennen toistoja tai tietoisesti kylmä mittaus.
- 0 ms = kääntäjä poisti työn. Syöte ohjelman ulkopuolelta.
- Mittaa `-O2`, ei sanitoijia. Sido ytimeen: `taskset -c 2`.
- Amdahl: $S = 1 / ((1 - p) + p/s)$, raja $1/(1 - p)$.
- Roofline: $\min(P, B \cdot I)$, $I$ = FLOP/tavu, harjanne $P/B$.

# Profilointi

```text
gcc -O2 -g -pg ...; ./a.out; gprof -b -p a.out gmon.out
valgrind --tool=callgrind ./a.out
callgrind_annotate --inclusive=yes callgrind.out.*
valgrind --tool=cachegrind --cache-sim=yes ./a.out
valgrind --tool=cachegrind --branch-sim=yes ./a.out
perf stat -e cycles,instructions,cache-misses,branch-misses ./a.out
perf record -g ./a.out; perf report; perf annotate f
```

| Työkalu | Näkee | Ei näe |
|----------|--------------------|------------------|
| gprof | Omat funktiot, tarkat kutsumäärät | Kirjastojen aika |
| Callgrind | Kaikki käskyt, kutsupuu, deterministinen | Aikaa, muistin odotusta |
| Cachegrind | Simuloidut hudit ja ennusteet | Todellista laitteistoa |
| perf | Todellinen aika ja laskurit | Toimii harvoin konteissa |

- IPC $\approx$ 3: laskentarajoitteinen. IPC $<$ 0,5: odottaa muistia.
- Kumulatiivinen = kutsupolku; oma = kuka työn tekee.

# Muisti

| Taso | Viive | Huom. |
|------|-------|-------|
| L1 | 1 ns | 32–48 KiB |
| L2 | 4–10 ns | 1–2 MiB |
| L3 | 10–50 ns | jaettu |
| DRAM | 80–200 ns | esihaku auttaa vain peräkkäin |

- Rivi 64 B, sivu 4 KiB (suuri 2 MiB). Sisin silmukka peräkkäin.
- AoS → SoA, kun silmukka käyttää yhtä kenttää.
- Kentät suurimmasta pienimpään; `pahole` näyttää aukot.
- `alignas(64)` säikeiden laskureille (väärä jakaminen).
- Lohkominen: käytä palaa kaikille riveille ennen seuraavaa.

```{.makefile tiedosto="esimerkit/Makefile" osa="cachegrind"}
```

# Haarat

```{.c tiedosto="esimerkit/07-haarat.c" osa="haaraton"}
```

- Väärä ennuste 15–20 jaksoa. Satunnaisesta datasta riippuva haara
  kuumassa silmukassa: lajittele, ositus tai maski.
- Tarkista ensin konekoodista: kääntäjä tekee usein `cmov`:n.
- Ennustettava haara on halvempi kuin haaraton laskenta.

# Vektorointi

- GCC `-O3 -fopt-info-vec-optimized` / `-missed`; Clang
  `-Rpass=loop-vectorize`.
- Esteet: aliasing (`restrict`), kierrosten riippuvuus, liukulukujen
  järjestys (omat osasummat), kutsut, hajanaiset osoitteet.
- Raportin ”vectorized” ei takaa rinnakkaisia operaatioita: katso
  konekoodi (`addss` vs. `addps`).
- Intrinsicsit: `<immintrin.h>`, `_mm_loadu_ps`, `_mm256_add_ps`;
  `[[gnu::target("avx2")]]` ja `__builtin_cpu_supports("avx2")`.

# Kääntäjä

| Lippu | Vaikutus |
|------------------------|--------------------|
| `-O2` | tuotannon oletus |
| `-O3` | vektorointi, avaus; koodi kasvaa |
| `-march=native` | koneen kaikki käskyt; ei siirrettävä |
| `-march=x86-64-v3` | AVX2-taso jaettavaan binääriin |
| `-flto` | sisällyttäminen yli käännösyksiköiden |
| `-fprofile-generate` / `-use` | PGO kahdessa käännöksessä |
| `-ffast-math` | liukulukusemantiikka muuttuu |

# Muisti ja I/O

- Areena: suuret lohkot, osoittimen siirto, vapautus kerralla.
- Ensimmäinen kosketus sivuun = sivuvirhe; varaa puskurit kerran.
- Puskuroi: `stdio`, `fread`/`fwrite` suurina paloina; ei `fflush`
  rivin välein.
