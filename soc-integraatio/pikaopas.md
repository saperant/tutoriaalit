---
title: SoC-integraatio
subtitle: Pikaopas – väylät, muistikartta, rekisterit, keskeytykset ja alueet
lang: fi
---

# Muistikartta

```{.c tiedosto="esimerkit/sw/soc.h" osa="kartta"}
```

- Ikkunat 4 KiB, tasattuja: dekoodaus ylimmistä biteistä, suojaus
  sivuittain.
- Tyhjä osoite → DECERR → poikkeus (5 luku, 7 kirjoitus).
- Laitteiston `KANTA`/`MASKI`, otsake ja linkkeriskripti samasta
  lähteestä.

# AXI4 ja AXI4-Lite

| Kanava | Suunta | Sisältö |
|--------|--------|---------|
| AR / R | M→S / S→M | lukuosoite / data + RRESP |
| AW / W | M→S | kirjoitusosoite / data + WSTRB |
| B | S→M | BRESP |

1. VALID pysyy ja sisältö säilyy kättelyyn asti.
2. VALID ei odota READYä (READY saa odottaa VALIDia).
3. Orja saa odottaa AW:tä ja W:tä; isäntä ei odota AWREADYä ennen
   W:tä.
4. Vastaus vasta osoitteen kättelyn jälkeen.

| Vastaus | Merkitys |
|---------|----------|
| OKAY 00 | onnistui |
| SLVERR 10 | orja tunnisti virheen |
| DECERR 11 | ei orjaa osoitteessa |

AXI4 lisää: purskeet (AxLEN ≤ 255, INCR/WRAP/FIXED, ei yli 4 KiB:n
rajan), tunnisteet (sama ID → sama järjestys), avoimet siirrot,
AxCACHE/AxPROT/AxQOS.

# APB

| Vaihe | PSEL | PENABLE | Siirto päättyy |
|-------|------|---------|----------------|
| SETUP | 1 | 0 | – |
| ACCESS | 1 | 1 | kun PREADY = 1 |

APB3: PREADY, PSLVERR. APB4: PSTRB, PPROT. Kirjoitus ACCESS-
vaiheessa: `psel && penable && pwrite`.

# Rekisterityypit

| Tyyppi | Ohjelmisto | Laitteisto |
|--------|------------|------------|
| rw | kirjoittaa/lukee | lukee |
| ro | lukee | antaa |
| wo | kirjoittaa | arvo + pulssi |
| w1c | lukee, 1 nollaa | asettaa |
| vakio | lukee | – |

- Kuvaus → RTL + C-otsake + dokumentaatio; CI tarkistaa ajantasaisuuden.
- Ei read-to-clear-rekistereitä; kuittaus W1C:llä.
- MMIO: `volatile`-rakenne, `const` vain luettaville,
  `_Static_assert` siirroille.

# RISC-V M-tilan ansat

| CSR | Sisältö |
|-----|---------|
| mstatus | MIE (bitti 3), MPIE (bitti 7) |
| mie / mip | MTIE/MTIP (7), MEIE/MEIP (11) |
| mtvec | käsittelijän osoite |
| mepc | paluuosoite |
| mcause | ylin bitti 1 = keskeytys; 5/7 väylävirhe, 4/6 kohdistus, 2 laiton, 11 ecall |
| mtval | osoite tai käsky |

Ansa: `mepc ← pc`, `MPIE ← MIE`, `MIE ← 0`, `pc ← mtvec`.
`mret`: `pc ← mepc`, `MIE ← MPIE`.

# Keskeytykset

```{.c tiedosto="esimerkit/sw/keskeytykset.c" osa="ulkoinen"}
```

1. Lunasta (lue LUNASTA) → lähde peitetään.
2. Kuittaa syy oheislaitteessa (W1C).
3. Valmis (kirjoita numero takaisin).

CLINT: MTIP = `mtime >= mtimecmp`. 64-bittinen kirjoitus RV32:lla:
`L ← ~0`, `H ← uusi_H`, `L ← uusi_L`.

# DMA

- Ohjelmointi APB:n kautta, kopiointi AXI-isäntänä.
- Valmis ja virhe W1C-bitteinä, molemmat kuitataan.
- Ennen käynnistystä: muistieste ja välimuistin tyhjennys; ennen
  lukua: mitätöinti (ellei koherentti).
- Nopeus: purskeet + avoimet siirrot; IOMMU rajaa osoitteet.

# Kello-, nollaus- ja tehoalueet

- CDC vain tunnetuissa lohkoissa (tahdistin, kättely, asynkroninen
  FIFO); tarkista työkalulla.
- Kellon portitus ICG-solulla (salpa + JA), ei pelkällä JA-portilla.
- Nollaus: asetus asynkroninen, vapautus synkroninen; järjestys PLL →
  väylät → isännät.
- Sammutus: eristys → kello pois → virta pois.
- Käynnistys: virta → asettuminen → nollaus kellon käydessä →
  vapautus → eristys pois.
- UPF (IEEE 1801) kuvaa tehoalueet, eristyksen ja säilytyksen.

# Komennot

| Komento | Tehtävä |
|---------|---------|
| `make -C esimerkit` | kaikki simulaatiot ja tarkistukset |
| `make -C esimerkit aja-virheet` | yksi ohjelma |
| `make -C esimerkit generoi` | rekisterilohkot JSON:sta |
| `verilator --binary -Wall --assert` | simulaattorin käännös |
| `riscv64-unknown-elf-gcc -march=rv32i_zicsr -mabi=ilp32` | ohjelman käännös |
| `objcopy -O verilog --verilog-data-width=4` | `$readmemh`-kuva |
