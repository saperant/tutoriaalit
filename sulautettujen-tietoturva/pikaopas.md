---
title: Sulautettujen järjestelmien tietoturva
subtitle: Pikaopas · luottamusketju, avaimet, päivitykset, fyysiset hyökkäykset
---

# Vastuulauseke

Mittaa, avaa ja häiritse vain omia laitteitasi tai kirjallisella
luvalla testattavia kohteita. Luvaton tunkeutuminen on rikos
(rikoslain 38. luku). Paketin hyökkäykset ovat simulaatioita.

# Uhkamalli

| Pääsy | Pinnat | Vastatoimi |
|-------|--------|------------|
| Etä | pilvi, päivityspalvelu | TLS, laitekohtainen identiteetti, allekirjoitetut kuvat |
| Lähi | BLE, Wi-Fi, web-UI | todennettu pariliitos, ei oletussalasanoja |
| Fyysinen | UART, SWD/JTAG, ulkoinen flash | lukitus, todennettu debug, salaus |
| Invasiivinen | häiriöt, tehonkulutus | kovennettu koodi, maskaus, tunnistimet |

Pääsääntö: yhden laitteen murto ei saa helpottaa muiden murtamista.

# Turvallinen käynnistys

- ROM → käynnistin → sovellus; jokainen vaihe tarkistaa seuraavan.
- Juuren julkinen avain tai sen tiiviste OTP:ssa; kumoamisbitit.
- Otsake: taikaluku, versio, koko, SHA-512(sovellus), Ed25519(otsake).
- Rajaa koko ennen tiivistystä; tarkista ja aja sama kopio.

```{.c tiedosto="esimerkit/laite/lahde/kaynnistin.c" osa="hyppy"}
```

```{.python tiedosto="esimerkit/03-kuvatyokalu.py" osa="kuva"}
```

# Versionpalautus

- Turvaversio ≠ julkaisuversio; nosta vain turvakorjauksissa.
- Monotoninen laskuri: OTP-termometri, TPM NV, RPMB, turvaelementti.
- Laskuri nostetaan vasta, kun uusi versio on vahvistettu.

# Mittaus ja todennus

| Vaihe | Toiminto |
|-------|----------|
| laite | PCR ← H(PCR ‖ H(seuraava vaihe)); tapahtumaloki |
| todentaja | haaste (nonce) |
| laite | allekirjoitus(nonce ‖ PCR) todennusavaimella |
| todentaja | tarkista allekirjoitus, toista loki, vertaa hyväksyttyihin |

# Avaimet

| Paikka | Huom. |
|--------|-------|
| flash | ei avaimille selväkielisenä |
| OTP/eFuse | muuttumaton, lukeminen rajattava |
| TrustZone-M/A | suojattu puoli, rajatut sisääntulot |
| turvaelementti, TPM | avain ei poistu piiristä |
| PUF | ei tallennettua avainta; sumea poimija |

- Laitekohtainen juuriavain (HUK), käyttökohtaiset avaimet HKDF:llä,
  käyttötarkoituksen nimessä versio.
- Luo avain laitteessa, varmenna julkinen avain tehtaalla.

# Päivitykset

- A/B-paikat tai varmistettu vaihto; kokeilukäynnistys + vahvistus.
- Manifesti ennen latausta: allekirjoitus, laitemalli, järjestysnumero,
  koko; latauksen jälkeen tiiviste.
- Delta: tarkista rakennetun kuvan tiiviste; väärä pohja → täysi kuva.
- Vaiheittainen julkaisu, seuraa vahvistuksia.

# Debug

| RDP | Debug | Flash | Lasku |
|-----|-------|-------|-------|
| 0 | täysi | luettava | – |
| 1 | rajattu | ei | pyyhkii flashin |
| 2 | pois | ei | ei mahdollinen |

- Todennettu debug: haaste ‖ sarjanumero allekirjoitetaan, kertakäyttö.
- UART pois tai todennettu; `bootdelay` nollaan.

# Sivukanavat ja viat

- Vakioaikainen vertailu kirjastosta (`crypto_verify16`,
  `mbedtls_ct_memcmp`, `sodium_memcmp`).
- CPA: korreloi H(S[p ⊕ arvaus]) mittauksiin; torjunta maskaus,
  sekoitus, suojattu laitteisto.
- Viat: käskyn ohitus, bittivirhe. Torjunta: vakiot (ei 0/1), oletus
  hylätty, tuplatarkistus `volatile`-muuttujilla, kulun laskuri,
  satunnaiset viiveet, jännite- ja kellotunnistimet.

```{.c tiedosto="esimerkit/09-vertailu.c" osa="vakioaikainen"}
```

# Sääntely

| Säädös | Sisältö |
|--------|---------|
| ETSI EN 303 645 | kuluttaja-IoT, 13 perusvaatimusta |
| EN 18031-1/2/3 | radiolaitteet, sovellettava 1.8.2025 |
| IEC 62443-4-1/-4-2 | kehitysprosessi; komponentit, SL 1–4 |
| CRA (EU) 2024/2847 | ilmoitukset 11.9.2026 alkaen, muu 11.12.2027 |

CRA-ilmoitus hyödynnetystä haavoittuvuudesta: varoitus 24 h,
ilmoitus 72 h, loppuraportti 14 vrk korjauksesta. Tukiaika vastaa
käyttöaikaa, vähintään 5 vuotta.

# Komennot

| Tehtävä | Komento |
|---------|---------|
| käännös | `arm-none-eabi-gcc -mcpu=cortex-m3 -mthumb -Os` |
| ajo | `qemu-system-arm -M mps2-an385 -nographic` |
| semihosting | `-semihosting-config enable=on,target=native` |
| kuva muistiin | `-device loader,file=k.bin,addr=0x00100000` |
| koko | `arm-none-eabi-size kaynnistin.elf` |
