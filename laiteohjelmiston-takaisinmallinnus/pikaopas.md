---
title: Laiteohjelmiston takaisinmallinnus
subtitle: Pikaopas · ARM Cortex-M, QEMU · objdump, radare2, gdb, Unicorn
---

# Vastuu ja rajat

Vain omat laitteet tai kohteet, joihin on lupa. Dekompilointi
tekijänoikeuslain ja EU:n ohjelmistodirektiivin rajoissa. Muokattu
radiolaite ei välttämättä ole vaatimustenmukainen. Heikkouksista
ilmoitus vastuullisesti valmistajalle.

# Työnkulku

| Vaihe | Kysymys |
|-------|---------|
| muoto | ELF, raaka, HEX/SREC vai säiliö? |
| sisältö | entropia: täyte, koodi, pakattu/salattu |
| arkkitehtuuri | vektoritaulu: pino, Reset, oheislaitteet |
| latausosoite | osoitinjoukon osumat |
| koodi | funktiot, kirjastot, algoritmit |
| ajo | sarja, gdb, QEMU, Unicorn |

# Muodon tunnistus

| Alku | Muoto |
|------|-------|
| `7f 45 4c 46` | ELF |
| `3a` (`:`) tekstiä | Intel HEX (`:LLAAAATT..CC`) |
| `53 30` (`S0`) | Motorola S-record |
| `78 9c`/`78 da` | zlib-pakattu |
| sana `0x2000....` + pariton | Cortex-M-vektoritaulu |

```{.bash tiedosto="esimerkit/01-muodot/aja.sh" osa="tunnistus"}
```

# Cortex-M-muistikartta

| Osoite | Sisältö |
|--------|---------|
| `0x00000000` | flash, vektoritaulu alussa |
| vektori 0 | pinon alkuarvo (RAM, `0x2000....`) |
| vektori 1 | Reset (pariton = Thumb) |
| `0x20000000` | RAM |
| `0x40000000`– | oheislaitteet |
| `0xE000E000`– | ytimen rekisterit (SCS, NVIC, VTOR) |

# Thumb-koodi (AAPCS)

| Kohde | Missä |
|-------|-------|
| argumentit | `r0`–`r3` |
| paluuarvo | `r0` |
| paluuosoite | `lr` (`r14`) |
| vakio/osoite | `ldr rX, [pc, #n]` (literaalivaranto) |
| kutsu / paluu | `bl` / `bx lr`, `pop {.., pc}` |
| hyppytaulu | `tbb`/`tbh [pc, rX]` (switch) |

# Työkalut

| Komento | Tehtävä |
|---------|---------|
| `python3 tunnista.py f` | muoto |
| `python3 entropia.py f` | entropia lohkoittain |
| `python3 vektorit.py f K T` | vektoritaulu |
| `python3 kanta.py bin` | latausosoite |
| `python3 oheislaitteet.py f K T L svd` | oheislaitteet |
| `python3 funktiot.py f K T L` | funktioluettelo |
| `python3 algoritmit.py f K T L` | algoritmit vakioista |
| `r2 -a arm -b 16 -m K` | radare2 Thumb-koodille |

```{.bash tiedosto="esimerkit/04-thumb/aja.sh" osa="r2"}
```

# Tunnetut vakiot

| Vakio | Algoritmi |
|-------|-----------|
| `0xEDB88320` | CRC-32 (zlib/Ethernet) |
| `0x1021` | CRC-16/CCITT |
| `0x9E3779B9` | TEA/XTEA (delta) |
| `0x6A09E667` | SHA-256 (alkuarvo) |

# Emulointi

| Työkalu | Käyttö |
|---------|--------|
| QEMU | koko kortti; `-icount` = toistettava |
| gdb | `target remote \| qemu ... -gdb stdio` |
| Unicorn | yksi funktio: kartoita muisti, aseta `r0`–`r3`, aja |

```{.python tiedosto="esimerkit/09-unicorn/emuloi.py" osa="crc"}
```

# Puolustus

| Heikkous | Korjaus |
|----------|---------|
| CRC aitoustakuuna | allekirjoitus julkisella avaimella |
| kovakoodattu avain | laitekohtainen avain suojatussa varastossa |
| avoin debug-portti | lukitus ja piirin lukkobitti |
| tarkistamaton jäsennin | pituustarkistus ennen kopiointia |

Suojaus salaamiseen tai hämäryyteen ei kestä takaisinmallinnusta; vain
kryptografia ja pääsynvalvonta kestävät. Korjaukset: *Sulautettujen
järjestelmien tietoturva*.
