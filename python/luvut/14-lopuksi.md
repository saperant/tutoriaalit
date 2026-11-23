# Lopuksi: käytännöt ja lähteet {.runko-kaytannot .runko-lahteet}

Tämä luku kokoaa lukujen *Käytännössä*-osioiden tärkeimmät idiomit ja
nyrkkisäännöt sekä luettelee lähteet ja kirjastot, joilla työtä voi
jatkaa.

## Idiomit ja mallit

| Malli | Pythonissa | Luku |
|-------|------------|------|
| EAFP | `try`/`except` tarkistuksen sijaan; ei kilpatilanteita | 10 |
| Vartija-arvo | `None` tai `object()` muuttuvan oletusarvon sijaan | 3 |
| Kontekstinhallinta (RAII) | `with`, `@contextmanager`, `ExitStack` | 7 |
| Generaattoriputki | `Iterable` sisään, `Iterator` ulos, vakiomuisti | 6 |
| Arvo-olio | `@dataclass(frozen=True, slots=True)` validoinnilla | 8 |
| Rakenteellinen rajapinta | `typing.Protocol`, ei perintää | 8, 11 |
| Kattava tilakone | `Enum` + `match` + `assert_never` | 8 |
| Jäsennä rajalla | ulkoinen data tyypitetyksi heti saapuessa | 9 |
| Poikkeusten käännös | `raise SovellusVirhe(...) from virhe` kerroksen rajalla | 10 |
| Riippuvuuksien kääntäminen | protokolla käyttäjän puolella, kokoaminen pääohjelmassa | 11 |
| Dekoraattori | uudelleenyritys, välimuisti, lokitus funktion ympärille | 4 |
| Atominen tallennus | väliaikainen tiedosto + `os.replace` | 7 |
| Rakenteellinen samanaikaisuus | `TaskGroup`, `with ThreadPoolExecutor()` | 12 |

## Nyrkkisäännöt

**Tietomalli ja tyypit**

- Sijoitus ei kopioi. Funktio joko jättää argumenttinsa ennalleen tai
  kertoo nimellään muuttavansa sitä.
- Muuttumaton oletuksena: monikko, `frozenset`, jäädytetty dataluokka.
- Ei muuttuvia oletusarvoja; `is None`, ei `== None`.
- `Decimal` rahalle, `pathlib` poluille, `encoding="utf-8"` tiedostoille.
- Kaikki julkiset rajapinnat tyypitetään ja tarkistetaan `mypy --strict`
  -tilassa. `Any` ei vuoda rajan yli.

**Rakenne**

- Kokoelma valitaan operaatioiden mukaan: `set` jäsenyydelle, `deque`
  jonolle, `dict` haulle, `Counter` ja `defaultdict` ryhmittelyyn.
- Iteroidaan suoraan (`enumerate`, `zip(strict=True)`, `items`),
  ei indekseillä.
- Generaattori virtaavalle datalle, lista kun tarvitaan pituus tai
  monta läpikäyntiä.
- Pienet funktiot, vartijalauseet ja avainsanaparametrit asetuksille.
- Moduuleissa ei sivuvaikutuksia tuonnissa; käynnistys `main`-funktiossa.

**Virheet ja resurssit**

- Jokainen resurssi `with`-lauseeseen.
- Siepataan tarkasti ja vain siellä, missä virheelle voi tehdä jotain.
  Leveä sieppaus vain ylimmällä tasolla, ja silloin lokitetaan.
- Oma kantapoikkeus, ketjutus `from`-osalla.

**Suorituskyky**

- Mittaa ensin (cProfile, py-spy, `timeit`).
- Algoritmi ja tietorakenne ennen mikro-optimointia.
- Työ C-tasolle: sisäänrakennetut funktiot, koostelausekkeet,
  `itertools`, NumPy.
- Odotus säikeillä tai `asyncio`-silmukalla, laskenta prosesseilla tai
  C-kirjastoilla.

## Hinnat yhdellä silmäyksellä

| Halpaa | Kallista |
|--------|----------|
| `dict`- ja `set`-haku, `list.append`, `deque` molemmista päistä | `x in lista`, `lista.pop(0)`, `lista.insert(0, x)` |
| sisäänrakennetut funktiot, koostelausekkeet | Python-tason silmukka alkio kerrallaan |
| `try` ilman poikkeusta | pinojäljen muotoilu, `deepcopy` |
| `str.join` | merkkijonon kasvatus `+=` silmukassa |
| paikallinen nimi | attribuuttihaku ja funktiokutsu kuumassa silmukassa |
| säikeet I/O:hon, korutiinit | säikeet Python-laskentaan (GIL) |
| `__slots__`, `array`, NumPy | miljoonat tavalliset oliot (`__dict__`) |

## Lähteet

**Virallinen dokumentaatio**

- Python-dokumentaatio: <https://docs.python.org/3/>; erityisesti
  *Language Reference* (tietomalli), *Library Reference* ja
  *What's New* -sivut kustakin versiosta.
- PEP-dokumentit: <https://peps.python.org/>. Keskeisiä ovat PEP 8
  (tyyli), PEP 20 (Zen), PEP 484 (tyyppivihjeet), PEP 621
  (`pyproject.toml`), PEP 634–636 (`match`), PEP 695 (tyyppiparametrit)
  ja PEP 703 (GIL-vapaa Python).
- Python Packaging User Guide: <https://packaging.python.org/>.
- typing-dokumentaatio ja -opas: <https://typing.python.org/>.

**Työkalut**

- pytest: <https://docs.pytest.org/>
- mypy: <https://mypy.readthedocs.io/>
- Ruff: <https://docs.astral.sh/ruff/>
- uv: <https://docs.astral.sh/uv/>
- py-spy: <https://github.com/benfred/py-spy>

**Kirjat**

- Luciano Ramalho: *Fluent Python*, 2. painos, O'Reilly 2022.
  Pythonin tietomalli, protokollat ja idiomit perusteellisesti.
- Brett Slatkin: *Effective Python*, 3. painos, Addison-Wesley 2024.
  Lyhyitä, perusteltuja käytäntöjä.
- Harry Percival, Bob Gregory: *Architecture Patterns with Python*,
  O'Reilly 2020. Kerrosrakenne, riippuvuuksien kääntäminen ja testaus.
- Micha Gorelick, Ian Ozsvald: *High Performance Python*, 2. painos,
  O'Reilly 2020.

**Kirjastot**

| Alue | Kirjastoja |
|------|------------|
| HTTP-asiakas | httpx, requests |
| Verkkopalvelut | FastAPI, Django, Flask |
| Datan validointi | Pydantic, msgspec, attrs |
| Tietokannat | SQLAlchemy, psycopg, asyncpg |
| Numeerinen laskenta ja data | NumPy, pandas, Polars, SciPy |
| Komentorivi | argparse (standardikirjasto), Typer, Click |
| Testaus | pytest-cov, Hypothesis (ominaisuuspohjainen testaus) |

Taitopuun jatkotaidot: *Python ja C/C++ yhteen* laajennuksiin ja
suorituskykyyn, *Rinnakkaisohjelmointi* yleisiin rinnakkaisuuden
malleihin ja *Käännösjärjestelmät, testaus ja CI* projektin
automaatioon.
