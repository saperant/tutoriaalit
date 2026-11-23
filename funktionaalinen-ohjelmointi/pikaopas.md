---
title: Funktionaalinen ohjelmointi
subtitle: Pikaopas · Racket 8.10 · vastineet valtavirran kieliin
---

# Työkalut

| Tarkoitus | Komento |
|-----------|---------|
| Aja moduuli (ja `main`-alimoduuli) | `racket ohjelma.rkt` |
| REPL | `racket`, DrRacket |
| Testit (`test`-alimoduulit) | `raco test .` |
| Käännä tavukoodiksi | `raco make ohjelma.rkt` |
| Makrojen laajennus | `raco expand ohjelma.rkt` |
| Paketit, dokumentaatio | `raco pkg install x`, `raco docs x` |

# Perussyntaksi

```{.scheme tiedosto="esimerkit/pikaopas.rkt" osa="perus"}
```

- Vain `#f` on epätosi. `'()`, `0` ja `""` ovat tosia.
- `eq?` oliot, `equal?` rakenne, `=` luvut.
- `1/3` on tarkka rationaaliluku, `0.33` liukuluku.
- Nimeämiskäytäntö: `tyhja?` predikaatti, `aseta!` muuttaa tilaa,
  `hash->list` muunnos.
- Ylätason lausekkeen arvo tulostuu, jos se ei ole `(void)`.

# Listat ja koosteet

```{.scheme tiedosto="esimerkit/pikaopas.rkt" osa="listat"}
```

| Kaava | Racket | Python | JS | Java Stream | Rust |
|-------|--------|--------|----|-------------|------|
| muunnos | `map` | `[f(x) for x in xs]` | `map` | `map` | `map` |
| suodatus | `filter` | `if` koost. | `filter` | `filter` | `filter` |
| kokoaminen | `foldl` | `reduce` | `reduce` | `reduce` | `fold` |
| laiska | `stream` | `yield` | `function*` | `Stream` | `Iterator` |

`for/list`, `for/sum`, `for/hash`, `for/fold`; `#:when`, `#:break`,
`#:final`. Kerro sekvenssin tyyppi: `in-list`, `in-range`, `in-hash`.

# Rekursio

- Haara jokaista datan tapausta kohti: `'()` ja `(cons x xs)`.
- Häntäkutsu ei kasvata pinoa (taattu). Kertymä = silmukkamuuttuja.
- Nimetty let: `(let kierros ([i 0] [acc '()]) ...)`.
- Python, Java ja JS eivät optimoi häntäkutsuja: syvä rekursio
  silmukaksi.

# Data

```{.scheme tiedosto="esimerkit/pikaopas.rkt" osa="data"}
```

- `struct` + `match` = summatyyppi (Rust `enum`, Kotlin `sealed`,
  Java `sealed` + `record`).
- Muuttumaton `hash`, `list`, `set`: päivitys O(log n), vanha versio
  säilyy.
- Muuttuva: `make-hash`, `vector`, `#:mutable`, `set!`, `box`.

# Sulkeumat ja funktiot

- `(λ (x) ...)`, `compose`, `curry`, `apply`, `const`, `identity`.
- Sulkeuma muistaa ympäristönsä. `for` luo kierroksittain uuden
  sidonnan (vrt. JS `var`, Python `lambda: i`).
- Funktiotehdas: funktio, joka palauttaa funktion.

# Makrot

```{.scheme tiedosto="esimerkit/pikaopas.rkt" osa="makro"}
```

- `define-syntax-rule`, `syntax-rules` (ellipsi `...`),
  `syntax-parse` (`x:id`, `e:expr`, virheilmoitukset).
- Hygieeninen: nimet eivät sekoitu (vrt. C:n esikääntäjä).
- Älä käytä makroa, jos funktio riittää.
- Puolilainaus: `` `(a ,x ,@xs) ``.

# Laiskuus

```{.scheme tiedosto="esimerkit/pikaopas.rkt" osa="laiska"}
```

- `racket/generator`: `generator`, `yield`, `in-producer`.
- `in-lines`, `in-port read`: syöte rivi tai lauseke kerrallaan.

# Virheet ja testit

```{.scheme tiedosto="esimerkit/pikaopas.rkt" osa="virheet"}
```

- Odotettu epäonnistuminen paluuarvona (`#f`), virhe poikkeuksena.
- Oma tyyppi: `(struct exn:fail:oma exn:fail (lisatieto))`.
- `(provide (contract-out [f (-> string? natural?)]))`: sopimus
  rajalla, virhe nimeää syyllisen.
- `(module+ test (require rackunit) (check-equal? (f 1) 2))`.

# Rakenne

- Funktionaalinen ydin, imperatiivinen kuori: `(tila, syöte) → (tila,
  tuloste)`.
- `parameterize`: dynaaminen sidonta (lokitaso, tulosteportti).
- Muistaminen vain puhtaille funktioille.
