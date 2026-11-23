---
title: Ohjelmoinnin perusteet
subtitle: Pikaopas · Python 3.12
---

# Työkalut

| Tarkoitus | Komento |
|-----------|---------|
| Aja ohjelma | `python3 ohjelma.py`, syöte tiedostosta `< syote.txt` |
| Kokeile | `python3` (REPL), lopetus `exit()` |
| Tarkista | `ruff check .` ja `mypy .` |
| Testaa | `pytest -q` (tiedostot `test_*.py`, funktiot `test_*`) |
| Debuggaa | `breakpoint()` koodiin, `print(f"{x=}")` |
| Ympäristö | `python3 -m venv .venv`, `source .venv/bin/activate` |
| Asenna | `pip install kirjasto` |

# Arvot ja lausekkeet

```{.python tiedosto="esimerkit/pikaopas.py" osa="arvot"}
```

| Muotoilu | Tulos |
|----------|-------|
| `f"{x:.2f}"` | `3.14` |
| `f"{n:>5}"`, `f"{s:<8}"` | tasaus oikealle, vasemmalle |
| `f"{n:03d}"` | `007` |
| `f"{x=}"` | `x=3.14` (debuggaus) |

- `input()` palauttaa aina `str`:n: muunna `int()`/`float()`.
- Raha sentteinä (`int`) tai `Decimal`, ei `float`.

# Ohjausrakenteet

```{.python tiedosto="esimerkit/pikaopas.py" osa="ohjaus"}
```

- Vertailut `== != < <= > >=`, ketju `1 <= x <= 5`,
  `and or not`, `x in kokoelma`.
- Epätosia: `0`, `""`, `[]`, `{}`, `None`.
- `range(5)` = 0–4, `range(1, 6)` = 1–5, `range(0, 10, 2)`.

# Funktiot

```{.python tiedosto="esimerkit/pikaopas.py" osa="funktiot"}
```

- Yksi tehtävä, palauttaa tuloksen eikä tulosta.
- Ei globaaleja muuttujia; arvo sisään parametrina, ulos `return`.

# Kokoelmat

```{.python tiedosto="esimerkit/pikaopas.py" osa="kokoelmat"}
```

| Tarve | Kokoelma |
|-------|----------|
| jono, järjestys, toistot | lista `[...]` |
| haku avaimella | sanakirja `{k: v}` |
| jäsenyys, ei toistoja | joukko `{...}`, tyhjä `set()` |
| kiinteä ryhmä | monikko `(...)` tai dataluokka |

- `kopio = lista` ei kopioi: `lista.copy()`.
- `sorted(x, key=..., reverse=True)` palauttaa uuden listan.

# Merkkijonot

```{.python tiedosto="esimerkit/pikaopas.py" osa="merkkijonot"}
```

`strip lower upper title split join replace startswith endswith find
partition isdigit`. Merkkijono on muuttumaton: metodit palauttavat
uuden.

# Tiedostot

```{.python tiedosto="esimerkit/pikaopas.py" osa="tiedostot"}
```

- Tilat: `"r"` luku, `"w"` uusi/tyhjennys, `"a"` lisäys.
- CSV: `csv.DictReader(f, delimiter=";")`, JSON: `json.load(f)`.

# Virheet

```{.python tiedosto="esimerkit/pikaopas.py" osa="virheet"}
```

| Poikkeus | Syy |
|----------|-----|
| `ValueError` | kelvoton arvo: `int("abc")` |
| `TypeError` | väärä tyyppi: `"a" + 1` |
| `KeyError`, `IndexError` | avain tai indeksi puuttuu |
| `FileNotFoundError` | tiedostoa ei ole |

- Virheilmoitus luetaan alhaalta ylös.
- `raise ValueError(f"virheellinen summa: {s!r}")`.
- Ei paljasta `except:` eikä `except ...: pass`.

# Luokat

```{.python tiedosto="esimerkit/pikaopas.py" osa="luokat"}
```

- `class Tili:` ja `__init__(self, ...)` invariantteineen.
- Oma poikkeus: `class KateEiRiita(Exception): ...`
- Koostaminen ennen periytymistä.

# Modulit

| Rakenne | Käyttö |
|---------|--------|
| `import math` | `math.ceil(x)` |
| `from rahat import euroina` | oma moduli `rahat.py` |
| `if __name__ == "__main__":` | ajo vain ohjelmana |

Standardikirjasto: `math statistics random datetime pathlib csv json
sys collections re`.

# Testit

| Rakenne | Merkitys |
|---------|----------|
| `assert f(2) == 4` | tarkistus |
| `@pytest.mark.parametrize("x", [...])` | sama testi monella syötteellä |
| `with pytest.raises(ValueError):` | odotettu poikkeus |

Testaa: tunnettu tulos, rajatapaukset, virheelliset syötteet ja
jokainen löydetty virhe.
