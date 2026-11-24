---
title: Arkkitehtuurin mallinnus
subtitle: Pikaopas · mallit, kaavat ja menetelmät
---

# Mallien tasot

| Taso | Näkee | Ei näe |
|------|-------|--------|
| analyyttinen | rajat, suuruusluokat | ajoitus, kilpailu |
| jälkipohjainen | välimuistit, ennustimet | ajoitus |
| LT (TLM) | toiminta, ohjelmisto | kilpailu |
| intervallimalli | hudit, MLP, haarat | liukuhihnan yksityiskohdat |
| syklitarkka | kaiken mallinnetun | mallintamattoman |

# Kuormat

| Tunnusluku | Määritelmä |
|------------|------------|
| käskyjakauma | operaatioiden osuudet luokittain |
| intensiteetti | FLOP / siirretyt tavut, joka tasolle |
| uudelleenkäyttöetäisyys | eri rivit kahden viittauksen välissä |
| hutikäyrä | hudit(C) = viittaukset, joiden etäisyys $\ge C$ |
| työjoukko | eri rivit aikaikkunassa |
| MPKI | hudit / 1000 käskyä |

```{.python tiedosto="esimerkit/arkki/jalki.py" osa="hutikayra"}
```

# Suorituskyky

| Malli | Kaava |
|-------|-------|
| Amdahl | $S = 1/((1-p) + p/s)$ |
| Gustafson | $S = (1-p) + p\,n$ |
| Pollack | $\text{perf}(r) = \sqrt{r}$ |
| Hill–Marty, symm. | $1/\big(\frac{1-f}{\text{perf}(r)} + \frac{f\,r}{\text{perf}(r)\,n}\big)$ |
| Hill–Marty, epäsymm. | $1/\big(\frac{1-f}{\text{perf}(r)} + \frac{f}{\text{perf}(r) + n - r}\big)$ |
| roofline | $\min(P, \min_i B_i I_i)$ |
| Littlen kaista | kaista $= L \cdot$ rivi $/ W$ |
| CPI-pino | $\text{CPI}_0 + \sum_i \text{MPKI}_i/1000 \cdot \text{sakko}_i$ |
| AMAT | osumaviive $+$ hutiosuus $\cdot$ hutisakko |

# Jonot

| Malli | Viipymä $W$ |
|-------|-------------|
| Little | $L = \lambda W$, aina |
| M/M/1 | $1/(\mu - \lambda)$ |
| M/G/1 | $E[S] + \lambda E[S^2] / (2(1-\rho))$ |
| M/D/1 | jonotus puolet M/M/1:stä |
| M/M/c | Erlang C: $W_q = C(c, a)/(c\mu - \lambda)$ |
| suljettu | MVA; rajat $\min(K/(Z+D), 1/S_{\max})$ |

```{.python tiedosto="esimerkit/arkki/jonot.py" osa="mva"}
```

# Simulointi

| Asia | Sääntö |
|------|--------|
| syklipohjainen | joka jakso kaikki; yksinkertainen, hidas |
| tapahtumapohjainen | hyppy seuraavaan; nopea, vaatii laskentaa |
| varausmalli | oikein vain aikajärjestyksessä (kvantti 0) |
| intervallimalli | perus + väärät ennustukset + johtavat hudit |
| MLP | huti ikkunan sisällä johtavasta: ilmainen |
| riippuva huti | aina koko viive |
| SimPoint | BBV → k-means → edustajat × painot |
| lämmittely | hylkää alku; lämmitä näytteen tila |

# Teho ja pinta-ala

| Asia | Kaava |
|------|-------|
| dynaaminen | $P = \alpha C V^2 f$ |
| vuoto | $P = V I_0 e^{k(V - V_0)}$ |
| taajuus | $f \propto (V - V_t)^a / V$, $a \approx 1{,}3$ |
| EDP, ED²P | $E \cdot t$, $E \cdot t^2$ |
| SRAM | energia, viive $\propto \sqrt{\text{koko}}$; ala $\propto$ koko |
| hutiosuus | $\propto 1/\sqrt{\text{koko}}$ (keskiarvona) |

| Operaatio (45 nm) | Energia |
|-------------------|---------|
| 32 b kokonaislukusumma | 0,1 pJ |
| 32 b liukulukukertolasku | 3,7 pJ |
| SRAM 8 KiB / 1 MiB, 64 b | 10 / 100 pJ |
| DRAM, 64 b | 1,3–2,6 nJ |

# Kiihdytin

| Asia | Sääntö |
|------|--------|
| aika | asetus + huuhtelu + siirrot + laskenta + keskeytys |
| tasapiste | pienin $n$: $T_{hw}(n) < T_{sw}(n)$ |
| kaksoispuskuri | pala $= \max(\text{siirrot}, \text{laskenta})$ |
| sovellus | Amdahl profiilin osuudella |

# Tutkiminen

| Menetelmä | Käyttö |
|-----------|--------|
| ruudukko | vähän parametreja, nopea malli |
| satunnainen | lähtökohta, vertailukohta |
| latinalainen hyperkuutio | tasainen kattavuus parametreittain |
| korvikemalli, BO | kalliit arvioinnit |
| NSGA-II | monta tavoitetta |
| Pareto | ei-dominoidut pisteet |
| jousto | $(\Delta y/y)/(\Delta x/x)$ |
| katumus | $1 - y(\text{valittu})/y(\text{uusi optimi})$ |

```{.python tiedosto="esimerkit/arkki/tutkimus.py" osa="pareto"}
```

# Raportointi

| Asia | Sääntö |
|------|--------|
| toistot | eri siemenet, $\bar x \pm t_{0,975}\,s/\sqrt{n}$ |
| vertailu | yhteiset satunnaisluvut |
| validointi | eri data kuin kalibroinnissa |
| virhe | MAPE ja suurin virhe |
| nopeutusten keskiarvo | geometrinen |
| toistettavuus | parametrit, siemenet, versiot, tiiviste |
