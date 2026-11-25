---
title: DSP-algoritmien laitteistototeutus
subtitle: Pikaopas · sanaleveydet, rakenteet, CORDIC, NCO, CIC, polyfaasi, verifiointi
---

# Sanaleveydet

| Operaatio | Leveys |
|-----------|--------|
| Qa.b × Qc.d | Q(a+c).(b+d) |
| $N$ termin summa | $+\lceil \log_2 N \rceil$ bittiä |
| tarkka FIR-raja | vahvistus $\le \sum_k \lvert h_k \rvert$ |
| esisumma $x_i + x_j$ | +1 bitti |
| CIC sisäinen | $B_{in} + N \log_2(RM)$ |
| CORDIC sisäinen | +2 bittiä aluetta, $+\log_2 n$ murtobittiä |

| Kavennus | Laitteisto | Virhe |
|----------|------------|-------|
| katkaisu | johdotus | −0,5 LSB keskimäärin, −6 dB SNR |
| pyöristys lähimpään | 1 summain | 0 keskimäärin |
| saturaatio | vertailu + multiplekseri | ylivuoto jää rajalle |
| kierto | johdotus | etumerkki kääntyy |

```{.python tiedosto="esimerkit/malli/kiintea.py" osa="pyoristys"}
```

Saturaatio RTL:ssä: arvo mahtuu, jos pudotettavat ylimmät bitit ja uusi
etumerkkibitti ovat kaikki samoja (`&` tai `~|`).

# Bittitarkka malli

1. Datapolussa vain kokonaislukuja.
2. Jokainen rajaus nimettynä funktiona samassa kohdassa kuin RTL:ssä.
3. Tila alkaa nollasta.
4. Sama järjestys tilalle; summien järjestys vapaa.

Kertoimet kokonaislukuina versionhallintaan, RTL-vakiot generoidaan
ja tarkistetaan testissä.

# FIR-rakenteet

| Rakenne | Kertojia | Latenssi | Kriittinen polku |
|---------|----------|----------|------------------|
| suora | $N$ | 3 | summainpuu |
| transponoitu | $N$ | 1 | kertoja + summain, haarautuminen |
| symmetrinen | $N/2$ | 3 | esisummain + kertoja |
| systolinen | $N$ | $N + 2$ | kertoja + summain |
| jaettu (MAC) | $\lceil N/C \rceil$ | $N + 1$ | kertoja + summain |

$C$ = kellojaksoja näytettä kohden.

# Vastapaine

```{.systemverilog tiedosto="esimerkit/rtl/fir_suora.sv" osa="pysaytys"}
```

- Valid-bitit kulkevat datan rinnalla jokaisessa vaiheessa.
- Pitkä ready-polku tai suuri haarautuminen → liukupuskuri tai luotot.
- `valid` ei saa riippua `ready`:stä.

# IIR

- Toisen asteen lohkot, DF1: yksi kertymä, yksi kavennus.
- Kertoimet Q2.14 ($\lvert a_1 \rvert < 2$), vahvistus jaettuna
  lohkoille.
- Silmukkaa ei voi liukuhihnoittaa: lyhennä, ennakoi tai lomita
  ($C$-slow).
- Saturoi takaisinkytkentä aina. Kuollut alue
  $\le 0{,}5 / (1 + a_1 + a_2)$ LSB.

# CORDIC

| Tila | Suunta $d_i$ | Tulos |
|----------|------------------|---------------------------------------------|
| rotaatio | $\mathrm{sign}(z_i)$ | $(x, y)$ kierrettynä kulmalla $z$, kertaa $K$ |
| vektori | $-\mathrm{sign}(y_i)$ | $x = K\lvert v \rvert$, $z = \mathrm{atan2}(y, x)$ |

```{.python tiedosto="esimerkit/malli/cordic.py" osa="iteraatio"}
```

- $K \approx 1{,}6468$; kompensoi alkupisteellä $(1/K, 0)$.
- Esikierto: 2. ja 3. neljännes (vektori: $x < 0$) → $-v$, $z + \pi$.
- Noin bitti kierrosta kohden; binäärikulmat (kierros $= 2^n$).
- Iteratiivinen: 1 vaihe, siirtäjä. Liukuhihna: $n$ vaihetta, ei
  siirtäjiä.

# NCO

- $f = M / 2^P \cdot f_s$, resoluutio $f_s / 2^P$, vaihejatkuva.
- Neljännesjakson taulukko, arvot $\sin(\frac{\pi}{2} \cdot
  \frac{i + 1/2}{2^A})$: peilaus = bittien kääntö.
- Vaiheen katkaisu → kannuspiikit, noin 6 dB vaihebittiä kohden.
- Keinot: suurempi taulukko, dither, interpolointi, CORDIC.

# Monitaajuus

- CIC: $N$ integraattoria → desimointi $R$ → $N$ kampaa; ei
  kertojia. Integraattorit saavat kiertää, ei saturointia.
- CIC:n taipuma kompensoidaan FIR-suotimella matalalla taajuudella.
- Polyfaasi: haara $p$ käyttää kertoimia $h_p, h_{p+R}, \ldots$;
  kertojia $N/R$.
- Malli määritelmästä (suodin + valinta), ei toteutuksen kopiona.

# Verifiointi

| Testi | Löytää |
|-------|--------|
| impulssi | kertoimet, järjestys |
| askel | DC-vahvistus, ylitys, saturaatio |
| pahin tapaus | $\sum \lvert h \rvert$-raja, saturaatio |
| satunnainen + tauot + vastapaine | ohjaus, liukuhihnan pysähdys |
| taajuusvaste | suunnittelu, kertoimet (toleranssilla) |
| bittitarkka vertailu | pyöristys, saturaatio, bittisiirrot |

```text
make -C esimerkit                        # kaikki
make -C esimerkit cocotb-fir-suora       # yksi cocotb-ajo
make -C esimerkit cocotb-fir-suora-katkaisu   # istutettu vika
make -C esimerkit verilator-fir          # 100 000 näytettä
make -C esimerkit synteesi-fir-suora-lut # resurssit ja Fmax
PAIVITA=1 make -C esimerkit ...          # odotetut uudelleen
```

# FPGA (iCE40 UP5K)

- 8 × SB_MAC16 (16 × 16, kertymä 32), 30 × SB_RAM40_4K, 39 nastaa.
- `synth_ice40 -dsp`: DSP-lohkot; ilman: kertojat LUT-soluista.
- nextpnr ei mallinna SB_MAC16:n viiveitä → Fmax LUT-versiosta.
- Vakiokertoja LUT-soluina = siirrot ja yhteenlaskut (CSD).
- Transponoitu + symmetriset kertoimet → synteesi yhdistää tulot.
