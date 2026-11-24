---
title: Python työkaluohjelmointiin
subtitle: Pikaopas · Python 3.12 · NumPy · matplotlib · pytest
---

# Työkalun runko

```{.python tiedosto="esimerkit/pikaopas.py" osa="runko"}
```

- `sys.exit(main())`: paluuarvo 0 onnistui, 1 tulos ei kelpaa, 2
  käyttövirhe (argparse).
- Tulokset `print`, diagnostiikka `logging` virhetulosteeseen.
- `type=funktio` tarkistaa ja muuntaa; virhe `ArgumentTypeError`.
- Alikomennot: `add_subparsers(required=True)` ja
  `set_defaults(toiminto=f)`.
- Suljettu putki: käsittele `BrokenPipeError` ennen `OSError`ia.

# Tekstimuodot

```{.python tiedosto="esimerkit/pikaopas.py" osa="re"}
```

| Tarve | Työkalu |
|-------|---------|
| Rivit kentiksi | `re.compile(r"...", re.VERBOSE)`, `(?P<nimi>...)` |
| Koko merkkijono | `fullmatch`; `match` = alusta; `search` = mistä vain |
| Monirivinen lohko | tilakone, generaattori, virhe kesken jääneestä |
| CSV | `csv.DictReader`, ei `split(",")` |
| TOML | `tomllib.load(f)`, tiedosto `"rb"`-tilassa |
| INI | `configparser`, `getint`, `getboolean` |
| JSON | `json.dumps(x, ensure_ascii=False, sort_keys=True)` |

# Binääridata

```{.python tiedosto="esimerkit/pikaopas.py" osa="struct"}
```

| Merkki | Merkitys |
|--------|----------|
| `<` `>` `!` | pieni-, iso-, verkkoendian; tiivis |
| `@` | alustan järjestys ja C:n kohdistus |
| `B H I Q` | u8 u16 u32 u64; pienet kirjaimet etumerkillisiä |
| `4s` | 4 tavua |

Muoto: taikasana, versio, pituus, CRC (`zlib.crc32`).
`memoryview(b)[a:b]` ja `.cast("h")` ilman kopiota.

# Tiedostot

```{.python tiedosto="esimerkit/pikaopas.py" osa="polut"}
```

- Lajittele aina: tiedostojärjestelmän järjestys vaihtelee.
- Atominen kirjoitus: `mkstemp(dir=kohde.parent)`, `fsync`,
  `os.replace`.
- `encoding="utf-8"` aina, lokeille `errors="replace"`.

# Aliprosessit

```{.python tiedosto="esimerkit/pikaopas.py" osa="aliprosessi"}
```

- Lista, ei merkkijonoa; `shell=True` vain `shlex.quote`lla.
- `timeout` aina; `TimeoutExpired` → lapsi on tapettu.
- Rinnakkain: `ThreadPoolExecutor(n).map(f, ajot)`.
- Python-alityökalu: `sys.executable`. Lokiin `shlex.join(komento)`.

# NumPy ja kuvaajat

```{.python tiedosto="esimerkit/pikaopas.py" osa="numpy"}
```

```{.tuloste tiedosto="esimerkit/pikaopas.odotettu"}
```

- Raakadata `int16`/`uint16`, laskenta `astype(np.float64)`.
- Broadcast: muodot oikealta, ulottuvuus sama tai 1.
- Viipale on näkymä; indeksilista ja maski kopioita.
- Satunnaisuus `rng = np.random.default_rng(siemen)`.
- Tietueet: `np.frombuffer(b, dtype=[("t", "<u4"), ("v", "<i2")])`.
- Kuvaaja: `Figure(figsize=(8, 3))`, `fig.add_subplot()`,
  `fig.savefig("x.pdf")`; ei `pyplot`ia työkalussa.

# Paketointi ja testaus

| Tehtävä | Komento |
|---------|---------|
| Ympäristö | `python3 -m venv .venv && . .venv/bin/activate` |
| Kehitysasennus | `pip install -e '.[kehitys]'` |
| Työkalu polulle | `pipx install .` |
| Komento | `[project.scripts] nimi = "paketti.cli:main"` |
| Tarkistus | `ruff check .`, `mypy --strict src tests` |
| Testit | `python3 -m pytest -q` |

pytest: `tmp_path`, `monkeypatch.setattr/setenv`, `capsys`,
`@pytest.mark.parametrize`, `pytest.raises(E, match=...)`,
tilannekuva tiedostoon ja päivitys ympäristömuuttujalla.
