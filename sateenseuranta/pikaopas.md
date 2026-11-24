---
title: Säteenseuranta ja fysikaalinen valaistus
subtitle: Pikaopas · leikkaukset, BVH, Monte Carlo, polunseuranta ja materiaalit
lang: fi
---

# Säde ja kamera

- **Säde** $\mathbf{o} + t\mathbf{d}$, $|\mathbf{d}| = 1$, osuma
  välillä $(t_\text{min}, t_\text{max})$; $t_\text{max}$ = lähin
  tähänastinen osuma tai etäisyys valoon.
- **Kamera:** $\mathbf{d} = \text{norm}(s_x\mathbf{x} + s_y\mathbf{y} +
  f\mathbf{z})$, $s_x = (2p_x/L - 1)\,L/K$, $s_y = 1 - 2p_y/K$,
  $f = 1/\tan(\theta/2)$.
- **Pikseli** on integraali: satunnaiset näytteet pikselin alueelta,
  keskiarvo radianssina.
- **Toistettavuus:** PCG32, oma virta pikselille, yksi satunnaisluku
  lausetta kohden.

# Leikkaukset

| Kappale | Ratkaisu |
|---------|----------|
| pallo | $b = -\mathbf{f}\cdot\mathbf{d}$, $\Delta = r^2 - \lVert\mathbf{f} + b\mathbf{d}\rVert^2$, $q = b + \operatorname{sgn}(b)\sqrt\Delta$, $t = c/q,\ q$ |
| taso | $t = (e - \mathbf{n}\cdot\mathbf{o}) / (\mathbf{n}\cdot\mathbf{d})$ |
| kolmio | Möller–Trumbore: $\mathbf{p} = \mathbf{d}\times\mathbf{e}_2$, $\det = \mathbf{e}_1\cdot\mathbf{p}$, $u$, $v$, $t$ Cramerilla |
| laatikko | laatat: $t_{0,1} = (\text{min}, \text{max} - o)\cdot d^{-1}$, välien leikkaus |

- **Itseleikkaus:** lähtöpiste $\mathbf{p} + \varepsilon\mathbf{n}$
  oikealle puolelle; $\varepsilon$ suhteessa koordinaatteihin.
- **NaN laatassa:** vertailut muotoon `t0 > tmin ? t0 : tmin`.

# BVH

- **SAH:** $C = C_\text{läpi} + (A_V N_V + A_O N_O)/A$, lokerot
  (12/akseli), lehti jos halvempi ja pieni.
- **Läpikäynti:** pino, lähempi lapsi ensin, ohita solmu jos
  $t_\text{laatikko} \ge t_\text{osuma}$.
- **Testaus:** sama tarkistussumma kuin raakahaulla, satunnaiset
  säteet, laskurit.

# Radiometria

| Suure | Yksikkö |
|-------|---------|
| vuo $\Phi$ | W |
| irradianssi $E = \int L\cos\theta\,d\omega$ | W/m² |
| radianssi $L$ | W/(m² sr) |

- $\int_\Omega \cos\theta\,d\omega = \pi$; Lambert $f = \rho/\pi$.
- $d\omega = \cos\theta'\,dA/r^2$.
- **Renderöintiyhtälö:**
  $L_o = L_e + \int f\,L_i\cos\theta_i\,d\omega_i$.

# Monte Carlo

- $\hat I = \frac1N\sum g(x_k)/p(x_k)$, harhaton, virhe
  $\sigma/\sqrt N$.
- **Tiheydet:** tasainen $1/(2\pi)$; kosini $\cos\theta/\pi$;
  kartio $1/(2\pi(1 - \cos\theta_\text{max}))$; valon pinta $1/A$.
- **Kosinipoiminta:** $r = \sqrt{u_1}$, $\phi = 2\pi u_2$,
  $z = \sqrt{1 - u_1}$.
- **Kolmion piste:** $s = \sqrt{u_1}$:
  $(1 - s)\mathbf{a} + s(1 - u_2)\mathbf{b} + s u_2\mathbf{c}$.
- **MIS:** $w_i = n_i p_i / \sum_j n_j p_j$.

# Polunseuranta

```{.cpp tiedosto="esimerkit/yhteinen/polku.hpp" osa="asetukset"}
```

- Diffuusi paino = albedo (kosinipoiminnalla).
- Suora valo: $f L_e \cos\theta\cos\theta' A / r^2 \cdot V$;
  silloin valoon osumista ei lasketa uudelleen.
- Ruletti: $q = \min(0{,}95, \max(\text{paino}))$, paino $/q$.

# Materiaalit

- **Cook–Torrance:** $f = DGF / (4\,\mathbf{n}\cdot\mathbf{l}\
  \mathbf{n}\cdot\mathbf{v})$, $\alpha = \text{karheus}^2$.
- **GGX:** $D = \alpha^2 / (\pi((\mathbf{n}\cdot\mathbf{h})^2(\alpha^2-1)+1)^2)$.
- **Smith:** $G_1 = 2c / (c + \sqrt{\alpha^2 + (1 - \alpha^2)c^2})$.
- **Schlick:** $F = F_0 + (1 - F_0)(1 - \cos)^5$; eriste
  $F_0 = 0{,}04$, metalli $F_0$ = väri.
- **Testit:** albedo $\le 1$, valkoinen uuni (Lambert = 1,000).

# Näytteistys ja kuva

| Menetelmä | Virhe reunalla |
|-----------|----------------|
| satunnainen | $N^{-1/2}$ |
| ositettu | $N^{-3/4}$ |
| Halton (2, 3) + kierto | $\approx N^{-3/4}$ – $N^{-1}$ |

- **Kohinan poisto:** apupuskurit (materiaali, normaali, syvyys),
  harha mitataan vertailukuvaa vastaan.
- **Sävykuvaus:** Reinhard $x/(1+x)$, ACES-sovite; valotus →
  sävykuvaus → sRGB.

# Tyypilliset virheet

| Oire | Syy |
|------|-----|
| pisteitä varjossa | itseleikkaus, siirto puuttuu |
| kuva liian kirkas tai tumma | $\pi$ tai pdf väärin |
| GCC ja Clang eri kuvan | argumenttien laskentajärjestys |
| kirkkaita pisteitä kiillossa | MIS puuttuu |
| reikiä kuvassa | BVH ohittaa osuman |
| peilikuva | kameran kanta |
