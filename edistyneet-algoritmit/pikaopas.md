---
title: Edistyneet algoritmit ja tietorakenteet
subtitle: Pikaopas · puut, välikyselyt, merkkijonot, virtaukset, satunnaistus ja vaativuus
---

# Testausmalli

- Malli: `std::set`, raaka haku, toinen algoritmi tai lause
  (max-flow = min-cut, König).
- Satunnainen sarja kiinteällä siemenellä; vertaa jokaisen operaation
  paluuarvoa, lopuksi sisältö.
- Invariantit jäsenfunktioksi, tarkistus joka operaation jälkeen.
- Pieni avainavaruus = rajatapaukset; suuri = suuret rakenteet.
- Pienennä epäonnistunut sarja (palat pois, avaimet pienemmiksi).
- Työ laskureilla, ei kellolla; sanitoijat samaan ajoon.

```{.cpp tiedosto="esimerkit/pikaopas.cpp" osa="vertailu"}
```

# Hakupuut

| Rakenne | Korkeus | Takuu |
|---------|---------|-------|
| punamusta (LLRB) | $\le 2 \log_2 n$ | pahin |
| AVL | $\le 1{,}44 \log_2 n$ | pahin |
| treap | $\approx 4{,}3 \ln n$ | odotettu |
| skip-lista | $O(\log n)$ | odotettu |
| B-puu, aste $t$ | $\le \log_t \frac{n+1}{2}$ | pahin |

- LLRB: punainen linkki vasemmalle, ei kahta punaista peräkkäin, sama
  musta korkeus. Korjaukset: kierto vasemmalle, kierto oikealle,
  värinvaihto.
- Treap: hakupuu avaimille, keko prioriteeteille; `jaa(x)` ja
  `yhdista(a, b)`; alipuun koko → $k$:s alkio ja järjestysluku.
- B-puu: $t-1 \ldots 2t-1$ avainta, halkaisu matkalla alas, kasvaa
  juuresta. Vertailuja $\log_2 n$ asteesta riippumatta, lohkoja
  $\log_t n$.

# Tasoitettu analyysi

- $\hat c_i = c_i + \Phi_i - \Phi_{i-1}$, $\sum \hat c \ge \sum c$, kun
  $\Phi_n \ge \Phi_0$.
- Taulukko: $\Phi = 2\,\text{koko} - \text{kapasiteetti}$, $\hat c = 3$.
  Kerroin 2: 1 kopio/lisäys; 1,5: 2; vakiolisäys: $O(n)$.
- Kutista vasta $1/4$:ssä (hystereesi); $1/2$ ⇒ jokainen operaatio
  kopioi.
- Laskuri: $\Phi$ = ykköset, $\hat c = 2$. Vähennys rikkoo rajan.

# Union-find

```{.cpp tiedosto="esimerkit/pikaopas.cpp" osa="uf"}
```

- Molemmat parannukset: $O(m\,\alpha(n))$, $\alpha \le 4$. Vain
  tiivistys $O(m \log_{1+m/n} n)$, vain tasot $O(m \log n)$.
- Virtuaalisolmut reunoille; poistot → käänteinen järjestys.

# Välikyselyt

```{.cpp tiedosto="esimerkit/pikaopas.cpp" osa="fenwick"}
```

| Rakenne | Kysely | Päivitys | Operaatio |
|---------|--------|----------|-----------|
| etuliitesummat | $1$ | $n$ | käännettävä |
| Fenwick | $\log n$ | $\log n$ | käännettävä |
| segmenttipuu | $\log n$ | $\log n$ | liitännäinen |
| laiska segmenttipuu | $\log n$ | $\log n$ väli | + lykkäys |
| harva taulukko | $1$ | — | idempotentti |

- Iteratiivinen segmenttipuu: lehdet $n \ldots 2n-1$, vasen ja oikea
  tulos erikseen (järjestys!). Testaa katenaatiolla.
- Fenwickin käänteishaku: $k$:s arvo ja persentiilit lukumääristä.

# Merkkijonot

```{.cpp tiedosto="esimerkit/pikaopas.cpp" osa="vika"}
```

```{.tuloste tiedosto="esimerkit/pikaopas.odotettu"}
```

- KMP $\le 2n$ vertailua; lyhin jakso $m - \text{vika}[m-1]$.
- Z: $z[i]$ = pisin etuliite kohdasta $i$; haku jonolla
  `P # T`.
- Rabin–Karp: moduli $2^{61}-1$, satunnainen kanta, varmistus
  vertailulla. Mod $2^{64}$: Thue–Morse törmää ($2^{11}$).
- Trie: $O(m)$, etuliitemäärät; pakkaa ketjut.
- Suffiksitaulukko: tuplaus $O(n \log^2 n)$, SA-IS $O(n)$; Kasain LCP
  $O(n)$. Eri osajonoja $n(n+1)/2 - \sum \text{LCP}$.

# Virtaukset

| Algoritmi | Aika |
|-----------|------|
| Edmonds–Karp | $O(VE^2)$ |
| Dinic | $O(V^2 E)$; yksikkö $O(E\sqrt V)$ |
| Kuhn (paritus) | $O(VE)$ |
| Hopcroft–Karp | $O(E\sqrt V)$ |

- Kaari $e$ ja vastakaari $e \oplus 1$; jäännös $c - f$.
- Minimileikkaus: $s$:stä saavutettavat jäännösverkossa.
- Paritus: $s \to L \to R \to t$, kapasiteetit 1.
- König: peite $(L \setminus Z) \cup (R \cap Z)$, $Z$ = vapaista
  vasemmista vuorottelevilla poluilla.

# Satunnaistus ja tiivistelmät

- Las Vegas: aina oikein (pikavalinta $\le 4n$ odotettu, treap,
  skip-lista). Monte Carlo: virhe $\le 2^{-k}$ $k$ toistolla
  (Freivalds $O(kn^2)$).
- Bloom: $p \approx (1 - e^{-kn/m})^k$, paras $k = (m/n)\ln 2$;
  10 bittiä/avain ≈ 1 %. Ei vääriä negatiivisia.
- Count-Min: $w = \lceil e/\varepsilon \rceil$,
  $d = \lceil \ln(1/\delta) \rceil$; arvio $\ge$ tarkka,
  yliarvio $\le \varepsilon N$.
- Säiliö: alkio $i$ korvaa todennäköisyydellä $k/(i+1)$.
- Siemen arvaamaton, kun syöte tulee ulkoa.

# Vaativuus ja approksimointi

- NP: todistus tarkistettavissa polynomiajassa. Reduktio
  $A \le_p B$: tunnettu vaikea $A$ → uusi $B$.
- 3-SAT → riippumaton joukko: kolmio/lauseke, kaari $x$–$\lnot x$,
  kysytään $m$ solmua.
- Helpot erikoistapaukset: 2-SAT, kaksijakoinen peite, puut, pienet
  painot (pseudopolynominen DP).

| Ongelma | Menetelmä | Kerroin |
|---------|-----------|---------|
| solmupeite | maksimaalinen paritus | 2 |
| joukkopeite | ahne | $\ln n + 1$ |
| metrinen TSP | puukierros / Christofides | 2 / 1,5 |
| TSP tarkka | Held–Karp | $O(2^n n^2)$ |
| TSP käytäntö | lähin naapuri + 2-opt, LKH | — |
| reppu | karsinta murto-osarajalla, DP $O(nW)$ | tarkka |
