---
title: Ohjelmistoradio
subtitle: Pikaopas · muodot, korjaukset, kanavan valinta ja vastaanottimet
---

# IQ-näytteet

| Asia | Sääntö |
|------|--------|
| kaista | kompleksinen $f_s$ kuvaa kaistan $f_c \pm f_s/2$ |
| cu8 | RTL-SDR, $(x - 127{,}5)/127{,}5$, 2 tavua/näyte |
| ci16_le | Pluto, USRP, $x/32767$, 4 tavua |
| cf32_le | GNU Radio, käsittely, 8 tavua |
| SigMF | `.sigmf-data` + `.sigmf-meta` (JSON) |
| SQNR | $6{,}02N + 1{,}76$ dB täydellä skaalalla |
| FFT-vahvistus | $10\log_{10} N_\text{FFT}$ kapealle signaalille |
| ylikuorma | leikkautuminen pilaa koko kaistan |

```{.python tiedosto="esimerkit/fm/vastaanotin.py" osa="lue"}
```

# Laitteen virheet

| Virhe | Korjaus |
|-------|---------|
| DC-piikki | $H(z) = (1 - z^{-1})/(1 - a z^{-1})$, $a = 0{,}999$; tai viritä ohi |
| IQ-epätasapaino | IRR $= \frac{1+2g\cos\varphi+g^2}{1-2g\cos\varphi+g^2}$; Gram–Schmidt |
| vahvistus | AGC: nopea isku, hidas palautus, dB-asteikko |
| kide | $\Delta f = f_c \cdot \text{ppm} \cdot 10^{-6}$ |
| taajuusarvio | FFT, nollatäyttö, paraabeli kolmeen binniin |

# Kanavan valinta

| Asia | Sääntö |
|------|--------|
| siirto | $x[n]\,e^{-i2\pi f_0 n/f_s}$ |
| NCO | askel $\text{round}(f_0/f_s \cdot 2^{32})$, resoluutio $f_s/2^{32}$ |
| NCO:n SFDR | noin $6{,}02 \times$ taulukon osoitebitit |
| FIR-pituus | $N \approx A/(22\,\Delta f/f_s)$ |
| desimointi | kustannus $\sum N_i / \prod_{j \le i} D_j$ |
| 1. vaiheen esto | $f_{s,1} - B_\text{lopullinen}$ |
| polyfaasi | $h_r[p] = h[pM + r]$, $y_k = \sum_r v_r e^{i2\pi kr/M}$ |

```{.python tiedosto="esimerkit/04-nco.py" osa="nco"}
```

# FM ja stereo

| Asia | Sääntö |
|------|--------|
| ilmaisin | $\arg(z[n] z^*[n-1]) \cdot f_s / (2\pi \Delta f)$ |
| vaste | $\text{sinc}(f/f_s)$: 38 kHz / 228 kS/s = −0,4 dB |
| kynnys | noin 10 dB CNR |
| SNR kynnyksen yllä | $1{,}5(\Delta f/W)^2 (B/W)\,\text{CNR}$ |
| jälkikorostus | $1/(1 + s\tau)$, $\tau = 50$ µs |
| MPX | 0–15 kHz summa, 19 kHz pilotti, 38 kHz erotus, 57 kHz RDS |
| stereo | $L = S + D$, $R = S - D$, sama suodin |
| PLL | $k_p = 2\zeta\omega_n T$, $k_i = (\omega_n T)^2$ |
| RDS | 1187,5 bit/s, differentiaali + kaksivaihe, 26 bitin lohkot |

```{.python tiedosto="esimerkit/fm/vastaanotin.py" osa="ilmaisin"}
```

# Paketit ja reaaliaika

| Asia | Sääntö |
|------|--------|
| GFSK | $h = 2\Delta f/R$; $BT = 0{,}5$ |
| haku | normitettu korrelaatio; kynnys kohinasta |
| taajuusvirhe | `1010…`-alkuosan ilmaisinlähdön keskiarvo |
| ajoitus | korrelaatiohuippu; lyhyt paketti ei liu'u |
| CRC-16/CCITT | poly 0x1021, alku 0xFFFF; "123456789" → 0x29B1 |
| ei-koherentti FSK | BER $\frac12 e^{-E_b/2N_0}$ |
| lohkot | tila säilyy, testaa lohkoittain = kerralla |
| herkkyys | $-174 + 10\log_{10}B + \text{NF} + \text{SNR}$ dBm |
| lähetys | radiolupa tai luvasta vapaan käytön ehdot (Traficom) |

```text
rtl_sdr -f 98000000 -s 912000 -g 20 tallenne.cu8
rtl_sdr -f 98000000 -s 912000 - | ./ketju --suodin 200000 > mpx.f32
```
