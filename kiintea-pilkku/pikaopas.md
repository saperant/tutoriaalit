---
title: Kiinteän pilkun aritmetiikka
subtitle: Pikaopas · Q-formaatit, bittikasvu, pyöristys, saturaatio ja sanaleveydet
---

# Q-formaatit

| Muoto | Bitit | Alue | LSB |
|-------|-------|------|-----|
| Qm.n | $m+n$ | $[-2^{m-1},\ 2^{m-1}-2^{-n}]$ | $2^{-n}$ |
| UQm.n | $m+n$ | $[0,\ 2^m - 2^{-n}]$ | $2^{-n}$ |
| Q1.15 | 16 | $[-1,\ 1 - 2^{-15}]$ | $3{,}05 \cdot 10^{-5}$ |
| Q1.31 | 32 | $[-1,\ 1 - 2^{-31}]$ | $4{,}66 \cdot 10^{-10}$ |
| Q8.8 | 16 | $[-128,\ 128 - 2^{-8}]$ | $0{,}0039$ |

- Arvo = koodi $\cdot\, 2^{-n}$. Koodi = round(arvo $\cdot\, 2^n$),
  saturoiden.
- Muodon vaihto: $+k$ murtobittiä = `<< k`, $-k$ = pyöristys ja
  `>> k`.
- Yhteenlasku vaatii kohdistetut pilkut.

# Bittikasvu

| Operaatio | Tulos |
|-----------|-------|
| Qa.b + Qa.b | Q(a+1).b |
| Qa.b × Qc.d | Q(a+c).(b+d) |
| $K$ tulon kertymä | $+\lceil \log_2 K \rceil$ vartijabittiä |
| FIR, syöte Q1.n | $+\lceil \log_2 \sum_k \lvert h_k\rvert \rceil$ |

- $n \times n$ etumerkillinen tulo: $2n-1$ bittiä paitsi
  $(-2^{n-1})^2$, joka vaatii $2n$.
- Q1.15 × Q1.15 = Q2.30; DSP-kertymä 40 bittiä = 32 + 8 vartijabittiä.

```{.c tiedosto="esimerkit/pikaopas.c" osa="perus"}
```

# Pyöristys

| Tapa | Harha (LSB) | RMS (LSB) | Hinta |
|------|-------------|-----------|-------|
| katkaisu (lattia) | $\approx -0{,}5$ | $\approx 0{,}58$ | ei mitään |
| kohti nollaa | 0, vaimentaa | $\approx 0{,}58$ | pieni |
| lähimpään, ylös | $2^{-k-1}$ | $\approx 0{,}29$ | summain |
| lähimpään parilliseen | 0 | $\approx 0{,}29$ | summain + tasapeli |

- Pyöristä kerran, lopuksi. Takaisinkytkennöissä parilliseen ja
  tilaan lisää murtobittejä (kuollut alue).
- C: `x / 2^k` pyöristää kohti nollaa, `>>` kohti −∞.

# Ylivuoto

- **Kierto** (ilmainen): virhe ≈ koko alue. Sallittu välituloksissa,
  jos lopputulos mahtuu (Jacksonin sääntö).
- **Saturaatio** (vertailu + mux): virhe pieni. Ulostuloihin ja
  IIR-takaisinkytkentöihin.
- $-1 \times -1 = +1$ ei mahdu Q1.15:een: saturoi tai rajaa pois.

# Kvantisointikohina

- $\sigma_e^2 = q^2/12$; täyden skaalan sini: SQNR $\approx
  6{,}02\,b + 1{,}76$ dB.
- Taso $-L$ dB → SQNR $-L$ dB (absoluuttinen tarkkuus).
- FIR-kertoimet: bittejä $\gtrsim$ vaimennus/6 + varaus.
- Budjetti: $\sigma_e^2 = \frac{q_x^2}{12}\sum h^2 +
  \sigma_x^2 \sum \delta h^2 + \frac{q_y^2}{12}$.

# Kiinteä vai liukuluku

| | Kiinteä | Liukuluku |
|-|---------|-----------|
| summain 32 b | ~32 | ~350 (binary32) |
| kertoja 32 b | ~1000 | ~630 (24-b mantissa) |
| tarkkuus | absoluuttinen | suhteellinen |
| sopii | tunnettu dynamiikka | tuntematon dynamiikka |

- Lohkoliukuluku: yhteinen eksponentti lohkolle, SQNR pysyy tasosta
  riippumatta.

# Sudenkuopat

- Etumerkkilaajennus: `(x ^ m) - m`, `m` = etumerkkibitin paino.
- `int32_t a, b; a * b` lasketaan 32 bitissä → `(int64_t)a * b`.
- Etumerkillinen ylivuoto C:ssä on määrittelemätön → kierto
  `uint32_t`:llä.
- Testaa $-2^{n-1}$, $2^{n-1}-1$, 0, −1 ja niiden tulot.
