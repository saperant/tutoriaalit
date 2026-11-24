---
title: Matematiikan perusteet ohjelmallisesti
subtitle: Pikaopas · kaavat, SymPy ja Maxima
---

# SymPy

| Tehtävä | Komento |
|---------|---------|
| symbolit | `x, y = sp.symbols("x y", real=True)`; `positive=True` |
| tarkka luku | `sp.Rational(1, 3)`, `sp.S(1)/3` (ei `1/3`) |
| muokkaus | `expand`, `factor`, `cancel`, `collect`, `apart`, `simplify` |
| sijoitus | `e.subs(x, 2)`, `e.subs({x: 1, y: 2})` |
| likiarvo | `e.evalf(8)`, `sp.N(e, 8)` |
| yhtälö | `sp.solve(e, x)`; ryhmä `dict=True`; `sp.Eq(a, b)` |
| joukkona | `sp.solveset(e, x, sp.S.Reals)`; väli `sp.Interval(a, b)` |
| lineaarinen | `sp.linsolve([e1, e2], [x, y])` |
| numeerinen | `sp.nsolve(e, x, x0)`; `sp.lambdify(x, e, "numpy")` |
| tarkistus | `sp.expand(vasen - oikea) == 0`, `sp.simplify(...)` |

```{.python tiedosto="esimerkit/01-tarkistus.py" osa="laajennus"}
```

# Maxima

| Tehtävä | Komento |
|---------|---------|
| eräajo | `maxima --very-quiet -b skripti.mac`; `display2d: false$` |
| sijoitus, funktio | `a: 2$`, `f(x) := x^2$`, `subst(2, x, e)` |
| vakiot | `%pi`, `%e`, `%i`; likiarvo `float(e)` |
| muokkaus | `expand`, `factor`, `ratsimp`, `partfrac`, `trigexpand` |
| yhtälö | `solve([x + y = 10, x - y = 2], [x, y])` |
| numeerinen | `find_root(cos(x) - x, x, 0, 1)` |
| summa | `simpsum: true$ sum(k^2, k, 1, n)` |

# Yhtälöt

| Asia | Kaava tai sääntö |
|------|------------------|
| toinen aste | $x = \frac{-b \pm \sqrt{D}}{2a}$, $D = b^2 - 4ac$ |
| vakaa juuri | $q = -\tfrac12(b + \operatorname{sgn}(b)\sqrt D)$, $x_1 = q/a$, $x_2 = c/q$ |
| jäännöslause | $p(r) = 0 \iff (x - r)$ jakaa $p(x)$ |
| itseisarvo | $\lvert x - a\rvert < r \iff a - r < x < a + r$ |
| määrittely | nimittäjä $\ne 0$, $\sqrt{g}$: $g \ge 0$, $\ln g$: $g > 0$ |

```{.python tiedosto="esimerkit/03-toinen-aste.py" osa="kumoutuminen"}
```

```{.python tiedosto="esimerkit/08-induktio.py" osa="induktio"}
```

# Funktiot

| Asia | Kaava tai sääntö |
|------|------------------|
| käänteisfunktio | ratkaise $y = f(x)$ $x$:n suhteen; vain bijektiolle |
| peilaus | $f^{-1}$:n kuvaaja on $f$:n peilikuva suoran $y = x$ suhteen |
| puolitushaku | $n = \lceil \log_2 \frac{b - a}{2\varepsilon} \rceil$ kierrosta |
| näytteistys | yli 2 pistettä värähtelyjaksoa kohden, mieluummin 10+ |
| asymptootti | katkaise viiva: suuret arvot NaN:iksi |

# Eksponentti ja logaritmi

| Asia | Kaava tai sääntö |
|------|------------------|
| kasvu | $N_0(1+p)^t = N_0 e^{kt}$, $k = \ln(1 + p)$ |
| tuplaus | $t = \ln 2 / \ln(1 + p) \approx 70/(100p)$ |
| aikavakio | $e^{-t/\tau}$; puoliintuminen $\tau \ln 2$; $5\tau$: alle 1 % |
| säännöt | $\log xy = \log x + \log y$, $\log x^r = r\log x$ ($x, y > 0$) |
| kanta | $\log_a x = \ln x / \ln a$ |
| desibelit | teho $10\lg$, amplitudi $20\lg$; $\times2$: 3 dB / 6 dB |

# Trigonometria

| Asia | Kaava tai sääntö |
|------|------------------|
| radiaanit | $\theta_\text{rad} = \theta_\circ \pi/180$; ohjelmissa aina radiaanit |
| arvot | $\sin\frac{\pi}{6} = \tfrac12$, $\sin\frac{\pi}{4} = \tfrac{\sqrt2}{2}$, $\sin\frac{\pi}{3} = \tfrac{\sqrt3}{2}$ |
| kaksinkertainen | $\sin 2x = 2\sin x\cos x$, $\cos 2x = 1 - 2\sin^2 x$ |
| ratkaisut | $\sin x = a$: $x_0 + 2\pi n$, $\pi - x_0 + 2\pi n$ |
| värähtely | $A\sin\omega t + B\cos\omega t = R\sin(\omega t + \varphi)$ |
| amplitudi, vaihe | $R = \sqrt{A^2 + B^2}$, $\varphi = \operatorname{atan2}(B, A)$ |

# Geometria

| Asia | Kaava tai sääntö |
|------|------------------|
| pistetulo | $\mathbf a\cdot\mathbf b = \lvert\mathbf a\rvert\lvert\mathbf b\rvert\cos\theta$; 0 = kohtisuora |
| projektio | $\frac{\mathbf a\cdot\mathbf b}{\mathbf b\cdot\mathbf b}\mathbf b$ |
| normaali | suunta $(v_1, v_2)$ → normaali $(-v_2, v_1)$ |
| etäisyys | $d = \lvert ap_x + bp_y + c\rvert / \sqrt{a^2 + b^2}$ |
| ympyrä | $(x - x_0)^2 + (y - y_0)^2 = r^2$ |
| törmäys | $(\mathbf v\cdot\mathbf v)t^2 + 2(\mathbf d\cdot\mathbf v)t + \mathbf d\cdot\mathbf d - r^2 = 0$ |

# Jonot ja summat

| Asia | Kaava tai sääntö |
|------|------------------|
| aritmeettinen | $a_n = a_1 + (n - 1)d$ |
| geometrinen | $b_n = b_1 q^{n-1}$; summa $b_1\frac{q^n - 1}{q - 1}$ |
| potenssisummat | $\sum k = \frac{n(n+1)}{2}$, $\sum k^2 = \frac{n(n+1)(2n+1)}{6}$ |
| harmoninen | $H(n) \approx \ln n + 0{,}5772$ |
| annuiteetti | $A = L i (1+i)^n / ((1+i)^n - 1)$ |
| induktio | perusaskel + askel $P(n) \Rightarrow P(n+1)$ |
