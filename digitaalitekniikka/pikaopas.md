---
title: Digitaalitekniikka
subtitle: Pikaopas · portit, aritmetiikka, kiikut, tilakoneet ja ajoitus
---

# Luvut

| Esitys | Sääntö |
|--------|--------|
| Kahden komplementti | MSB:n paino $-2^{n-1}$; $n$ bitillä $-2^{n-1} \ldots 2^{n-1}-1$ |
| Vastaluku | käännä bitit, lisää 1 ($-x = \bar{x} + 1$) |
| Vähennys | $a - b = a + \bar{b} + 1$ (b käännetään, tulomuisti 1) |
| Etumerkin laajennus | kopioi MSB uusiin bitteihin |
| Gray-koodi | $g = n \oplus (n \gg 1)$; peräkkäiset eroavat yhdessä bitissä |
| BCD | numero kerrallaan neljällä bitillä |

# Boolen algebra

| Laki | Muoto |
|------|-------|
| De Morgan | $\overline{ab} = \bar{a} + \bar{b}$, $\overline{a+b} = \bar{a}\,\bar{b}$ |
| Osittelu | $a(b+c) = ab + ac$, $a + bc = (a+b)(a+c)$ |
| Absorptio | $a + ab = a$, $a(a+b) = a$ |
| Konsensus | $ab + \bar{a}c + bc = ab + \bar{a}c$ |
| Yhdistäminen | $xy + x\bar{y} = x$ (Karnaugh, Quine–McCluskey) |

- NAND ja NOR ovat universaaleja: $\bar{a} = \overline{aa}$,
  $a + b = \overline{\bar{a}\,\bar{b}}$.
- CMOS: pMOS-ylösveto ja nMOS-alasveto ovat duaalit (sarja ↔ rinnan).
  Dynaaminen teho $P \approx \alpha C V^2 f$.

```{.python tiedosto="esimerkit/qm.py" osa="yhdista"}
```

# Kombinaatiologiikka

```{.systemverilog tiedosto="esimerkit/05-kombinaatio.sv" osa="prioriteetti"}
```

- Mux $2^k$:1 on universaali; FPGA:n LUT on muisti + mux.
- `if`–`else if` = prioriteettiketju; `case` = rinnakkainen valinta.

# Summaimet ja ALU

```{.systemverilog tiedosto="esimerkit/06-summain/taysisummain.sv" osa="taysisummain"}
```

| Rakenne | Viive $n$ bitille | Koko |
|---------|-------------------|------|
| Ripple-carry | $\sim 2n$ porttia | pienin |
| Lookahead, 4 bitin lohkot | $\sim n/2$ | keskikokoinen |
| Prefiksipuu (Kogge–Stone) | $\sim \log_2 n$ | suurin |

| Lippu | Laskenta |
|-------|----------|
| N | tuloksen MSB |
| Z | kaikki bitit nollia |
| C | muisti ulos (vähennyksessä 1 = ei lainaa, Arm) |
| V | muisti MSB:hen $\oplus$ muisti MSB:stä |

# Ajoitus

| Ehto | Kaava |
|------|-------|
| Asetus | $T \geq t_{cq} + t_{logiikka,max} + t_{su}$ |
| Pito | $t_{cq} + t_{logiikka,min} \geq t_h$ |
| Maksimitaajuus | $f_{max} = 1 / (t_{cq} + t_{max} + t_{su})$ |
| Tahdistimen MTBF | $e^{t_r/\tau} / (T_w f_{kello} f_{data})$ |

- Asetusrike: hidasta kelloa tai lyhennä polkua. Pitorike: lisää
  viivettä, kello ei auta.
- Liukuhihna: lyhyempi polku, suurempi latenssi, sama tai parempi
  läpäisy.

# Muisti ja tilakoneet

```{.systemverilog tiedosto="esimerkit/08-kiikut.sv" osa="kiikku"}
```

```{.systemverilog tiedosto="esimerkit/09-laskurit.sv" osa="laskuri"}
```

- Salpa läpinäkyvä sallinnan ollessa 1; kiikku näytteistää reunalla.
- Moore: lähtö tilasta, jakson viive. Mealy: lähtö tilasta ja
  syötteestä, samassa jaksossa.
- Suunnittelu: kaavio → taulu → koodaus → logiikka → testi taulua
  vastaan.

# Työkalut

| Tarkoitus | Komento |
|-----------|---------|
| Simulointi | `verilator --binary --assert -Wall --top-module testipenkki *.sv` |
| Ajo | `./obj_dir/Vtestipenkki` |
| Python-mallit | `ruff check x.py && mypy --strict x.py && python3 x.py` |
| Kaikki esimerkit | `make -C digitaalitekniikka testaa` |
