---
title: Lineaarialgebra
subtitle: Pikaopas · kaavat, NumPy ja numeeriset nyrkkisäännöt
---

# Vektorit

| Suure | Kaava |
|-------|-------|
| pituus | $\lVert v \rVert = \sqrt{v \cdot v}$ |
| pistetulo | $u \cdot v = \sum u_i v_i = \lVert u \rVert \lVert v \rVert \cos\theta$ |
| projektio | $\dfrac{v \cdot u}{u \cdot u}\, u$ |
| ristitulo | $\perp$ molempia, pituus = suunnikkaan ala |
| kohtisuoruus | $u \cdot v = 0$ |

# Matriisit

| Asia | Muista |
|------|--------|
| sarakkeet | kantavektorien kuvat |
| $AB$ | ensin $B$, sitten $A$; ei vaihdannainen |
| $(AB)^T$ | $B^T A^T$ |
| $(AB)^{-1}$ | $B^{-1} A^{-1}$ |
| $\det$ | alan/tilavuuden kerroin; $< 0$ peilaa, $0$ litistää |
| ortogonaalinen $Q$ | $Q^T Q = I$, $Q^{-1} = Q^T$, säilyttää pituudet |
| kierto tasossa | $\begin{pmatrix} c & -s \\ s & c \end{pmatrix}$ |
| homogeeninen | piste $w=1$, suunta $w=0$, siirto viimeiseen sarakkeeseen |

# Ratkaiseminen

| Tehtävä | Menetelmä | Työ |
|---------|-----------|-----|
| $Ax = b$ | LU osittaistuennalla | $\tfrac{2}{3}n^3$ |
| sama $A$, uusi $b$ | sijoitukset | $2n^2$ |
| symmetrinen pos. def. | Cholesky | $\tfrac{1}{3}n^3$ |
| $\min \lVert Ax - b \rVert$ | QR / SVD (`lstsq`) | $O(mn^2)$ |
| ominaisarvot | QR-algoritmi (`eig`, `eigh`) | $O(n^3)$ |
| suurin ominaisarvo | potenssimenetelmä | matriisitulo/kierros |

Ratkaisujen määrä: aste $A$ < aste $[A|b]$ → ei ratkaisua;
aste $= n$ → yksi; muuten $n - r$ vapaata muuttujaa.

# NumPy

```{.python tiedosto="esimerkit/pikaopas.py" osa="numpy"}
```

```{.tuloste tiedosto="esimerkit/pikaopas.odotettu"}
```

# Numeriikka

- Kuntoluku $\kappa = \sigma_{\max}/\sigma_{\min}$; $\kappa \approx
  10^k$ vie noin $k$ numeroa (float64:ssä noin 16, float32:ssa 7).
- `solve`, ei `inv`; `lstsq`, ei $A^TA$; `eigh` symmetrisille.
- Osittaistuenta aina; modifioitu Gram–Schmidt tai Householder.
- Vertaa `np.allclose`illa; rajaa `acos`in argumentti välille $[-1, 1]$.
- Skaalaa ja keskitä muuttujat ennen sovitusta ja PCA:ta.
- Ortogonalisoi kertyvät kierrot säännöllisesti.
