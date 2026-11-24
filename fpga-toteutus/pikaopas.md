---
title: FPGA-toteutus
subtitle: Pikaopas · iCE40, Yosys, nextpnr, ajoitus, kellot ja kortti
---

# Vuo

| Vaihe | Työkalu | Tuotos | Tarkistus |
|-------|---------|--------|-----------|
| Simulointi | Verilator | toiminta | testipenkki |
| Synteesi | `yosys` / `synth_ice40` | netlista (JSON) | `stat`: RAM, DSP, kanto |
| Sijoittelu ja reititys | `nextpnr-ice40` | ASC, raportti | Fmax `PASS`, käyttöaste |
| Bittivirta | `icepack` | BIN | koko |
| Lataus | `iceprog` (`-S` SRAMiin) | konfiguroitu piiri | vilkku, tunnisterekisteri |

# Komennot

```{.bash tiedosto="esimerkit/tyokalut/vuo.sh" osa="vuo"}
```

```{.makefile tiedosto="esimerkit/Makefile" osa="bittivirta"}
```

| Valinta | Merkitys |
|---------|----------|
| `synth_ice40 -dsp` | kertojat `SB_MAC16`-lohkoihin |
| `synth_ice40 -retime` | uudelleenajoitus (ABC `-dff`) |
| `chparam -set P 1 ylin` | parametri synteesiin |
| `--up5k --package sg48` | piiri ja kotelo |
| `--freq 48` | tavoitetaajuus MHz |
| `--pcf x.pcf` | nastat; ilman sitä vain `--pcf-allow-unconstrained` |
| `--seed N` | sijoittelun siemen (vaihtelu noin 5 %) |
| `--report r.json` | Fmax, käyttöaste, kriittiset polut |

# iCE40UP5K

| Resurssi | Määrä | Primitiivi |
|----------|-------|------------|
| Logiikkasolu (LUT4 + kiikku + kanto) | 5 280 | `SB_LUT4`, `SB_DFF*`, `SB_CARRY` |
| Lohko-RAM 4 kbit | 30 | `SB_RAM40_4K` (256×16 … 2048×2) |
| SPRAM 256 kbit | 4 | `SB_SPRAM256KA` (instansioidaan) |
| DSP 16×16 + 32 b kertymä | 8 | `SB_MAC16` |
| PLL | 1 | `SB_PLL40_PAD`, `SB_PLL40_CORE` |
| Globaali verkko | 8 | `SB_GB` |
| Oskillaattorit | 2 | `SB_HFOSC` 48 MHz, `SB_LFOSC` 10 kHz |
| Käyttäjän IO (SG48) | 39 | `SB_IO` |

# Koodaustyyli

| Kuvaus | Tulos |
|--------|-------|
| muisti, rekisteröity luku | `SB_RAM40_4K` |
| muisti, kombinatorinen luku | kiikut ja multiplekseri (kallis) |
| `a * b` ja `-dsp` | `SB_MAC16` |
| `a * b` ilman `-dsp` | LUT:t ja kantoketju (8×8 ≈ 160 solua) |
| vakiolla kertominen | siirrot ja summat |
| alkuarvo `= '0` | bittivirrassa, ei nollauslogiikkaa |
| synkroninen nollaus | `SB_DFFSR` |
| `if (en) q <= d;` | `SB_DFFE` |

```{.systemverilog tiedosto="esimerkit/04-muisti/muisti.sv" osa="muisti"}
```

# Ajoitus

- Polku: kello → lähtö + Σ(LUT + reititys) + asetus ≤ jakso.
  Reititys on usein yli puolet viiveestä.
- Korjaukset: liukuhihnoitus, rekisteröity IO, kopioitu rekisteri,
  kantoketju ja DSP aritmetiikalle, one-hot-tilakone, `-retime`.
- Ei tarkisteta: IO-polut (`<async>`), kellojen väliset polut,
  DSP:n sisäiset polut.
- Marginaali vähintään 10 %; siementen kokeilu ei korvaa sitä.

# Kellot

```text
$ icepll -i 12 -o 48
DIVR:  0 (4'b0000)
DIVF: 63 (7'b0111111)
DIVQ:  4 (3'b100)
FILTER_RANGE: 1 (3'b001)
```

f = f_tulo · (DIVF + 1) / ((DIVR + 1) · 2^DIVQ), VCO 533–1066 MHz.

```{.systemverilog tiedosto="esimerkit/07-pll/pll_ylin.sv" osa="nollaus"}
```

- Hidas tahti sallinnalla, ei johdetulla kellolla.
- Ei kellon portitusta logiikalla.
- PLL vain `ifdef SYNTHESIS` -lohkoon; simulaatiossa suora kytkentä.

# Kellotusalueet

| Signaali | Rakenne |
|----------|---------|
| yksi bitti, asynkroninen tulo | kaksi kiikkua |
| nollaus | asynkroninen asetus, tahdistettu vapautus |
| pulssi | vaihtosignaali + tahdistin + reunan tunnistus |
| monibittinen arvo | kättely |
| tietovirta | asynkroninen FIFO, Gray-osoittimet |

- SDC/XDC: `set_clock_groups -asynchronous`,
  `set_max_delay -datapath_only` Gray-väylille, `ASYNC_REG`.
- nextpnr raportoi kellojen väliset viiveet mutta ei tarkista niitä.

# PCF

```{tiedosto="esimerkit/01-vilkku/icebreaker.pcf"}
```

# Kortilla

1. Vilkku: bittivirta, kello, nastat.
2. UART-silmukka: baudinopeus, isännän asetukset.
3. Virheenjäljitysydin: tunnisterekisteri `0x42`, laskuri.
4. Oma suunnitelma ytimen rinnalla; ILA viimeisenä.

| Oire | Syy |
|------|-----|
| ei mitään | nasta, PCF, kotelo |
| toimii joskus | ajoitus `FAIL`, tahdistamaton tulo |
| vain kerran | nollaus puuttuu |
| UART sekaisin | baudinopeus, PLL |
