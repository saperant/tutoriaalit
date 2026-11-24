---
title: Digitaalinen signaalinkäsittely
subtitle: Pikaopas · suunnittelu, toteutus ja testaus
---

# Vaatimukset ja toleranssit

| Asia | Kaava tai sääntö |
|------|------------------|
| poikkeamat | $\delta_p = (10^{R_p/20}-1)/(10^{R_p/20}+1)$, $\delta_s = 10^{-A_s/20}$ |
| tarkistus | `freqz`/`sosfreqz` tiheällä hilalla, palauta rikkeet listana |
| vertailu | $\max\lvert a-b\rvert / \max\lvert b\rvert$; ei pelkkää `rtol`:ia |
| toleranssit | FIR, FFT $10^{-12}$; IIR $10^{-10}$; NLMS $10^{-9}$; Q15 bitilleen |
| bitilleen | sama koodi lohkoittain ja kerralla |

# FIR

| Asia | Kaava tai sääntö |
|------|------------------|
| ikkunat | suorakaide 21 dB, Hann 44, Hamming 54, Blackman 75 |
| Kaiser $\beta$ | $A > 50$: $0{,}1102(A - 8{,}7)$ |
| Kaiser $N$ | $(A - 7{,}95)/(2{,}285 \cdot 2\pi\,\Delta f) + 1$, $\Delta f$ / $f_s$ |
| Parks–McClellan | paino $\delta_p/\delta_s$; $N \approx \frac{-20\log\sqrt{\delta_p\delta_s} - 13}{14{,}6\,\Delta f}$ |
| tyypit | I kaikki; II ei ylipäästöä; III ei ali/yli; IV ei alipäästöä |
| viive | $(N-1)/2$ näytettä; symmetria puolittaa kertolaskut |

```{.python tiedosto="esimerkit/pikaopas.py" osa="fir"}
```

# IIR

| Asia | Kaava tai sääntö |
|------|------------------|
| perheet | Butterworth tasainen; Chebyshev I/II aaltoilee päästö/esto; elliptinen pienin aste |
| bilineaari | $s = 2f_s\frac{1-z^{-1}}{1+z^{-1}}$; $\Omega = 2 f_s \tan(\omega/2)$ |
| esivääristys | $\Omega_c = 2 f_s \tan(\pi f_c / f_s)$ |
| rakenne | aina toisen asteen lohkot; DF2T liukuluku, DF1 kiinteä pilkku |
| RBJ-alipäästö | $\alpha = \sin\omega_0/2Q$; $b = \frac{1-\cos\omega_0}{2}[1, 2, 1]$, $a = [1+\alpha, -2\cos\omega_0, 1-\alpha]$ |
| Butterworth 4 | kaksi lohkoa, $Q = 0{,}5412$ ja $1{,}3066$ |
| kvantisointi | Q2.14 askel $6\cdot10^{-5}$; pieni $f_c/f_s$ vaatii bittejä |
| rajasykli | pyöristys jättää värähtelyn; itseisarvon katkaisu poistaa |

```{.python tiedosto="esimerkit/pikaopas.py" osa="iir"}
```

```{.c tiedosto="esimerkit/07-biquad/biquad.c" osa="df2t"}
```

```{.python tiedosto="esimerkit/pikaopas.py" osa="tarkista"}
```

# FFT ja spektri

| Asia | Kaava tai sääntö |
|------|------------------|
| radix-2 | $(N/2)\log_2 N$ kompleksikertolaskua; $N^2$ suoraan |
| perhonen | $X[k] = E + W^k O$, $X[k+N/2] = E - W^k O$ |
| testit | sini biniin, Parseval, paluu, suora DFT |
| overlap-save | $L = N - M + 1$; heitä $M - 1$ ensimmäistä; $N \approx 4M$ |
| Goertzel | 1 kertolasku/näyte/bin; voittaa, kun binejä alle $2\log_2 N$ |

# Monitaajuus

| Asia | Kaava tai sääntö |
|------|------------------|
| desimointi $M$ | suodata rajaan $f_s/2M$ ensin; $N/M$ kertolaskua/syöte |
| interpolointi $L$ | nollat + suodin, vahvistus $L$; $N$ kertolaskua/syöte |
| rationaalinen | $L/M$ supistettuna; suodin alemman Nyquistin mukaan |
| CIC | vaste $\lvert\sin(\pi fR)/\sin(\pi f)\rvert^N$; DC $R^N$; $B + N\log_2 R$ bittiä |

```{.python tiedosto="esimerkit/pikaopas.py" osa="monitaajuus"}
```

# Adaptiiviset suotimet

| Asia | Kaava tai sääntö |
|------|------------------|
| LMS | $\mathbf{w} \mathrel{+}= \mu e \mathbf{x}$; raja $\mu < 2/(N\sigma_x^2)$ |
| NLMS | $\mathbf{w} \mathrel{+}= \frac{\mu}{\varepsilon + \lVert\mathbf{x}\rVert^2} e \mathbf{x}$, $0 < \mu < 2$ |
| jäännösvirhe | noin $\mu N \sigma_x^2/2$ kertaa kohinan teho |
| häiriönpoisto | $x$ = viite, $d$ = mittaus, ulostulo $e$ |

# Reaaliaika C:llä

| Asia | Sääntö |
|------|------------------|
| muisti | tila oliossa, muisti kutsujalta, ei `malloc`:ia |
| rengas | kaksoiskirjoitus: $2N$ puskuri, sisäsilmukka ilman jakojäännöstä |
| jono | yksi tuottaja ja kuluttaja; atomiset indeksit, acquire/release |
| Q15 | kertymä 64 bittiä, pyöristys $+2^{14} \gg 15$, saturaatio, laske saturaatiot |
| latenssi | esitäyttö + lohko + ryhmäviive (+ muuntimet) |
| budjetti | MAC/näyte × $f_s$ pahimman tapauksen mukaan |

```{.c tiedosto="esimerkit/05-fir/fir.c" osa="tyonna"}
```

# Testaus

```{.python tiedosto="esimerkit/vertailu/mallit.py" osa="vertaa"}
```

```{.python tiedosto="esimerkit/vertailu/test_vertailu.py" osa="sos"}
```
