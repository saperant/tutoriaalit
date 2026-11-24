---
title: Tietorakenteet
subtitle: Pikaopas · rakenteet, hinnat ja idiomit C23:lla
---

# Operaatioiden hinnat

| Rakenne | Haku | Lisäys | Poisto | Muuta |
|---------|------|--------|--------|-------|
| vektori | $O(n)$, indeksi $O(1)$ | loppuun tas. $O(1)$ | lopusta $O(1)$, keskeltä $O(n)$ | paras paikallisuus |
| lajiteltu taulukko | $O(\log n)$ | $O(n)$ | $O(n)$ | välit, järjestys |
| linkitetty lista | $O(n)$ | $O(1)$ paikassa | $O(1)$ kaksoislink. | pysyvät osoittimet |
| rengaspuskuri | – | $O(1)$ | $O(1)$ | kiinteä koko |
| hajautustaulu | odot. $O(1)$ | odot. $O(1)$ | odot. $O(1)$ | ei järjestystä |
| hakupuu (tasap.) | $O(\log n)$ | $O(\log n)$ | $O(\log n)$ | välit, edeltäjä |
| hakupuu (pahin) | $O(n)$ | $O(n)$ | $O(n)$ | järjestetty syöte |
| binäärikeko | pienin $O(1)$ | $O(\log n)$ | pienin $O(\log n)$ | kekoutus $O(n)$ |

# Dynaaminen taulukko

- Kasvata kertoimella 1,5–2: $n$ lisäystä kopioi enintään
  $n \cdot k/(k-1)$ alkiota. Vakiolisäys kopioi $\approx n^2/(2c)$.
- `realloc` väliaikaiseen muuttujaan; vanha muisti ennallaan virheessä.
- Osoitin taulukon sisään mitätöityy kasvatuksessa → käytä indeksiä.
- Poisto vaihtamalla viimeiseen: $O(1)$, järjestys muuttuu.
- Kutista vasta, kun koko $\leq$ kapasiteetti/4.

```{.c tiedosto="esimerkit/pikaopas.c" osa="kasvu"}
```

# Listat

- Osoitin osoittimeen poistaa alkupään erikoistapauksen.
- Tunnussolmu: rengas, tyhjä lista osoittaa itseensä, ei `if`-lauseita.
- Tunkeileva lista: linkit tietueessa, ei varauksia, monta listaa.

```{.c tiedosto="esimerkit/pikaopas.c" osa="linkki"}
```

# Indeksit ja makrot

```{.c tiedosto="esimerkit/pikaopas.c" osa="indeksit"}
```

```{.tuloste tiedosto="esimerkit/pikaopas.odotettu"}
```

# Rengaspuskuri

| Malli | Täysi | Tyhjä |
|-------|-------|-------|
| tyhjä paikka | `(k + 1) % K == l` | `k == l` |
| laskuri | `n == K` | `n == 0` |
| juoksevat indeksit | `k - l == K` | `k - l == 0` |

Juoksevat etumerkittömät indeksit: $K$ kahden potenssi, kumpikin
osapuoli kirjoittaa vain omaa indeksiään → lukoton SPSC-jono
atomisilla indekseillä.

# Hajautus

```{.c tiedosto="esimerkit/pikaopas.c" osa="fnv"}
```

- Indeksi `h & (K - 1)`, kun $K = 2^b$; heikolle funktiolle
  Fibonacci: `(h * 2654435769u) >> (32 - b)`.
- Ketjutus: kasvata, kun $\alpha > 1$; haku $\approx 1 + \alpha/2$.
- Lineaarinen kokeilu: kasvata, kun $\alpha > 0{,}75$; huti
  $\approx \frac12(1 + 1/(1-\alpha)^2)$.
- Poisto: hautakivi; hautakivet lasketaan kuormaan.
- Ulkoa tulevat avaimet: avaimellinen funktio (SipHash).

# Hakupuu ja keko

- Hakupuun poisto, kaksi lasta: korvaa seuraajalla (oikean alipuun
  pienin).
- Invariantti: avain välillä, jonka *kaikki* esivanhemmat määräävät.
- Järjestyksessä lisätty puu = lista, korkeus $n$.
- Keko: vanhempi $\lfloor(i-1)/2\rfloor$, lapset $2i+1$, $2i+2$.
- Lisäys: loppuun ja nosta. Otto: viimeinen juureen ja laske.
- Kekoutus: `for (i = n/2; i-- > 0;) laske(i)`, $O(n)$.

# Graafit

| Ominaisuus | Matriisi | Listat | CSR |
|------------|------------|----------------|----------------|
| muisti | $n^2$ bittiä | $O(n+m)$ + osoittimet | $O(n+m)$ |
| kaari $(u,v)$? | $O(1)$ | $O(\text{aste})$ | $O(\log \text{aste})$ lajit. |
| naapurit | $O(n)$ | $O(\text{aste})$ | $O(\text{aste})$, peräkkäin |

CSR: asteluvut → kumulatiivinen summa `alku[]` → naapurit `kohde[]`.

# Välimuisti

- Rivi 64 tavua; peräkkäinen läpikäynti hakee rivin kerran.
- Satunnainen lista: lähes rivi solmua kohti, ei etukäteishakua.
- AoS vs. SoA: yhden kentän silmukka koskettaa SoA:ssa
  `sizeof(tietue)/sizeof(kenttä)` kertaa vähemmän rivejä.
- Mittaa rivinvaihtoja tai laskureita; ajoitukset `-O2`, paras
  monesta, väljä raja.

# Testaus

- Vertailutesti: satunnainen sarja, kiinteä siemen, referenssinä
  totuusarvo- tai lajiteltu taulukko; pieni avainalue.
- Invariantti jokaisen operaation jälkeen.
- `-fsanitize=address,undefined -fno-sanitize-recover=all`.
