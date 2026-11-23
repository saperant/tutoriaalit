---
title: Python
subtitle: Pikaopas kokeneelle kehittäjälle · Python 3.12
---

# Työkalut

| Tarkoitus | Komento |
|-----------|---------|
| Ympäristö | `python3 -m venv .venv && source .venv/bin/activate` |
| Asennus | `pip install -e ".[dev]"` tai `uv sync` |
| Tarkistus | `ruff check --fix .`, `ruff format .`, `mypy --strict src` |
| Testit | `pytest -q`, `-x`, `-k nimi`, `--lf`, `--pdb` |
| Debuggaus | `breakpoint()`; pdb: `n`, `s`, `c`, `p x`, `w`, `q` |
| Profilointi | `python -m cProfile -s cumtime x.py`, `py-spy top` |
| Mikromittaus | `python -m timeit "sum(range(1000))"` |
| Tuontiajat | `python -X importtime -c "import x"` |

# Perusidiomit

- Totuusarvo: tyhjä, `0`, `""`, `None` ovat epätosia: `if rivit:`.
- `==` arvo, `is` identiteetti (vain `None`ille). `0 <= i < n`.
- `/` aina `float`, `//` lattiajako, `int` ei vuoda yli.
- Purku: `a, *loput = xs`; vaihto `a, b = b, a`.
- Iterointi: `enumerate`, `zip(strict=True)`, `d.items()`, `reversed`.

```{.python tiedosto="esimerkit/pikaopas.py" osa="perus"}
```

| Määre | Tulos | Määre | Tulos |
|-------|-------|-------|-------|
| `{x:>8}` | oikealle 8 | `{x:.2f}` | 2 desimaalia |
| `{x:,}` | tuhaterotin | `{x:.1%}` | prosentti |
| `{x!r}` | `repr` | `{x=}` | lauseke ja arvo |
| `{x:08b}` | binääri | `{d:%d.%m.%Y}` | päiväys |

# Tietomalli

- Sijoitus sitoo nimen olioon, ei kopioi. Parametri on uusi nimi
  samalle oliolle.
- Muuttumattomat: `int float str bytes tuple frozenset`. Muuttuvat:
  `list dict set` ja tavalliset oliot. Avaimen on oltava hajautettava.
- `copy.copy` matala, `copy.deepcopy` syvä kopio.
- Ei muuttuvia oletusarvoja: `def f(x: list[int] | None = None)`.

# Luokat ja rajapinnat

```{.python tiedosto="esimerkit/pikaopas.py" osa="luokat"}
```

- `frozen=True`: muuttumaton ja hajautettava; `order=True`: vertailut;
  `slots=True`: vähemmän muistia. Kopio muutoksella: `replace(o, x=1)`.
- `Protocol` rakenteelliselle rajapinnalle, `ABC` jaetulle toteutukselle.
- `Enum` + `match` + `assert_never` = kattava tilakone.
- `@property`, `@classmethod` (vaihtoehtoinen konstruktori).

# Iteraattorit ja resurssit

```{.python tiedosto="esimerkit/pikaopas.py" osa="iteraattorit"}
```

- Generaattori kuluu: toinen läpikäynti on tyhjä.
- `itertools`: `batched`, `pairwise`, `accumulate`, `groupby`
  (lajittele ensin), `islice`, `chain`.
- Jokainen resurssi `with`-lauseeseen; dynaaminen määrä `ExitStack`.

# Virheet

```{.python tiedosto="esimerkit/pikaopas.py" osa="virheet"}
```

```{.tuloste tiedosto="esimerkit/pikaopas.odotettu"}
```

- EAFP: `try` on ilmainen (3.11+), poikkeus halpa. Ei kilpatilanteita.
- Oma kantapoikkeus; `raise Uusi(...) from virhe` säilyttää syyn.
- `try` pieneksi, `except` tarkaksi; `except*` poikkeusryhmille.

# Tyypitys

| Merkintä | Merkitys |
|----------|----------|
| `Iterable[T]`, `Sequence[T]`, `Mapping[K, V]` | parametrit |
| `list[T]`, `dict[K, V]` | paluuarvot |
| `def f[T](x: T) -> T` | geneerinen funktio (3.12) |
| `class Jono[T]:` | geneerinen luokka (3.12) |
| `def f[T: Vertailtava]` | rajattu tyyppimuuttuja |
| `type Id = int` | tyyppialias (3.12) |
| `Literal`, `TypedDict`, `NewType` | ulkoisen datan tyypit |
| `Callable[[int], str]`, `Self` | kutsuttava, oma luokka |

Yhdiste kirjoitetaan `A | B`; puuttuva arvo `str | None` kavennetaan
ehdolla `if x is not None:`.

# Rinnakkaisuus

| Työ | Väline |
|-----|--------|
| I/O, estävät kirjastot | `ThreadPoolExecutor` |
| Tuhansia yhteyksiä | `asyncio`, `TaskGroup`, `Semaphore` |
| Python-laskenta | `ProcessPoolExecutor` + `__main__`-vartija |
| Numeerinen laskenta | NumPy (vektorointi) |

GIL: vain yksi säie suorittaa Python-koodia kerrallaan (paitsi
GIL-vapaa 3.13t/3.14t). `+=` ei ole atominen: lukko tai ei jaettua tilaa.

# Hinnat

| Halpaa | Kallista |
|--------|----------|
| `dict`/`set`-haku, `append`, `deque` | `x in lista`, `pop(0)`, `insert(0, x)` |
| sisäänrakennetut, koostelausekkeet | Python-silmukka alkio kerrallaan |
| `try` ilman poikkeusta | pinojälki, `deepcopy` |
| `"".join(osat)` | `s += osa` silmukassa |
| `__slots__`, `array`, NumPy | miljoonat oliot `__dict__`-sanakirjoineen |

# Sudenkuopat

- Muuttuva oletusarvo; `[[0] * 3] * 3` jakaa sisälistan.
- Sulkeuma sitoo nimen, ei arvoa: `lambda i=i: i`.
- `except Exception: pass`; `assert` syötteen tarkistukseen (`-O`).
- `rstrip(".txt")` poistaa merkkejä; käytä `removesuffix`.
- Joukon tai `set`-iteroinnin järjestys vaihtelee ajosta toiseen.
- `float` rahalle; `Decimal(0.1)` liukuluvusta (käytä `"0.1"`).
- Estävä kutsu korutiinissa; säikeet laskentaan.
- Moduuli, jonka nimi peittää standardikirjaston (`json.py`).
