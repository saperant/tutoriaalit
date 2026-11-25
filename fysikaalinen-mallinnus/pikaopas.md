---
title: Fysikaalinen mallinnus ja simulointi
subtitle: Pikaopas · mallit, menetelmät, rajat ja tarkistukset
---

# Mallin ketju

| Vaihe | Kysymys | Tarkistus |
|-------|---------|-----------|
| tase + aineen laki | mikä säilyy, mitä reunan läpi kulkee | käsilasku, yksiköt |
| yhtälö + reunaehdot | mitä oletetaan | dimensiottomat luvut |
| diskretointi | hila vai verkko, mikä kertaluku | kertaluvun mittaus |
| ratkaisu | suora vai iteratiivinen, mikä askel | tase, symmetria |
| tulos | kuinka suuri virhe | kolme verkkoa, mittaus |

# Yhtälöt

| Tyyppi | Yhtälö | Luonne |
|--------|--------|--------|
| elliptinen | $-\nabla\cdot(k\nabla u) = s$ | tasapaino, yksi yhtälöryhmä |
| parabolinen | $\rho c\,u_t = \nabla\cdot(k\nabla u) + s$ | tasoittuu, jäykkä |
| hyperbolinen | $u_{tt} = c^2\nabla^2 u$ | etenee, energia säilyy |

| Reunaehto | Muoto | Merkitys |
|-----------|-------|----------|
| Dirichlet (oleellinen) | $u = g$ | lämpötila, tuki |
| Neumann (luonnollinen) | $-k\,\partial_n u = q$ | vuo, kuorma; 0 = eriste, symmetria, vapaa |
| Robin | $-k\,\partial_n u = h(u - T_\infty)$ | konvektio, jousituki |

# Dimensiottomat luvut

| Luku | Kaava | Käyttö |
|------|-------|--------|
| Fourier | $\mathrm{Fo} = \alpha t/L^2$ | tasoittunut, kun $\mathrm{Fo} \sim 1$; aika $\propto L^2$ |
| Biot | $\mathrm{Bi} = hL/k$ | $< 0{,}1$: yksi lämpötila riittää |
| hilan Fourier | $r = \alpha\,\Delta t/h^2$ | eksplisiittinen: $r \le \tfrac12$ (2D $\tfrac14$) |
| Courant | $C = c\,\Delta t/h$ | $C \le 1$ (2D $1/\sqrt2$) |

# Differenssimenetelmä

| Asia | Sääntö |
|------|--------|
| toinen differenssi | $(u_{i-1} - 2u_i + u_{i+1})/h^2$, virhe $O(h^2)$ |
| vaihteleva $k$ | diskretoi vuo; rajapinnalla $2k_1k_2/(k_1 + k_2)$ |
| vuoreuna | haamupiste $u_{n+1} = u_{n-1} + \dots$; ei toispuoleista erotusta |
| 2D | viiden pisteen kaava, matriisi `kron`illa, `spsolve` |
| lämpö ajassa | theta-menetelmä: 1 = impl. Euler, ½ = Crank–Nicolson |
| epäjatkuva alku | ensin impl. Euler, sitten Crank–Nicolson |
| aalto | $u^{n+1} = 2u^n - u^{n-1} + C^2\delta^2 u^n$; noin 10 väliä / aallonpituus |

```{.python tiedosto="esimerkit/04-ftcs.py" osa="askel"}
```

# Elementtimenetelmä

| Asia | Sääntö |
|------|--------|
| heikko muoto | kerro $v$:llä, integroi, siirrä derivaatta: $\int k\nabla u\cdot\nabla v = \int s v + \int_{\partial} q v$ |
| 1D-elementti | $\frac{EA}{h}\begin{pmatrix}1&-1\\-1&1\end{pmatrix}$ |
| kolmio | $K^e_{ij} = kA\,\nabla\varphi_i\cdot\nabla\varphi_j$, gradientit vakioita |
| kokoaminen | silmukka elementeistä, lisää paikallinen globaaliin |
| virhe (P1, sileä) | $L^2$: $h^2$; energia (vuo, jännitys): $h$ |
| aste $p$ | $L^2$: $h^{p+1}$, jos ratkaisu on sileä |
| sisänurkka | kertaluku putoaa; huippuarvo ei suppene |
| massa | konsistentti (implisiittinen), keskitetty (eksplisiittinen) |
| ominaisarvot | $Kv = \omega^2 Mv$; `eigsh(K, M=M, sigma=0)` |
| elastisuus | toisen asteen elementit; P1 lukkiutuu taivutuksessa |

# Verkko ja ratkaisija

| Asia | Sääntö |
|------|--------|
| kolmion muoto | vältä suuria kulmia; pieni kulma yksin ei haittaa |
| tihennys | nurkat, reiät, kuormien reunat; koko muuttuu vähitellen |
| singulariteetti $r^{2/3}$ | $h \le H\sqrt r$ palauttaa kertaluvun |
| suora ratkaisija | 2D satoihintuhansiin; täyttö riippuu järjestyksestä |
| liittogradientti | kierrokset $\propto 1/h$; esiehdostin tai monihila |
| aika-askel | hajota matriisi kerran, `splu(...).solve` |

```{.python tiedosto="esimerkit/08-kirjasto.py" osa="ratkaisu"}
```

# Tarkistukset

| Tarkistus | Löytää |
|-----------|--------|
| kertaluku tarkkaa ratkaisua vasten | diskretoinnin ja reunaehdon virheet |
| tase: sisään − ulos = varasto | puuttuvat termit, reunajoukot, yksiköt |
| paikkatesti (lineaarinen ratkaisu) | elementtimatriisin ja numeroinnin |
| valmistettu ratkaisu | minkä tahansa termin virheen |
| kolme verkkoa: $p = \log_2\frac{Q_2 - Q_1}{Q_3 - Q_2}$ | virheen suuruuden, singulaarisen suureen |
| GCI $= 1{,}25\,\lvert Q_3 - Q_2\rvert / (\lvert Q_3\rvert (2^p - 1))$ | raportoitava virhearvio |
| ennuste uudessa tilanteessa | mallin muodon virheen |

Kalibrointi ja validointi eri aineistoilla. Verifioi ennen kuin
validoit. Ilmoita tulos, virhearvio ja oletukset yhdessä.
