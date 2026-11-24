---
title: Diskreetti matematiikka
subtitle: Pikaopas · logiikka, kombinatoriikka, lukuteoria ja graafit
---

# Logiikka

| Laki | Muoto |
|------|-------|
| De Morgan | $\neg(p \land q) \equiv \neg p \lor \neg q$ |
| implikaatio | $p \to q \equiv \neg p \lor q$ |
| kontrapositio | $p \to q \equiv \neg q \to \neg p$ |
| kvanttorin negaatio | $\neg \forall x\, P \equiv \exists x\, \neg P$ |
| tyhjä joukko | `all([])` tosi, `any([])` epätosi |

- Ekvivalenssi tarkistetaan kaikilla $2^n$ arvoilla
  (`itertools.product([False, True], repeat=n)`).
- CNF: lausekkeiden konjunktio; SAT-ratkaisijoiden syöte.

# Joukot ja relaatiot

| Käsite | Koko tai ehto |
|--------|---------------|
| potenssijoukko | $2^{\lvert A \rvert}$ |
| karteesinen tulo | $\lvert A \rvert \cdot \lvert B \rvert$ |
| injektio | eri syötteet → eri kuvat |
| bijektio | injektio ja surjektio; käänteisfunktio |
| ekvivalenssi | refleksiivinen, symmetrinen, transitiivinen |
| osittainen järjestys | refleksiivinen, antisymmetrinen, transitiivinen |

# Kombinatoriikka

| | järjestys merkitsee | ei merkitse |
|-|---------------------|-------------|
| ilman toistoa | $n!/(n-k)!$ | $\binom{n}{k}$ |
| toistoin | $n^k$ | $\binom{n+k-1}{k}$ |

- Lokero: jossakin vähintään $\lceil m/n \rceil$.
- Inkluusio–ekskluusio: lisää yksittäiset, vähennä parit, lisää
  kolmikot.

```{.python tiedosto="esimerkit/pikaopas.py" osa="kaavat"}
```

```{.tuloste tiedosto="esimerkit/pikaopas.odotettu"}
```

# Lukuteoria

| Työkalu | Python |
|---------|--------|
| syt, pyj | `math.gcd`, `math.lcm` |
| käänteisalkio | `pow(a, -1, m)` (vaatii syt = 1) |
| modulaaripotenssi | `pow(a, e, m)`, $O(\log e)$ |
| Fermat | $a^{p-1} \equiv 1 \pmod{p}$ |
| CRT | jaottomat modulit → yksikäsitteinen $x \bmod \prod m_i$ |

# Rekursio

| Yhtälö | Ratkaisu |
|--------|----------|
| $T(n) = T(n/2) + 1$ | $\Theta(\log n)$ |
| $T(n) = 2T(n/2) + n$ | $\Theta(n \log n)$ |
| $T(n) = aT(n/b) + n^d$, $d < \log_b a$ | $\Theta(n^{\log_b a})$ |
| $T(n) = T(n-1) + T(n-2)$ | $\Theta(\varphi^n)$, $\varphi \approx 1{,}618$ |

# Graafit ja puut

- Kättelylemma: $\sum \deg(v) = 2\lvert E \rvert$.
- Euler-polku: 0 tai 2 paritonasteista solmua (helppo).
  Hamilton: NP-täydellinen.
- Kaksijakoinen ⇔ ei paritonta kehää.
- Puu: yhtenäinen, $n - 1$ kaarta, yksi polku solmuparien välillä;
  $n^{n-2}$ numeroitua puuta.
