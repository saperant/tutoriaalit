---
title: Oheislaiteväylät
subtitle: Pikaopas · UART, SPI, I2C, CAN, DMA ja ajurit
---

# Väylät

| Väylä | Johtimet | Kello | Osoitus | Tarkistus |
|-------|----------|-------|---------|-----------|
| UART | TX, RX (RTS, CTS) | ei, sovittu nopeus | ei | pariteetti |
| SPI | SCK, MOSI, MISO, CS | isäntä | CS-johdin | ei |
| I2C | SCL, SDA (avokoll.) | isäntä, venytys | 7 bittiä | ACK |
| CAN | CANH, CANL | ei, reunat | tunniste = prioriteetti | CRC-15, ACK |

Vetovastus: $R_{min} = (V_{DD} - V_{OL}) / I_{OL}$,
$R_{max} = t_r / (0{,}847\,C_b)$. I2C: $t_r$ 1000 / 300 / 120 ns
(100 k / 400 k / 1 M), $I_{OL}$ 3 mA (Fm+: 20 mA).
RS-485 ja CAN: päätevastus 120 Ω molemmissa päissä.

# UART

Lepo 1, START 0, databitit LSB ensin, pariteetti, STOP 1. 8N1.
Jakaja: klassinen `kello / (16 · nopeus)`, CMSDK `kello / nopeus`.
Sieto 8N1, 16×: noin ±4,5 % yhteensä; pidä kumpikin pää < 2 %.

  Virhe          Syy
  -------------- ----------------------------------------
  pariteetti     häiriö, väärä muoto
  kehys          STOP = 0: väärä nopeus, katko (break)
  ylivuoto       ohjelma ei ehtinyt lukea
  -------------- ----------------------------------------

- Keskeytyslähetys: salli TXINTEN, kirjoita 1. tavu itse,
  kriittisessä osiossa.
- Vastaanotto: kuittaa, tyhjennä renkaaseen; täysi rengas →
  vuonohjaus (RTS, lukemisen keskeytys).
- Kehys: `COBS(data + CRC16) + 0x00`; NAK syykoodilla. 
  CRC-16/CCITT-FALSE: polynomi `0x1021`, alku `0xFFFF`, tarkiste
  `0x29B1`.
- RS-485: DE pois vasta TX complete -tilassa.

# SPI

  Moodi   CPOL   CPHA   Näyte      Siirto
  ------- ------ ------ ---------- ----------
  0       0      0      nouseva    laskeva
  1       0      1      laskeva    nouseva
  2       1      0      laskeva    nouseva
  3       1      1      nouseva    laskeva
  ------- ------ ------ ---------- ----------

Väärä moodi: data bitin myöhässä (`0x3C` → `0x9E`). CS = transaktion
raja; nosta vasta kun BSY = 0. PL022:
$f = f_{clk} / (\mathrm{CPSDVSR} (1 + \mathrm{SCR}))$, CPSDVSR
parillinen 2–254. FIFO 8: enintään 8 kehystä matkalla.

  Flash   Komento
  ------- --------------------------------------------
  `9F`    tunniste (valmistaja, tyyppi, koko)
  `05`    tila: bitti 0 WIP, bitti 1 WEL
  `06`    WREN ennen jokaista PP/SE
  `02`    PP: osoite 24 b + ≤ 256 tavua, kiertää sivulla
  `20`    SE: 4 KiB → `0xFF`
  `03`    READ: osoite 24 b, jatkuva luku
  ------- --------------------------------------------

# I2C

`S osoite+W A reg A Sr osoite+R A data A … data N P`. START/STOP:
SDA muuttuu SCL:n ollessa ylhäällä; muuten data muuttuu vain SCL:n
ollessa alhaalla. Varatut osoitteet `00–07`, `78–7F`.

- Venytys: odota SCL:n nousua, aikaraja (SMBus 35 ms).
- Arbitraatio: lähetä 1, näe 0 → hävisit, vapauta.
- Jumiutunut SDA: ≤ 9 kellojaksoa, sitten STOP; alustuksessa.
- EEPROM: kirjoitus sivun rajoilla, ACK-kysely kirjoitusjakson ajan.
- Rajapinta: `siirto(väylä, osoite, kirjoitus, n, luku, m)`; tulos
  OK, NACK osoite, NACK data, jumissa, aikaraja.

# CAN

`SOF ID(11) RTR IDE r0 DLC(4) DATA(0–64) CRC(15) | erotin ACK erotin
EOF(7)`. 0 dominantti, 1 resessiivinen. Täyttö: 5 samaa → vastakkainen.

  Laskuri          Tapahtuma               Muutos
  ---------------- ----------------------- --------
  TEC              lähetysvirhe            +8
  TEC              onnistunut lähetys      −1
  REC              vastaanottovirhe        +1
  REC              onnistunut vastaanotto  −1
  ---------------- ----------------------- --------

≥ 128: error passive, TEC > 255: bus-off, paluu 128 × 11 resessiivistä.
Ajoitus: `bitti = (1 + TSEG1 + TSEG2) TQ`, näytepiste ≈ 87,5 %.
Väylän pituus: ~40 m @ 1 Mbit/s, ~100 m @ 500 k, ~500 m @ 125 k.

# DMA

- Määrä leveyden yksiköissä, ei tavuina.
- DSB ennen käynnistystä; valmistumisen jälkeen aita tai `volatile`.
- Välimuisti: clean ennen lähetystä, invalidate ennen luettua dataa,
  puskurit 32 tavun rajalle ja rivin monikerraksi.
- Puskuri elää koko siirron; kuittaa tilabitit; käsittele virhe.

```{.c tiedosto="esimerkit/07-dma/main.c" osa="kaynnista"}
```

# Ajurit

Rekisterit → väyläohjain → väylärajapinta → laiteajuri → sovellus.
Rajapinta funktio-osoittimena, toteutus upottaa sen ensimmäiseksi.
Isäntätesti: laiteajuri mallia vastaan, ohjain muistisivua vastaan,
sanitoijat päälle. Jokainen odotus rajattu, virhe käännetään
kerroksen kielelle eikä sitä niellä.

QEMU-laboratorio:

```{.make tiedosto="esimerkit/Makefile" osa="laitteet"}
```
