---
title: Differentiaaliyhtälöt ja Laplace-muunnos
subtitle: Pikaopas · mallit, ratkaisut, SymPy, SciPy, Maxima ja Octave
---

# Mallit ja ensimmäinen kertaluku

| Asia | Kaava tai komento |
|------|-------------------|
| tase | muutos = sisään − ulos |
| 1. kertaluvun malli | $\tau y' + y = y_\infty$, $y = y_\infty + (y_0 - y_\infty)e^{-t/\tau}$ |
| asettuminen | 63 % yhdessä, 95 % kolmessa, 99 % viidessä aikavakiossa |
| logistinen | $N' = rN(1 - N/K)$, käännepiste $K/2$, suurin kasvu $rK/4$ |
| separoituva | $\int dy/h(y) = \int g(t)\,dt + C$ |
| lineaarinen | $\mu = e^{\int p}$, $y = (\int \mu q + C)/\mu$ |
| tasapaino | $f(y^*) = 0$; stabiili, jos $f'(y^*) < 0$ |
| SymPy | `sp.dsolve(sp.Eq(y(t).diff(t), f), y(t), ics={y(0): y0})` |
| tarkistus | `sp.checkodesol(yhtalo, ratkaisu)` |
| Maxima | `ic1(ode2('diff(y, t) = f, y, t), t = 0, y = y0)` |

# Toinen kertaluku

| Asia | Kaava tai komento |
|:-----|:------------------|
| yhtälö | $my'' + cy' + ky = F(t)$ |
| ominaiskulmataajuus | $\omega_0 = \sqrt{k/m} = 1/\sqrt{LC}$ |
| vaimennussuhde | $\zeta = c/(2\sqrt{km}) = (R/2)\sqrt{C/L}$ |
| tapaukset | $\zeta < 1$ värähtelee, $= 1$ kriittinen, $> 1$ hidas |
| resonanssi | huippu $\omega_0\sqrt{1 - 2\zeta^2}$, korkeus $\approx 1/(2\zeta)$ |
| ylitys | $e^{-\zeta\pi/\sqrt{1 - \zeta^2}}$, huippuhetki $\pi/\omega_d$ |
| Maxima | `ic2(ode2(...), t = 0, y = 1, 'diff(y, t) = 0)` |

# Tilaesitys ja stabiilisuus

| Asia | Kaava tai komento |
|------|-------------------|
| tilaesitys | $x_1 = y$, $x_2 = y'$, $\mathbf{x}' = A\mathbf{x}$ |
| ratkaisu | $\mathbf{x}(t) = e^{At}\mathbf{x}_0$; `scipy.linalg.expm`, Octave `expm` |
| satula | $\det A < 0$ |
| solmu / spiraali | $\det A > 0$, $\operatorname{tr}^2 \gtrless 4\det$; stabiili, jos $\operatorname{tr} A < 0$ |
| keskus | $\operatorname{tr} A = 0$, $\det A > 0$ |
| epälineaarinen | Jacobin matriisi tasapainossa: `f.jacobian([x1, x2])` |
| takaisinkytkentä | $T = KG/(1 + KG)$, navat: $1 + KG = 0$ |
| Routh–Hurwitz | merkinvaihdot 1. sarakkeessa = juuret oikealla |

# Laplace-muunnos

| $f(t)$ | $F(s)$ |
|--------|--------|
| $1$, $t$, $t^n$ | $1/s$, $1/s^2$, $n!/s^{n+1}$ |
| $e^{-at}$ | $1/(s + a)$ |
| $\sin\omega t$, $\cos\omega t$ | $\omega/(s^2 + \omega^2)$, $s/(s^2 + \omega^2)$ |
| $f'(t)$ | $sF - f(0)$ |
| $f''(t)$ | $s^2F - sf(0) - f'(0)$ |
| $e^{-at}f(t)$ | $F(s + a)$ |
| $f(t - T)u(t - T)$ | $e^{-sT}F(s)$ |
| $(f * g)(t)$ | $F\,G$ |
| alku- ja loppuarvo | $\lim_{s\to\infty} sF$, $\lim_{s\to 0} sF$ (navat vasemmalla) |

```{.python tiedosto="esimerkit/06-alkuarvo.py" osa="osamurrot"}
```

# Siirtofunktio

| Asia | Kaava tai komento |
|------|-------------------|
| siirtofunktio | $H = Y/U$ nollilla alkuehdoilla |
| SciPy | `signal.lti(osoittaja, nimittaja)`, `signal.step`, `signal.freqs` |
| taajuusvaste | $H(i\omega)$: amplitudi $\lvert H\rvert$, vaihe $\arg H$ |
| s ja z | $z = e^{sT}$; $\operatorname{Re} s < 0 \Leftrightarrow \lvert z\rvert < 1$ |
| Octave | `roots`, `residue`; `control`-paketti erikseen |

# Numeeriset ratkaisijat

| Tilanne | SciPy `solve_ivp` | Octave |
|---------|-------------------|--------|
| tavallinen | `method="RK45"`, `rtol=1e-6` | `ode45` |
| jäykkä | `"Radau"`, `"BDF"` | `ode15s`, `ode23s` |
| tuntematon | `"LSODA"` | `ode15s` |
| tapahtumat | `events=f`, `f.terminal = True` | `odeset("Events", f)` |

Euler on 1. kertaluvun, RK4 4. kertaluvun menetelmä. Eksplisiittinen
menetelmä on jäykälle yhtälölle vakaa vain, kun $h \lesssim 2/\lvert\lambda\rvert$.
