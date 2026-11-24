---
title: Tietokonearkkitehtuuri
subtitle: Pikaopas · käskykanta, liukuhihna, ennustus, välimuistit, MMU ja moniytimet
---

# Suorituskyky

| Kaava | Merkitys |
|-------|----------|
| $T = N \cdot \text{CPI} \cdot t_\text{jakso}$ | rautalaki |
| $\text{IPC} = 1 / \text{CPI}$ | käskyä jaksossa |
| $1 / ((1-p) + p/s)$ | Amdahl: osuus $p$ nopeutuu $s$-kertaisesti |
| $\text{CPI} = 1 + f_\text{lat} \cdot p_\text{lu} + f_\text{haara} \cdot m \cdot c$ | liukuhihnan CPI |
| $\text{AMAT} = t_1 + h_1 (t_2 + h_2 t_m)$ | keskimääräinen muistiviive |
| kaista × viive = keskeneräiset tavut | Littlen laki (MLP) |

# RV32I-käskymuodot

| Muoto | 31..25 | 24..20 | 19..15 | 14..12 | 11..7 |
|-------|--------|--------|--------|--------|-------|
| R | funct7 | rs2 | rs1 | f3 | rd |
| I | imm[11:5] | imm[4:0] | rs1 | f3 | rd |
| S | imm[11:5] | rs2 | rs1 | f3 | imm[4:0] |
| B | imm[12,10:5] | rs2 | rs1 | f3 | imm[4:1,11] |
| U | imm[31:25] | imm[24:20] | imm[19:15] | imm[14:12] | rd |
| J | imm[20,10:5] | imm[4:1,11] | imm[19:15] | imm[14:12] | rd |

Opcode bitit 6..0. Etumerkki aina bitissä 31. Haarat ±4 KiB, `jal`
±1 MiB, siirtymät pc-suhteellisia. Vakio: `lui (x+0x800)>>12` + `addi`.

```{.cpp tiedosto="esimerkit/yhteinen/rv32i.hpp" osa="bitit"}
```

# Liukuhihna

- Vaiheet IF, ID, EX, MEM, WB. Rekisteritiedosto: kirjoitus jakson
  alussa, luku lopussa.
- Ilman kytkentää RAW vierekkäin = 2 pysähdystä. Kytkentä EX/MEM → EX
  ja MEM/WB → EX; tuoreempi voittaa, rd ≠ x0.
- Load–use = 1 pysähdys kytkennästäkin huolimatta. Siirrä
  riippumaton käsky väliin.
- Haara ratkeaa EX:ssä: väärä ennuste 2 jaksoa, `jal` 1, `jalr` 2.
- Optimaalinen syvyys $n \approx \sqrt{t / (o \cdot p)}$.

# Ennustimet

| Ennustin | Idea | Heikkous |
|----------|------|----------|
| ei hypätä | aina PC + 4 | silmukat |
| BTFN | taaksepäin = silmukka | datasta riippuvat |
| 1-bittinen | viimeisin suunta | 2 virhettä per silmukka |
| 2-bittinen | kyllästyvä laskuri 0..3 | ei korrelaatiota |
| gshare | historia XOR PC | hidas oppia, jakaminen |
| TAGE | monta historian pituutta | koko, monimutkaisuus |
| BTB, RAS | kohde, paluuosoitepino | epäsuorat hypyt (ITTAGE) |

# Välimuistit

- Osoite = tagi | indeksi ($\log_2$ joukot) | siirtymä ($\log_2$ lohko).
  Joukot = koko / (lohko × tiet).
- 3C: pakollinen (lohko, esihaku), kapasiteetti (koko), ristiriita
  (tiet, täyte).
- LRU on huono hieman välimuistia suuremmalle silmukalle.
- WB + WA oletus; WT + no-WA kertakirjoituksille; WB voi hävitä, jos
  likainen lohko syrjäytyy toistuvasti.
- Rivi peräkkäin (row-major): sisin silmukka viimeisen indeksin yli.

```{.cpp tiedosto="esimerkit/yhteinen/valimuisti.hpp" osa="asetukset"}
```

# Virtuaalimuisti

| Muoto | VPN-kentät | Sivut |
|-------|------------|-------|
| Sv32 | 10 + 10 | 4 KiB, 4 MiB |
| Sv39 | 9 + 9 + 9 | 4 KiB, 2 MiB, 1 GiB |
| Sv48 | 9 × 4 | + 512 GiB |

- PTE: V R W X U G A D + PPN. R = W = X = 0 → seuraava taso.
- Sivuvirheet: 12 nouto, 13 lataus, 15 talletus.
- TLB-ulottuvuus = alkiot × sivu. VIPT: L1 ≤ tiet × 4 KiB.
- `satp` = tila | ASID | juuren PPN; `sfence.vma` tyhjentää.

# Ansat

| CSR | Sisältö |
|-----|---------|
| `mtvec` | käsittelijän osoite |
| `mepc` | poikkeus: aiheuttaja; keskeytys: seuraava käsky |
| `mcause` | syy; bitti 31 = keskeytys (7 ajastin, 11 ulkoinen) |
| `mtval` | virheellinen osoite tai käsky |
| `mstatus` | MIE, MPIE, MPP |
| `mie` / `mip` | sallitut / odottavat keskeytykset |

Poikkeuksessa `mepc += 4` ennen `mret`ia (paitsi uudelleensuoritus).
Ajastin: `mtimecmp` eteenpäin. Tallenna rekisterit (`mscratch`).
MMIO: ei välimuistia, `volatile`, `fence`.

# Koherenssi

| Tila | Ainoa | Likainen | Kirjoitus |
|------|-------|----------|-----------|
| M | kyllä | kyllä | heti |
| E | kyllä | ei | hiljaa → M |
| S | ei | ei | BusUpgr |
| I | – | – | BusRdX |

Väärä jakaminen: eri muuttujat samassa 64 B:n lohkossa →
`alignas(64)`. Vahvin SC, sitten TSO (x86), heikoin RVWMO; `std::atomic` oletuksena SC.
NUMA: first touch, `numactl`.

# Superskalaari

- In-order: leveys auttaa vähän. OoO: nimeäminen (WAR, WAW pois),
  liikkeellelähtöjono, ROB (järjestyksessä poisto = tarkat poikkeukset).
- Ikkuna × ennustustarkkuus määrää IPC:n; riippuvuusketju on yläraja.
- x86 → µop:t; makrofuusio `cmp`+`jcc`, mikrofuusio lataus+ALU,
  µop-välimuisti.

# Mittaaminen

```text
perf stat -e cycles,instructions,branch-misses,cache-misses ./ohjelma
perf stat -e dTLB-load-misses,page-faults ./ohjelma
perf c2c record ./ohjelma && perf c2c report     # väärä jakaminen
valgrind --tool=cachegrind ./ohjelma             # välimuistisimulaatio
numactl --hardware                               # NUMA-topologia
```
