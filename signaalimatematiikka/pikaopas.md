---
title: Kompleksiluvut ja Fourier-analyysi
subtitle: Pikaopas · kaavat, parit ja NumPy
---

# Kompleksiluvut

| Asia | Kaava | Python |
|------|-------|--------|
| luku | $z = a + bi = re^{i\varphi}$ | `complex(a, b)`, `3 + 4j` |
| osat | $\operatorname{Re} z = a$, $\operatorname{Im} z = b$ | `z.real`, `z.imag` |
| itseisarvo | $\lvert z\rvert = \sqrt{a^2 + b^2} = \sqrt{z\bar z}$ | `abs(z)`, `numpy.abs` |
| kulma | $\varphi = \operatorname{atan2}(b, a) \in (-\pi, \pi]$ | `cmath.phase`, `numpy.angle` |
| liittoluku | $\bar z = a - bi$ | `z.conjugate()`, `numpy.conj` |
| jakolasku | $z/w = z\bar w / \lvert w\rvert^2$ | `z / w` |
| napaesitys | $(r, \varphi)$ | `cmath.polar`, `cmath.rect` |
| tulo | $r_1 r_2 e^{i(\varphi_1 + \varphi_2)}$: kierto ja skaalaus | |

# Eulerin kaava

| Kaava | Muista |
|-------|--------|
| $e^{i\varphi} = \cos\varphi + i\sin\varphi$ | yksikköympyrä, $e^{i\pi} = -1$ |
| $\cos\varphi = (e^{i\varphi} + e^{-i\varphi})/2$ | kaksi vastakkain pyörivää nuolta |
| $\sin\varphi = (e^{i\varphi} - e^{-i\varphi})/(2i)$ | |
| $(e^{ix})^n = e^{inx}$ | de Moivre |
| $w_k = e^{2\pi ik/N}$ | ykkösen juuret; $\sum_k w_k^m = N$ tai $0$ |
| $\frac{d}{dt}e^{2\pi ift} = 2\pi i f\,e^{2\pi ift}$ | derivointi on kertolasku |

# Signaalit ja teho

| Suure | Kaava |
|-------|-------|
| sinimuotoinen signaali | $A\cos(2\pi ft + \varphi) = \operatorname{Re}(Xe^{2\pi ift})$, $X = Ae^{i\varphi}$ |
| jakso, kulmataajuus | $T = 1/f$, $\omega = 2\pi f$ |
| osoittimen mittaus | $X = 2\cdot\operatorname{mean}(x\,e^{-2\pi ift})$ kokonaisten jaksojen yli |
| interferenssi | $\lvert 1 + e^{i\delta}\rvert = 2\lvert\cos(\delta/2)\rvert$ |
| huojunta | taajuus $\lvert f_2 - f_1\rvert$ |
| teho | $P = \operatorname{mean}\lvert x\rvert^2$; sinille $A^2/2$ |
| tehollisarvo | $\sqrt P$; sinille $A/\sqrt2$ |
| desibelit | $10\log_{10}(P/P_0) = 20\log_{10}(A/A_0)$ |
| geometrinen summa | $\sum_{k=0}^{n-1} r^k = (1 - r^n)/(1 - r)$ |
| Dirichlet'n ydin | $\sum_{k=-N}^{N} e^{ikx} = \sin((N+\frac12)x)/\sin(x/2)$ |

# Fourier-sarja (jakso $2\pi$)

| Asia | Kaava |
|------|-------|
| sarja | $x(t) = \sum_k c_k e^{ikt}$ |
| kerroin | $c_k = \frac1{2\pi}\int_0^{2\pi} x(t)e^{-ikt}dt = \langle x, e_k\rangle$ |
| reaalinen muoto | $a_k = 2\operatorname{Re}c_k$, $b_k = -2\operatorname{Im}c_k$, amplitudi $2\lvert c_k\rvert$ |
| Parseval | $\frac1{2\pi}\int\lvert x\rvert^2 = \sum_k \lvert c_k\rvert^2$ |
| kanttiaalto | $\frac4\pi(\sin t + \frac13\sin 3t + \frac15\sin 5t + \cdots)$ |
| saha-aalto $(t - \pi)/\pi$ | $b_k = -2/(\pi k)$ |
| sileys | hyppy $1/k$, kulma $1/k^2$ |
| Gibbs | ylitys $\to \frac2\pi\operatorname{Si}(\pi) - 1 \approx 0.179$, eli 8.95 % hypystä |

# Fourier-muunnos

| Signaali | Muunnos |
|----------|---------|
| $x(t)$ | $X(f) = \int x(t)e^{-2\pi ift}dt$ |
| $\operatorname{rect}(t)$ | $\operatorname{sinc} f = \sin(\pi f)/(\pi f)$ |
| $e^{-\pi t^2}$ | $e^{-\pi f^2}$ |
| $e^{-\lvert t\rvert}$ | $2/(1 + 4\pi^2f^2)$ |
| $\max(0, 1 - \lvert t\rvert)$ | $\operatorname{sinc}^2 f$ |
| $x(t - t_0)$ | $e^{-2\pi ift_0}X(f)$ |
| $x(t)e^{2\pi if_0t}$ | $X(f - f_0)$ |
| $x(at)$ | $X(f/a)/\lvert a\rvert$ |
| $x'(t)$ | $2\pi if\,X(f)$ |
| $(x * h)(t)$ | $X(f)H(f)$ |

Epätarkkuus: $\sigma_t\sigma_f \ge 1/(4\pi)$, yhtäsuuruus Gaussin pulssille.

# Konvoluutio

| Asia | Muista |
|------|--------|
| määritelmä | $y[n] = \sum_k x[k]h[n-k]$, pituus $N_x + N_h - 1$ |
| impulssivaste | $h$ = vaste yksittäiseen ykkösnäytteeseen |
| liukuva keskiarvo | kohina $\sigma/\sqrt M$, $\lvert H\rvert = \lvert\sin(\pi fM)/(M\sin\pi f)\rvert$ |
| syklinen | `ifft(fft(x) * fft(h))` |
| lineaarinen FFT:llä | täytä nollilla: `fft(x, n=L)`, $L \ge N_x + N_h - 1$ |
| NumPy | `numpy.convolve(x, h, mode="full" / "same" / "valid")` |

# DFT ja FFT

| Asia | Kaava tai funktio |
|------|-------------------|
| DFT | $X[k] = \sum_n x[n]e^{-2\pi ikn/N}$, `numpy.fft.fft` |
| käänteinen | $x[n] = \frac1N\sum_k X[k]e^{2\pi ikn/N}$, `numpy.fft.ifft` |
| matriisi | $F_{kn} = e^{-2\pi ikn/N}$, $F^HF = NI$ |
| Parseval | $\sum\lvert x[n]\rvert^2 = \frac1N\sum\lvert X[k]\rvert^2$ |
| taajuudet | $kf_s/N$, `fftfreq(N, d=1/fs)`, `fftshift` |
| reaalinen signaali | $X[N-k] = \overline{X[k]}$, `rfft`, `rfftfreq` |
| sinin amplitudi | $2\lvert X[k]\rvert/N$ |
| jatkuva muunnos | `fftshift(fft(ifftshift(x))) * dt` |
| FFT | $X[k] = E[k] + w_N^kO[k]$, $X[k + N/2] = E[k] - w_N^kO[k]$ |
| työmäärä | DFT $N^2$, FFT $\frac N2\log_2 N$ kertolaskua |
