---
title: Numeeriset menetelmät
subtitle: Pikaopas · virheet, kertaluvut, SciPy ja Octave
---

# Virheet

| Asia | Kaava tai sääntö |
|------|------------------|
| konetarkkuus | $\varepsilon = 2^{-52} \approx 2{,}2 \cdot 10^{-16}$, pyöristys $u = \varepsilon/2$ |
| ehtoluku | $\kappa_f = \lvert x f'(x)/f(x)\rvert$; menetetään $\log_{10}\kappa$ numeroa |
| eteen/taakse | eteenpäinvirhe $\lesssim \kappa \cdot$ taaksepäinvirhe |
| kumoutuminen | kirjoita uudelleen; `log1p`, `expm1`, `hypot` |
| varianssi | kaksi läpikäyntiä tai Welford, ei $\sum x^2 - n\bar x^2$ |
| summa | `math.fsum`, `np.sum` (parittainen), Kahan |
| rekursio | laske suuntaan, jossa virhe jaetaan |

# Yhtälöt

| Menetelmä | Kertaluku | Huomio |
|--------------|-------------------|--------------------------------------------------|
| puolitus | 1 (bitti/kierros) | varma, tarvitsee merkinvaihdon |
| kiintopiste | 1, kerroin $\lvert g'(x^*)\rvert$ | suppenee, jos kerroin $< 1$ |
| sekantti | 1,618 | ei derivaattaa |
| Newton | 2 | moninkertainen juuri: 1, korjaus askel $\times m$ |
| Brent | superlineaarinen | `optimize.brentq`, Octave `fzero` |
| ryhmä | 2 | $J\,\Delta x = -F$; `optimize.root`, `fsolve` |

Kertaluvun mittaus: $p \approx \log(e_{k+1}/e_k) / \log(e_k/e_{k-1})$.

# Interpolointi ja sovitus

| Asia | Sääntö tai komento |
|------|--------------------|
| virhe | $\frac{f^{(n+1)}(\xi)}{(n+1)!}\prod(x - x_i)$ |
| Tšebyšov | $x_k = \cos\frac{(2k+1)\pi}{2n+2}$; ei Rungen ilmiötä |
| polynomi | `BarycentricInterpolator`, `Chebyshev.fit` |
| splini | `CubicSpline`, virhe $O(h^4)$; `PchipInterpolator` |
| PNS | QR tai `lstsq`; $\kappa(A^TA) = \kappa(A)^2$ |
| Octave | `polyfit`, `interp1(..., "spline")`, `A \ y` |

# Derivointi ja integrointi

| Sääntö | Virhe | Paras askel |
|--------|-------|-------------|
| eteenpäin-erotus | $O(h)$ | $\sqrt\varepsilon \approx 10^{-8}$ |
| keskeinen erotus | $O(h^2)$ | $\varepsilon^{1/3} \approx 10^{-5}$ |
| Richardson | $O(h^4)$ | $(4D(h/2) - D(h))/3$ |
| kompleksiaskel | $O(h^2)$, ei kumoutumista | $10^{-100}$ kelpaa |
| puolisuunnikas | $O(h^2)$ | jaksollisille eksponentiaalinen |
| Simpson | $O(h^4)$ | |
| Gauss $n$ pistettä | tarkka asteelle $2n-1$ | `leggauss` |
| adaptiivinen | `quad(f, a, b)`; `points`, `weight` | Octave `integral` |

# Lineaariset yhtälöryhmät

| Tilanne | Menetelmä | Hinta |
|---------|-----------|-------|
| yleinen neliö | LU tuennalla, `solve` | $\tfrac23 n^3$ |
| symmetrinen PD | Cholesky, `cho_factor` | $\tfrac13 n^3$ |
| suorakulmainen | QR, `lstsq` | $2mn^2$ |
| huonokuntoinen | SVD | $\sim 10\,n^3$ |
| monta oikeaa puolta | `lu_factor` kerran, `lu_solve` | $2n^2$ / puoli |
| virheraja | $\lVert\hat x - x\rVert/\lVert x\rVert \lesssim \kappa\varepsilon$ | |
| harva 2D | `spsolve` | täyttyminen |
| harva iso SPD | `cg` + esiehdostin (IC, AMG) | $\sim\sqrt\kappa$ kierrosta |
| harva epäsymm. | `gmres`, `bicgstab` | |

```{.python tiedosto="esimerkit/06-hajotelmat.py" osa="lu"}
```

# Differentiaaliyhtälöt

| Asia | Sääntö tai komento |
|------|--------------------|
| kertaluvut | Euler 1, Heun 2, RK4 4 |
| Euler stabiili | $\lvert 1 + h\lambda\rvert \le 1$, eli $h \le 2/\lvert\lambda\rvert$ |
| implisiittinen | A-stabiili; vaatii yhtälön ratkaisun |
| ei-jäykkä | `solve_ivp(..., method="RK45")`; Octave `ode45` |
| jäykkä | `Radau`, `BDF`, `LSODA`; Octave `ode15s` |
| askel | $h \leftarrow 0{,}9\,h\,(\mathrm{tol}/\mathrm{arvio})^{1/(p+1)}$ |
| toleranssit | `rtol` ja `atol` mittakaavan mukaan |

# Optimointi

| Tehtävä | Menetelmä |
|---------|-----------|
| 1 muuttuja välillä | kultainen leikkaus, `minimize_scalar`, `fminbnd` |
| sileä, gradientti | BFGS, `minimize(..., jac=grad)`; Octave `fminunc` |
| ei derivaattoja | Nelder–Mead; Octave `fminsearch` |
| rajoitteet | `SLSQP`, `trust-constr` |
| lineaarinen | `linprog` (HiGHS), varjohinnat `ineqlin.marginals` |
| kokonaisluvut | `milp`; älä pyöristä LP-ratkaisua |
| minimin paikka | tarkkuus vain $\sim\sqrt\varepsilon$ |
