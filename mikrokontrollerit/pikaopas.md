---
title: Mikrokontrollerit ja bare-metal-ohjelmointi
subtitle: Pikaopas · Cortex-M, käynnistys, rekisterit, keskeytykset, viat
---

# Muistikartta

| Alue | Osoite | Sisältö |
|------|--------|---------|
| Code | `0x00000000` | flash, vektoritaulu (VTOR) |
| SRAM | `0x20000000` | RAM; bit-band `0x22000000` |
| Peripheral | `0x40000000` | piirin oheislaitteet; bit-band `0x42000000` |
| SysTick | `0xE000E010` | CTRL, LOAD, VAL, CALIB |
| NVIC | `0xE000E100` | ISER, ICER, ISPR, ICPR, IABR, IPR |
| SCB | `0xE000ED00` | CPUID, ICSR, VTOR, AIRCR, SCR, CCR, SHPR, SHCSR, CFSR |
| MPU | `0xE000ED90` | TYPE, CTRL, RNR, RBAR, RASR |

# Rekisterit ja tilat

| Rekisteri | Tehtävä |
|-----------|---------|
| `r0`–`r3`, `r12` | argumentit, paluuarvo; kutsuja tallentaa |
| `r4`–`r11` | kutsuttu tallentaa |
| `sp` | MSP (Handler, reset) tai PSP (CONTROL.SPSEL) |
| `lr` | paluuosoite; poikkeuksessa EXC_RETURN |
| PRIMASK, BASEPRI | peitä kaikki / heikommat keskeytykset |
| CONTROL | nPRIV (bitti 0), SPSEL (bitti 1) |

Poikkeuskehys: r0, r1, r2, r3, r12, lr, pc, xPSR. EXC_RETURN
`0xFFFFFFF9` = Thread ja MSP, `0xFFFFFFFD` = Thread ja PSP,
`0xFFFFFFF1` = Handler. Koodiosoitteet parittomia (Thumb).

# Käynnistys

Reset: MSP ← [0], PC ← [4]. Reset_Handler: kopioi `.data`
(LMA → VMA), nollaa `.bss`, kellot ja FPU, `main`.

```{.c tiedosto="esimerkit/yhteinen/kaynnistys.c" osa="reset"}
```

```{.ld tiedosto="esimerkit/yhteinen/laite.ld" osa="muisti"}
```

- `.data : { ... } > RAM AT> FLASH`, `LOADADDR(.data)`.
- `KEEP(*(.vektorit))` ensimmäisenä; `(NOLOAD)` `.bss`:lle ja pinolle.
- Liput: `-mcpu=cortex-m3 -mthumb`, `-ffreestanding`,
  `-ffunction-sections -fdata-sections`, `-nostartfiles`,
  `-Wl,--gc-sections,-Map=x.map`.

# Rekisterit C:ssä

  Tarkoitus     Lauseke
  ------------- --------------------------------------------
  aseta         `REG |= MASKI;`
  nollaa        `REG &= ~MASKI;`
  testaa        `if (REG & MASKI)`
  kenttä        `REG = (REG & ~(0xFu << 4)) | (v << 4);`
  kuittaa W1C   `REG = MASKI;` (ei `|=`)
  ------------- --------------------------------------------

- Rakenne + `volatile` + `_Static_assert(offsetof(...))`.
- `volatile` ≠ atominen; RMW suojataan tai käytetään SET/CLR-rekistereitä
  tai bit-bandia.
- Ei toimi? Oheislaitteen kello, nastan toiminto, aktiivinen nolla.

# NVIC

```{.c tiedosto="esimerkit/yhteinen/mps2.h" osa="nvic-apu"}
```

- Pienempi luku = kiireellisempi; vain kiireellisempi keskeyttää.
- Tasapeli: pienempi numero. Ketjutus ilman kehyksen purkua.
- Kuittaa syy oheislaitteesta, mieluiten alussa.
- BASEPRI = n peittää prioriteetit ≥ n; 0 = ei peittoa.

# Jaettu data

```{.c tiedosto="esimerkit/07-kilpailu/main.c" osa="kriittinen"}
```

- LDREX/STREX tai `__atomic_*` (ei M0+).
- 64-bittinen laskuri: lue yläosa ennen ja jälkeen.
- Rengas: vapaat indeksit, koko 2^n^, data ennen indeksiä
  (`atomic_signal_fence`), laske ylivuodot.

# Ajastimet ja uni

```{.c tiedosto="esimerkit/06-ajastimet/main.c" osa="viive"}
```

```{.c tiedosto="esimerkit/09-uni/main.c" osa="silmukka"}
```

- SysTick LOAD = jakso − 1; aika `nyt - alku` (etumerkitön).
- WFI herää odottavaan keskeytykseen myös PRIMASK = 1.
- SCR: SLEEPDEEP, SLEEPONEXIT, SEVONPEND. Tikitön uni RTC:llä.
- Vahtikoira: ruoki pääsilmukasta todistetun edistyksen jälkeen.

# Viat

```{.c tiedosto="esimerkit/10-viat/main.c" osa="stub"}
```

| Bitti (CFSR) | Syy |
|--------------|-----|
| DACCVIOL, MMARVALID | MPU, osoite MMFAR:ssa |
| PRECISERR, BFARVALID | väylävirhe, osoite BFAR:ssa |
| IMPRECISERR | puskuroitu kirjoitus; PC ei osu |
| UNDEFINSTR | hyppy dataan, ylikirjoitettu paluuosoite |
| INVSTATE | Thumb-bitti 0: nollaosoitin, väärä funktio-osoitin |
| NOCP | FPU sallimatta |
| DIVBYZERO, UNALIGNED | CCR.DIV_0_TRP, CCR.UNALIGN_TRP |

HFSR.FORCED = eskaloitunut; salli SHCSR:n MEM/BUS/USGFAULTENA.

# gdb

| Komento | Tehtävä |
|---------|---------|
| `target extended-remote :3333` | OpenOCD, pyOCD (QEMU `-s`: `:1234`) |
| `load`, `monitor reset halt` | ohjelmoi, resetoi |
| `break f`, `break x.c:18 if i >= 7` | katkopiste (laitteisto: 4–6) |
| `watch v`, `rwatch`, `awatch` | vahtipiste (DWT: 2–4) |
| `p arr[0]@n`, `x/8wx osoite` | taulukko, muisti |
| `finish`, `bt`, `info symbol 0x...` | paluuarvo, kutsupino, osoite |

```text
arm-none-eabi-size x.elf; arm-none-eabi-nm -n -S x.elf
arm-none-eabi-objdump -d -S x.elf; arm-none-eabi-addr2line -e x.elf 0x...
qemu-system-arm -M mps2-an385 -nographic -kernel x.elf -S -s
```
