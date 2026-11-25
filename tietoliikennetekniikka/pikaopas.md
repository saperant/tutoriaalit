---
title: Tietoliikennetekniikka
subtitle: Pikaopas · kaavat, nyrkkisäännöt ja tunnusluvut
---

# Desibelit

| dB | tehokerroin | | dBm | teho |
|----|-------------|-|-----|------|
| +3 | ×2 | | 0 | 1 mW |
| +10 | ×10 | | 20 | 100 mW |
| +20 | ×100 | | 30 | 1 W |
| −3 | ×0,5 | | −90 | 1 pW |

Ketju lasketaan summana. Tehot summataan milliwatteina, ei
desibeleinä. Jännitesuhde: $20 \log_{10}$.

# Kaavat

| Suure | Kaava |
|-------|-------|
| Shannon | $C = B \log_2(1 + S/N)$ |
| Nyquist | $C = 2B \log_2 M$ |
| vapaan tilan vaimennus | $20 \log_{10}(4\pi d f / c)$ |
| kohinataso | $-174 + 10 \log_{10} B + NF$ dBm |
| linkin SNR | $P_t + G - L$ − kohinataso |
| siirtoviive | koko / nopeus |
| etenemisviive | matka / (2·10⁸ m/s) kuidussa |
| BDP | kaista × kierrosaika |
| ALOHA | puhdas $G e^{-2G}$ (max 18 %), viipaloitu $G e^{-G}$ (max 37 %) |
| ARQ, kierros $k$ kehystä | go-back-N $(1-p)/(1+kp)$, valikoiva $1-p$ |
| M/M/1 | $W = 1/(\mu - \lambda)$, $L = \rho/(1-\rho)$ |
| Little | $L = \lambda W$ |
| NR-numerologia | väli $15 \cdot 2^\mu$ kHz, aikaväli $1/2^\mu$ ms |

```{.python tiedosto="esimerkit/pikaopas.py" osa="kaavat"}
```

```{.tuloste tiedosto="esimerkit/pikaopas.odotettu"}
```

# Siirtotiet

| Siirtotie | Kantama | Raja |
|-----------|---------|------|
| kierretty pari | 100 m | vaimennus $\propto \sqrt{f}$, ylikuuluminen |
| monimuotokuitu | 100–500 m | muotodispersio |
| yksimuotokuitu | 10–80 km | 0,2–0,35 dB/km, kromaattinen dispersio |
| radio | m – km | etäisyyden neliö, häipymä, häiriöt |

# Linjakoodit ja virheet

| Koodi | Hinta | Missä |
|-------|-------|-------|
| Manchester | 100 % | 10BASE-T |
| 4B5B | 25 % | 100BASE-X |
| 8b10b | 25 % | 1000BASE-X, PCIe 1–2 |
| 64b/66b | 3 % | 10G ja nopeammat |
| PAM4 | 2 bittiä/symboli, −9,5 dB | 50G+ |

CRC-32: kaikki purskeet ≤ 32 bittiä. Hamming(7,4): korjaa yhden
virheen. Lomitus hajottaa purskeet. CRC ei suojaa tahalliselta
muokkaukselta.

# Kanavanvaraus ja kytkentä

- Piirikytkentä: varattu kaista, vakio viive. Pakettikytkentä:
  tilastollinen jako, best-effort.
- CSMA/CD: kuuntele, havaitse törmäys, perääntyminen $0 \ldots 2^k-1$.
- CSMA/CA: odota ja kuittaa; RTS/CTS piilotetulle asemalle.
- TDMA ja vuoromerkki: rajattu viive, tyhjät vuorot hukkaan.

# Ethernet

Yleiskustannus 38 tavua kehystä kohti; 64 tavun kehyksillä
14,88 milj. kehystä/s @ 10 Gbit/s. Vähimmäiskoko 64 tavua = 512 bitin
aikaviipale. Anna molempien päiden neuvotella nopeus ja dupleksi.

# Jonot ja QoS

Viive $\propto 1/(1-\rho)$: 50 % → 2×, 90 % → 10×, 99 % → 100×.
Prioriteetti puheelle (EF), rajattu osuus. Rahakkeen ämpäri:
keskinopeus + purskeen koko. DSCP-merkinnät vain omassa verkossa.
