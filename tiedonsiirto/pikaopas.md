---
title: Digitaalinen tiedonsiirto
subtitle: Pikaopas · kaavat, nyrkkisäännöt ja Python
---

# Signaalit ja modulaatiot

| Asia | Kaava tai sääntö |
|------|------------------|
| kantataajuus | $s = \operatorname{Re}\{(I + iQ)e^{i2\pi f_c t}\}$ |
| sekoitus alas | $2s\,e^{-i2\pi f_c t}$ + alipäästö |
| AM | $(1 + \mu m)\cos$; verhokäyrä vaatii $\mu \le 1$ |
| FM | $\beta = \Delta f/f_m$; Carson $2(\Delta f + f_m)$ |
| FM-ilmaisu | $\arg(z[n]\,z^*[n-1])\,f_s/2\pi$ |
| $M$-PSK, QAM | $k = \log_2 M$ bittiä/symboli, Gray-nimiöt |
| FSK | ortogonaalinen: $\Delta f = 1/(2T)$ koherentti, $1/T$ ei |
| MSK | CPFSK, $\Delta f T = 1/2$, vakioamplitudi |

# Pulssit ja suodatus

| Asia | Kaava tai sääntö |
|------|------------------|
| Nyquist | $p(kT) = 0$, kun $k \ne 0$ |
| RC-kaista | $(1+\beta)/(2T)$ |
| RRC + RRC | = RC; vastaanoton RRC on sovitettu suodin |
| sovitettu suodin | $g(t) = p^*(-t)$; SNR $= E_s/N_0$ |
| energia | $\sum h^2 = 1$: lähtö = symboli, kohina $N_0$ |
| silmäkuvio | aukeama < 0: silmä kiinni |

# Kohina ja virheet

| Asia | Kaava tai sääntö |
|------|------------------|
| energiat | $E_s = k E_b$; koodattuna koodibitti $R E_b$ |
| SNR/näyte | $E_s/N_0 - 10\log_{10}\text{sps}$ |
| EVM | $E_s/N_0 \approx -20\log_{10}\text{EVM}$ |
| BPSK, QPSK | $Q(\sqrt{2E_b/N_0})$ |
| $M$-QAM | $\frac4k(1-\frac1{\sqrt M})Q(\sqrt{3kE_b/N_0/(M-1)})$ |
| $M$-PSK | $\frac2k Q(\sqrt{2kE_b/N_0}\sin\frac\pi M)$ |
| Rayleigh | $\frac12(1-\sqrt{\gamma/(1+\gamma)})$ |
| Shannon | $E_b/N_0 > (2^\eta-1)/\eta$, raja $-1{,}59$ dB |
| PER | $1 - (1 - P_b)^n$ |
| luotettavuus | suhteellinen virhe $\approx 1/\sqrt{N_e}$ |

# Synkronointi ja koodaus

| Asia | Kaava tai sääntö |
|------|------------------|
| taajuusvirhe | $360\,\Delta f/R_s$ astetta symbolia kohti |
| Costas (QPSK) | $e = \operatorname{sign}(I)Q - \operatorname{sign}(Q)I$ |
| 2. asteen silmukka | PI + NCO; ei pysyvää virhettä |
| Gardner | $e = \operatorname{Re}\{(y_k - y_{k-1})y^*_{k-1/2}\}$ |
| kehys | $\lvert\text{korrelaatio}\rvert$ / energia > kynnys |
| OFDM | IFFT, etuliite > viive, $Y[k]/H[k]$ |
| konvoluutiokoodi (7,5) | $R = 1/2$, 4 tilaa, $d_\text{free} = 5$ |
| koodausvahvistus | asymptoottisesti $10\log_{10}(R\,d_\text{free})$ |
| pehmeä päätös | noin 2 dB parempi kuin kova |

# Python: muunnokset

```{.python tiedosto="esimerkit/pikaopas.py" osa="muunnokset"}
```

# Python: kohina ja BER

```{.python tiedosto="esimerkit/pikaopas.py" osa="kohina"}
```

```{.python tiedosto="esimerkit/pikaopas.py" osa="ber"}
```

```{.tuloste tiedosto="esimerkit/pikaopas.odotettu"}
```
