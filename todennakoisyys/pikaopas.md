---
title: Todennäköisyys ja tilastot
subtitle: Pikaopas · jakaumat, laskusäännöt, välit ja testit
---

# Laskusäännöt

| Sääntö | Kaava |
|--------|-------|
| komplementti | $P(\bar A) = 1 - P(A)$ |
| yhdiste | $P(A \cup B) = P(A) + P(B) - P(A \cap B)$ |
| ehdollinen | $P(A \mid B) = P(A \cap B)/P(B)$ |
| Bayes | $P(A \mid B) = P(B \mid A)P(A)/P(B)$ |
| riippumattomuus | $P(A \cap B) = P(A)P(B)$ |
| lineaarisuus | $E[aX + bY] = aE[X] + bE[Y]$ |
| varianssi | $\operatorname{Var}(aX + b) = a^2\operatorname{Var}(X)$ |
| summa | $\operatorname{Var}(X+Y) = \operatorname{Var}X + \operatorname{Var}Y + 2\operatorname{Cov}$ |

# Jakaumat

| Jakauma | Malli | $E$ | Var |
|---------|-------|-----|-----|
| Bin($n$, $p$) | onnistumiset | $np$ | $np(1-p)$ |
| Geom($p$) | yrityksiä | $1/p$ | $(1-p)/p^2$ |
| Poisson($\lambda$) | tapahtumat | $\lambda$ | $\lambda$ |
| Exp($\lambda$) | väliaika | $1/\lambda$ | $1/\lambda^2$ |
| N($\mu$, $\sigma^2$) | summa, kohina | $\mu$ | $\sigma^2$ |

- Normaali: 68 / 95 / 99,7 % yhden, kahden ja kolmen $\sigma$:n sisällä.
- Exp ja Geom ovat muistittomia.
- Poisson: varianssi ≈ keskiarvo; suurempi varianssi = ryöppyjä.

```{.python tiedosto="esimerkit/pikaopas.py" osa="kaavat"}
```

# Satunnaisluvut

```{.python tiedosto="esimerkit/pikaopas.py" osa="generaattori"}
```

- Käänteisfunktio: $X = F^{-1}(U)$; Exp: $-\ln(1-U)/\lambda$.
- Salaisuuksiin `secrets`, ei PRNG:tä.

# Estimointi ja välit

```{.python tiedosto="esimerkit/pikaopas.py" osa="tunnusluvut"}
```

```{.python tiedosto="esimerkit/pikaopas.py" osa="bootstrap"}
```

- Keskivirhe $s/\sqrt{n}$; Monte Carlon virhe pienenee kuten $1/\sqrt{n}$.
- Alle 30 havaintoa: $t$-kerroin 1,96:n sijaan.
- Persentiili $p$ vaatii noin $50/(1-p)$ havaintoa.

# Kohina ja testit

| Asia | Sääntö |
|------|--------|
| SNR teho / amplitudi | $10\log_{10}$ / $20\log_{10}$ |
| keskiarvoistus | $N$ mittausta: $+10\log_{10}N$ dB |
| riippumattomat kohinat | $\sigma = \sqrt{\sigma_1^2 + \sigma_2^2}$ |
| korreloituneet | $\sigma = \sigma_1 + \sigma_2$ |
| hajautettu pyyntö | $P(\text{hidas}) = 1 - (1-p)^N$ |
| monivertailu | Bonferroni: $\alpha / m$ |

- Päätä otoskoko ja analyysi etukäteen; älä kurki.
- Ilmoita efekti ja luottamusväli p-arvon rinnalla.
