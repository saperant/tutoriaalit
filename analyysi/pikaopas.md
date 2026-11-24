---
title: Differentiaali- ja integraalilaskenta
subtitle: Pikaopas · kaavat, SymPy, SciPy ja Maxima
---

# Raja-arvo ja derivaatta

| Asia | Kaava tai komento |
|------|-------------------|
| raja-arvo | `sp.limit(f, x, a)`; suunta `"+"`, `"-"`, `"+-"` |
| l'Hôpital | $\lim f/g = \lim f'/g'$, vain muodoille $\tfrac00$, $\tfrac\infty\infty$ |
| derivaatta | $f'(a) = \lim_{h\to0} \frac{f(a+h) - f(a)}{h}$; `sp.diff(f, x, n)` |
| keskeinen erotus | $\frac{f(a+h) - f(a-h)}{2h}$, virhe $\sim h^2$; $h \approx 10^{-5}$ |
| tulo, osamäärä | $(uv)' = u'v + uv'$, $(u/v)' = (u'v - uv')/v^2$ |
| ketjusääntö | $(u(v(x)))' = u'(v(x))\,v'(x)$ |
| implisiittinen | `sp.idiff(F, y, x)` yhtälölle $F(x, y) = 0$ |
| kumoutuminen | $1 - \cos x = 2\sin^2\tfrac x2$; `log1p`, `expm1` |

```{.python tiedosto="esimerkit/03-saannot.py" osa="ketju"}
```

# Derivaatan sovelluksia

| Asia | Kaava tai komento |
|------|-------------------|
| kriittinen piste | $f'(a) = 0$; minimi, jos $f''(a) > 0$ |
| suljettu väli | ehdokkaat: kriittiset pisteet ja päätepisteet |
| Newton | $x_{n+1} = x_n - f(x_n)/f'(x_n)$, neliöllinen |
| varma juuri | `optimize.brentq(f, a, b)`, merkki vaihtuu |
| linearisointi | $f(a + \Delta x) \approx f(a) + f'(a)\Delta x$ |
| herkkyys | $\frac{x}{f}f'(x)$; potenssille $c x^n$ herkkyys $n$ |

# Integraali

| Asia | Kaava tai komento |
|------|-------------------|
| peruslause | $\int_a^b f\,dx = F(b) - F(a)$, $F' = f$ |
| SymPy | `sp.integrate(f, x)`, `sp.integrate(f, (x, a, b))` |
| osittain | $\int u\,dv = uv - \int v\,du$ |
| sijoitus | $u = g(x)$, $du = g'(x)\,dx$ |
| osamurrot | `sp.apart(r, x)`; Maxima `partfrac` |
| epäoleellinen | $\int_1^\infty x^{-p}\,dx$ suppenee, kun $p > 1$ |
| numeerinen | `quad(f, a, b)`; näytteille `trapezoid`, `simpson` |
| virheet | puolisuunnikas $\sim h^2$, Simpson $\sim h^4$ |
| keskiarvo, RMS | $\frac{1}{b-a}\int f$, $\sqrt{\frac{1}{b-a}\int f^2}$ |

```{.python tiedosto="esimerkit/06-numeerinen.py" osa="saannot"}
```

# Sarjat

| Asia | Kaava tai komento |
|------|-------------------|
| geometrinen | $\sum q^k = \frac{1}{1-q}$, $\lvert q\rvert < 1$ |
| harmoninen | $\sum 1/k$ hajaantuu, $H_n \approx \ln n + 0{,}5772$ |
| suhdetesti | $\lvert a_{k+1}/a_k\rvert \to L < 1$ suppenee |
| Taylor | $P_n = \sum \frac{f^{(k)}(a)}{k!}(x - a)^k$; `sp.series(f, x, a, n)` |
| jäännös | $\lvert f - P_n\rvert \le \frac{M}{(n+1)!}\lvert x - a\rvert^{n+1}$ |
| sarjat | $e^x = \sum \frac{x^k}{k!}$, $\sin x = x - \frac{x^3}{6} + \dots$ |
| pienet $x$ | $\sin x \approx x$ (1 %: 14°), $(1 + x)^n \approx 1 + nx$ |

# Usea muuttuja

| Asia | Kaava tai komento |
|------|-------------------|
| gradientti | $\nabla f = (f_x, f_y)$, jyrkin nousu |
| suunnattu | $D_{\mathbf u} f = \nabla f \cdot \mathbf u$, $\lvert\mathbf u\rvert = 1$ |
| laskeutuminen | $\mathbf p \leftarrow \mathbf p - \alpha\nabla f$, vakaa kun $\alpha < 2/L$ |
| Hessen | `sp.hessian(f, (x, y))`; ominaisarvot $> 0$: minimi |
| Jacobin | `X.jacobian([r, t])`; napakoordinaatit $\det J = r$ |
| optimointi | `optimize.minimize(f, x0, jac=grad, method="BFGS")` |
| kaksoisintegraali | `sp.integrate(f, (y, c, d), (x, a, b))` |
| napakoordinaatit | $dA = r\,dr\,d\theta$ |
| Monte Carlo | virhe $\sim 1/\sqrt N$; `rng = np.random.default_rng(siemen)` |

# Maxima

| Tehtävä | Komento |
|---------|---------|
| eräajo | `maxima --very-quiet -b skripti.mac`; `display2d: false$` |
| raja-arvo | `limit(f, x, 0, plus)`; ääretön `inf`, `minf` |
| derivaatta | `diff(f, x, 2)`; implisiittinen `depends(y, x)` |
| integraali | `integrate(f, x, a, b)`; oletukset `assume(R > 0)` |
| numeerinen | `quad_qags(f, x, a, b)`, `find_root(f, x, a, b)` |
| sarjat | `simpsum: true$`, `sum(...)`, `taylor(f, x, 0, 7)` |
| usea muuttuja | `hessian(f, [x, y])`, `solve([eq1, eq2], [x, y])` |
