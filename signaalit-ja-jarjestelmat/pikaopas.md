---
title: Signaalit ja järjestelmät
subtitle: Pikaopas · kaavat, säännöt ja SciPy
---

# Signaalit

| Asia | Kaava tai sääntö |
|------|------------------|
| impulssi, askel | $\delta[n]$, $u[n]$; $x[n] = \sum_k x[k]\delta[n-k]$ |
| energia | $E = \sum \lvert x[n]\rvert^2$; $a^n u[n]$: $1/(1-a^2)$ |
| teho | $P = \operatorname{mean}\lvert x\rvert^2$; sini $A^2/2$, askel $1/2$ |
| jaksollisuus | $\cos(2\pi f n)$ jaksollinen, jos $f = p/q$; jakso $q$ |
| monikäsitteisyys | $f$, $f + 1$ ja kosinille $1 - f$ samat; $\omega \in (-\pi, \pi]$ |
| normitettu taajuus | $\omega = 2\pi f/f_s$ rad/näyte; SciPyssä 1 = $f_s/2$ ilman `fs` |

# Näytteistys

| Asia | Kaava tai sääntö |
|------|------------------|
| Nyquist | $f_s > 2B$; Nyquistin taajuus $f_s/2$ |
| alias | $f \bmod f_s$, peilaus: $\min(r, f_s - r)$ |
| rekonstruktio | $x(t) = \sum_n x[n]\operatorname{sinc}(f_s t - n)$ |
| nollannen asteen pito | vaimennus $\lvert\operatorname{sinc}(f/f_s)\rvert$, $-3{,}9$ dB Nyquistilla |
| desimointi | suodatus + harvennus: `decimate(x, q)` |
| kvantisointi | SNR $\approx 6{,}02\,b + 1{,}76$ dB |

# LTI-järjestelmät

| Asia | Kaava tai sääntö |
|------|------------------|
| ulostulo | $y = x * h$, $h = T\{\delta\}$ |
| kausaalinen | $h[n] = 0$, kun $n < 0$ |
| BIBO-stabiili | $\sum \lvert h[n]\rvert < \infty$ |
| askelvaste | $s[n] = \sum_{k\le n} h[k]$ |
| differenssiyhtälö | $\sum_k a_k y[n-k] = \sum_k b_k x[n-k]$ |
| siirtofunktio | $H(z) = B(z)/A(z)$, kertoimet $z^{-k}$:n potensseina |
| stabiilisuus | kausaalinen: kaikki navat $\lvert p\rvert < 1$ |
| sarjaankytkentä | `convolve(b1, b2)`, `convolve(a1, a2)` |
| taajuusvaste | $H(e^{i\omega})$; $\lvert H\rvert$ = nollien / napojen etäisyydet |
| ryhmäviive | $-d\arg H/d\omega$; symmetrinen FIR: $(N-1)/2$ |
| EMA | $b = [\alpha]$, $a = [1, \alpha - 1]$, $\alpha = 1 - e^{-T_s/\tau}$ |
| resonaattori | $a = [1, -2r\cos\theta, r^2]$, navat $re^{\pm i\theta}$ |
| lovi | nollat $e^{\pm i\omega_0}$, navat $re^{\pm i\omega_0}$ |

# Spektri

| Asia | Kaava tai sääntö |
|------|------------------|
| resoluutio | $\Delta f = f_s/N = 1/$mittausaika |
| amplitudi | $A = 2\lvert X[k]\rvert/\sum w$ |
| ikkunat | suorakaide $-13$ dB, Hann $-31$ dB, Blackman $-58$ dB |
| nollilla täyttö | tihentää hilaa, ei erottelukykyä |
| PSD | valkoinen kohina $\sigma^2/(f_s/2)$; arvio Welchillä |
| FFT-konvoluutio | täyttö $\ge N_x + N_h - 1$; satoja kertoimia |
| STFT | lyhyt ikkuna: aika, pitkä ikkuna: taajuus |

# SciPy: suodatus

```{.python tiedosto="esimerkit/pikaopas.py" osa="suodatus"}
```

# SciPy: analyysi

```{.python tiedosto="esimerkit/pikaopas.py" osa="analyysi"}
```

# SciPy: spektri

```{.python tiedosto="esimerkit/pikaopas.py" osa="spektri"}
```

# Sudenkuopat

| Virhe | Korjaus |
|-------|---------|
| `x[::q]` | `decimate(x, q)` |
| normitettu taajuus luultiin hertseiksi | anna `fs=` kaikille funktioille |
| tila nollautuu lohkojen välillä | `lfilter(..., zi=tila)` |
| suuri tasataso, pitkä alkutransientti | `lfilter_zi(b, a) * x[0]` |
| korkea-asteinen `(b, a)` pyöristettynä | `output="sos"`, `sosfilt` |
| $a_0 \ne 1$ omassa toteutuksessa | jaa kertoimet $a_0$:lla |
| amplitudi jaettu $N$:llä ikkunan kanssa | jaa ikkunan summalla |
| yksi periodogrammi kohinasta | `welch(x, fs, nperseg)` |
| `assert np.allclose(...)` | `np.testing.assert_allclose` |
| tulosteessa $-0.00$ | `np.round(x, d) + 0.0` |
