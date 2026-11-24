---
title: Miten tietokone laskee
subtitle: Pikaopas · kokonaisluvut, liukuluvut, ML-muodot ja muisti · C23 ja Python/NumPy
---

# Kokonaisluvut

| Tyyppi | Arvoalue | Huom. |
|--------|----------|-------|
| `int8_t` | −128 … 127 | kahden komplementti |
| `uint8_t` | 0 … 255 | pikselit, tavut |
| `int32_t` | ±2,1 · 10^9^ | ei rahalle |
| `int64_t` | ±9,2 · 10^18^ | rahat sentteinä |
| `size_t` | 0 … 2^64^−1 | koot, indeksit |

- Etumerkillinen ylivuoto on määrittelemätön (UBSan:
  `signed integer overflow`). Etumerkitön kiertää modulo $2^n$.
- `int` + `unsigned` → etumerkitön: `-1 < sizeof(x)` on epätosi.
- Siirto $\ge$ leveys on määrittelemätön. Negatiivinen `>>` pyöristää
  alaspäin (`-7 >> 1 == -4`, `-7 / 2 == -3`).
- `INT_MIN / -1` ja `x / 0` kaatavat ohjelman.

```{.c tiedosto="esimerkit/pikaopas.c" osa="tarkistettu"}
```

```{.c tiedosto="esimerkit/pikaopas.c" osa="bitit"}
```

| Bittioperaatio | Lauseke |
|----------------|---------|
| aseta / poista | `x \| m`, `x & ~m` |
| vaihda / testaa | `x ^ m`, `(x & m) != 0` |
| kahden potenssi | `x && !(x & (x - 1))` |
| tasaa ylös (2^k^) | `(x + a - 1) & ~(a - 1)` |
| `<stdbit.h>` | `stdc_count_ones`, `stdc_bit_ceil` |

# Jakolasku

| Kieli | `-7 / 2` | `-7 % 2` |
|-------|----------|----------|
| C, Java, Rust, Go | −3 | −1 |
| Python `//`, `%` | −4 | 1 |

```{.c tiedosto="esimerkit/pikaopas.c" osa="jako"}
```

Kattojako: `a / b + (a % b != 0)`.

# Liukuluvut (IEEE 754)

| Muoto | e/m-bitit | Suurin | Epsilon |
|-------|-----------|--------|---------|
| binary64 | 11/52 | 1,8 · 10^308^ | 2,2 · 10^−16^ |
| binary32 | 8/23 | 3,4 · 10^38^ | 1,2 · 10^−7^ |
| binary16 | 5/10 | 65 504 | 9,8 · 10^−4^ |
| bfloat16 | 8/7 | 3,4 · 10^38^ | 7,8 · 10^−3^ |
| FP8 E5M2 | 5/2 | 57 344 | 0,25 |
| FP8 E4M3 | 4/3 | 448 | 0,125 |

- Arvo $= (-1)^s \cdot 1.m \cdot 2^{e - \text{bias}}$, bias
  $= 2^{k-1} - 1$.
- binary64 esittää kokonaisluvut tarkasti $2^{53}$:een, binary32
  $2^{24}$:ään.
- NaN ≠ NaN, kaikki NaN-vertailut epätosia. `-0.0 == 0.0`.
- Oletuspyöristys: lähimpään, tasapeli parilliseen (`rint`, Pythonin
  `round`). `round` C:ssä: poispäin nollasta.

```{.c tiedosto="esimerkit/pikaopas.c" osa="liukuluku"}
```

| Ongelma | Ratkaisu |
|---------|----------|
| pitkä summa | Kahan, parittain, `math.fsum` |
| varianssi | Welford, ei $\overline{x^2} - \overline{x}^2$ |
| $\log(1+x)$, $e^x - 1$ | `log1p`, `expm1` |
| tulon virhe | `fma(a, b, -a*b)` |
| raha | sentit `int64_t`, `Decimal` |
| aikaleima | `int64_t` ns/µs |
| toistettavuus | `-ffp-contract=off`, kiinteä järjestys |
| `-ffast-math` | rikkoo Kahanin ja `isnan`-tarkistuksen |

# Python ja NumPy

```{.python tiedosto="esimerkit/pikaopas-python.py" osa="python"}
```

```{.tuloste tiedosto="esimerkit/pikaopas-python.odotettu"}
```

- NumPy-taulukot kiertävät hiljaa: `sum(dtype=np.int64)`.
- `sum` kompensoi (3.12+), `math.fsum` on tarkka, `np.sum` parittain.
- `float.hex()` / `%a` ja `%.17g` säilyttävät arvon tarkasti.

# Kvantisointi

- Symmetrinen (painot): $s = \max|w| / 127$, $q = \text{round}(w/s)$.
- Asymmetrinen (aktivaatiot): $s = (\max - \min)/255$,
  $z = \text{round}(-128 - \min/s)$, $x \approx s(q - z)$.
- Kertymä leveämpi: int8 → int32, FP8/bf16 → float32.

# Muisti

- Rivijärjestys (C, NumPy): $(i, j) \to i \cdot n + j$. Sarakejärjestys
  (Fortran, BLAS, MATLAB): $(i, j) \to j \cdot m + i$.
- Sisin silmukka peräkkäisiin osoitteisiin; matriisitulo ikj tai
  lohkottuna, tuotannossa BLAS (`@`, `dgemm`).
- Näkymä: viipale, `.T`, `transpose`. Kopio: `reshape` ei-yhtenäisestä,
  `ascontiguousarray`, `.copy()`.
- Kuvat HWC (Pillow, OpenCV), neuroverkot NCHW (PyTorch) tai NHWC.
