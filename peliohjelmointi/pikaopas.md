---
title: Peliohjelmointi
subtitle: Pelin rakenteet tiiviisti
lang: fi
---

# Pelisilmukka

```{.cpp tiedosto="esimerkit/pikaopas.cpp" osa="silmukka"}
```

```{.cpp tiedosto="esimerkit/pikaopas.cpp" osa="kaytto"}
```

- Kiinteä askel 1/60 s; aika `std::chrono::nanoseconds`-lukuina.
- Ruudun kesto rajataan (0,1–0,25 s): ei kuolemanspiraalia.
- Piirto interpoloi: `alfa = kertymä / askel`, yhden askeleen viive.

# Determinismi

| Uhka | Ratkaisu |
|------|----------|
| muuttuva `dt` | kiinteä askel |
| `std::*_distribution` | oma PCG32 ja välin valinta |
| `unordered_map`-järjestys | lajiteltu tai tunnisteen mukaan |
| `-ffast-math`, FMA | kiinteät kääntäjäasetukset |
| kello logiikassa | `dt` parametrina |

Tallenne + tarkistussumma = regressiotesti.

# Syöte

```{.cpp tiedosto="esimerkit/pikaopas.cpp" osa="reuna"}
```

- Näppäimet → toiminnot kartalla; hyppy painalluksesta, liike pidosta.
- Puskurointi ja kojoottiaika noin 3–6 ruutua.

# Törmäykset

```{.cpp tiedosto="esimerkit/pikaopas.cpp" osa="aabb"}
```

| Muoto | Testi |
|-------|-------|
| AABB | välit kummallakin akselilla |
| ympyrä | etäisyyden neliö < säteiden summan neliö |
| kupera monikulmio | SAT: särmien normaalit |
| nopea kappale | pyyhkäisy, säde, CCD |
| paljon kappaleita | ruudukko, nelipuu, BVH |

# Fysiikka

| Integraattori | Käyttö |
|---------------|--------|
| eksplisiittinen Euler | ei peleihin: energia kasvaa |
| semi-implisiittinen Euler | oletus: `v += a dt; x += v dt` |
| nopeus-Verlet | tarkempi, kaksi kiihtyvyyttä |
| paikka-Verlet | köydet, kankaat, ragdollit |

Hyppy korkeudelle *h* ajassa *t*: `g = 2h/t²`, `v₀ = 2h/t`.

# Arkkitehtuuri

| Malli | Käyttö |
|-------|--------|
| tilakone | tekoäly, hahmo, animaatio |
| kohtauspino | valikko, peli, tauko |
| tapahtumajono | ääni, pisteet, saavutukset |
| ECS | paljon samanlaisia olioita |
| kahva | viittaukset resursseihin ja entiteetteihin |
| objektipooli | ammukset, partikkelit |

# Hinnat 60 Hz:llä

- Ruudun budjetti 16,7 ms; 144 Hz:llä 6,9 ms.
- Hajallaan olevat oliot ja virtuaalikutsut: noin 20 kertaa hitaampi
  päivitys kuin tiiviit taulukot (miljoona oliota).
- Kaikkien parien törmäystesti O(n²): 2000 kappaletta ≈ 2 milj. testiä.
- Keon varaus pelisilmukassa: arvaamaton kesto, pirstoutuminen.
- Äänisäie: ei varauksia, ei levyä, ei lukkoja.

# Työkalut

| Tarve | Komento |
|-------|---------|
| kääntö | `g++ -std=c++23 -Wall -Wextra -fsanitize=address,undefined` |
| SDL2-liput | `sdl2-config --cflags --libs` |
| ikkunaton SDL | `SDL_VIDEODRIVER=dummy` |
| esimerkit | `make sdl`, `make pelaa`, `make mittaa` |
