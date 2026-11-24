---
title: Algoritmit
subtitle: Pikaopas · vaativuus, lajittelu, haku, suunnittelumenetelmät ja graafit
---

# Kasvuluokat

| Luokka | Esimerkki | $n$ / s |
|--------|-----------|---------|
| $\log n$ | binäärihaku | rajaton |
| $n$ | Kadane, lineaarihaku | $10^8$ |
| $n \log n$ | lomitus, keko, Dijkstra | $10^7$ |
| $n^2$ | lisäys, LCS, Prim taulukolla | $10^4$ |
| $n^3$ | kaikki välit suoraan | 500 |
| $2^n$ | kaikki osajoukot | 27 |
| $n!$ | kaikki järjestykset | 11 |

- $O$ yläraja, $\Omega$ alaraja, $\Theta$ molemmat; vakiot ja kanta
  katoavat.
- Kaksinkertaista $n$: suhde 2 lineaarinen, 4 neliöllinen, hieman yli 2
  $n \log n$; vakioerotus $\log n$.
- Pahin = takuu, keskimääräinen = jakaumaoletus, satunnaistettu =
  odotusarvo omien valintojen yli, tasoitettu = sarjan keskiarvo.

| Rekursio | Ratkaisu |
|----------|----------|
| $T(n/2) + 1$ | $\log n$ |
| $2T(n/2) + n$ | $n \log n$ |
| $3T(n/2) + n$ | $n^{1{,}585}$ |
| $T(n-1) + n$ | $n^2$ |

# Lajittelu

| Algoritmi | Pahin | Keskim. | Muisti | Vakaa |
|-----------|-------|---------|--------|-------|
| lisäys | $n^2$ | $n^2$ | 1 | kyllä |
| lomitus | $n \log n$ | $n \log n$ | $n$ | kyllä |
| pika (satunn.) | $n^2$ | $n \log n$ | $\log n$ | ei |
| keko | $n \log n$ | $n \log n$ | 1 | ei |
| laskeminen | $n + k$ | $n + k$ | $n + k$ | kyllä |
| kantaluku | $d(n + b)$ | $d(n + b)$ | $n + b$ | kyllä |

- Lisäyslajittelun työ $\Theta(n + I)$, $I$ = inversiot.
- Pikalajittelu: satunnainen jakoalkio, kolmijako toistoille, rekursio
  lyhyempään osaan. Introsort = pika + keko + lisäys.
- Vertailulajittelun alaraja $\log_2 n! \approx n \log_2 n - 1{,}44\,n$.
- Vakaus: tasapelissä vasen; `qsort` ei ole vakaa.

```{.c tiedosto="esimerkit/pikaopas.c" osa="vertailija"}
```

# Binäärihaku

```{.c tiedosto="esimerkit/pikaopas.c" osa="alaraja"}
```

- Yläraja: ehto `a[keski] <= x`. Esiintymät = yläraja − alaraja.
- Ylöspäin pyöristävä keskikohta: `hi - (hi - lo) / 2`.
- Haku arvoalueelta: monotoninen ehto `ok(c)`, etsi pienin tosi;
  $O(\textrm{tarkistus} \cdot \log \textrm{alue})$.

# Suunnittelumenetelmät

- **Hajota ja hallitse:** $T(n) = aT(n/b) + f(n)$, master-lause.
  Inversiot lomituksessa: oikean puolen alkio + `keski - i`.
  Karatsuba: $z_1 = (a_0 + a_1)(b_0 + b_1) - z_0 - z_2$.
- **Ahne:** vaihtoargumentti. Aikataulutus aikaisimman loppumisen
  mukaan; Huffman yhdistää kaksi kevyintä. Kolikot {1, 3, 4}:
  ahne väärin summalla 6.
- **Dynaaminen ohjelmointi:** määrittele osatehtävä, rekursio,
  täyttöjärjestys, rekonstruktio taulukosta takaperin.

| Tehtävä | Rekursio |
|---------|----------|
| reppu | `p[i][w] = max(p[i-1][w], p[i-1][w-pi] + ai)` |
| LCS | samat: `p[i-1][j-1] + 1`, muuten `max(ylä, vasen)` |
| editointi | `min(ylä + 1, vasen + 1, vino + (ai != bj))` |

```{.c tiedosto="esimerkit/pikaopas.c" osa="reppu"}
```

# Graafit

| Tehtävä | Algoritmi | Aika |
|---------|-----------|------|
| painoton lyhin polku | BFS jonolla | $n + m$ |
| sykli, topologinen | DFS kolmella värillä, Kahn | $n + m$ |
| painot $\ge 0$ | Dijkstra keolla | $(n + m) \log n$ |
| negatiiviset painot | Bellman–Ford | $nm$ |
| virittävä puu, harva | Kruskal + union-find | $m \log m$ |
| virittävä puu, tiheä | Prim taulukolla | $n^2$ |

- BFS: merkitse löydetyksi, kun lisäät jonoon.
- Dijkstra: lisää uudelleen paremmalla etäisyydellä, ohita vanhentuneet.
- Bellman–Ford: $n$:s kierros muuttaa jotain → negatiivinen sykli.
- Kruskal: lajittele kaaret, ota jos `etsi(u) != etsi(v)`.

```{.c tiedosto="esimerkit/pikaopas.c" osa="etsi"}
```

```{.tuloste tiedosto="esimerkit/pikaopas.odotettu"}
```

# Testaus

- Raaka referenssi: kaikki osajoukot, kaikki parit, `qsort`, toinen
  algoritmi. Pieni $n$, pieni arvoalue, kiinteä siemen.
- Monta oikeaa vastausta: tarkista sallittuus ja arvo.
- Laskurit vertailuille; kello vain `-O2`-mittaukseen väljällä
  rajalla.
- `-fsanitize=address,undefined -fno-sanitize-recover=all` löytää
  ylivuodot vertailijassa ja keskikohdassa.
