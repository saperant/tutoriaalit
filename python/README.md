# Python

Tiivis suomenkielinen johdatus idiomaattiseen ja ammattimaiseen
Pythoniin ohjelmoinnin osaavalle. Esimerkit vaativat Python 3.12:n.
Valmiit dokumentit: [python.pdf](https://saperant.github.io/tutoriaalit/materiaalit/python.pdf) ja pikaopas
[python-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/python-pikaopas.pdf).

## Sisältö

1. Johdanto – käyttökohteet, versiot, työkalut, ensimmäinen ohjelma
2. Python kokeneelle – vertailu C++:aan, Javaan ja JavaScriptiin,
   hinnat, sudenkuopat
3. Tietomalli, tyypit ja muotoilu – viittaukset, muuttuvuus,
   oletusarvoansa, kopiointi, f-merkkijonot, syötteen jäsennys
4. Ohjausrakenteet ja funktiot – `match`, parametrien lajit,
   sulkeumat, dekoraattorit, `functools.cache`
5. Kokoelmat ja merkkijonot – hinnat, `Counter`, `defaultdict`,
   `deque`, lajittelu, `re`
6. Iteraattorit ja generaattorit – protokolla, generaattoriputket,
   `itertools`
7. Muistinhallinta ja resurssit – viitelaskenta, `with`,
   `@contextmanager`, `ExitStack`, atominen tallennus
8. Luokat, dataluokat ja protokollat – erikoismetodit, `Protocol`,
   `ABC`, `Enum`
9. Tyypitys – geneerisyys (3.12), `TypedDict`, `NewType`, mypy
10. Virheenkäsittely – EAFP, poikkeushierarkiat, ketjutus,
    `ExceptionGroup`
11. Modulit, paketit ja projektin rakenne – kerrokset,
    `pyproject.toml`, virtuaaliympäristöt
12. Rinnakkaisuus – GIL, säikeet, prosessit, `asyncio`
13. Työkalut – pytest, ruff, mypy, pdb, `logging`, cProfile
14. Lopuksi – käytännöt, hinnat ja lähteet

## Rakentaminen

```text
make testaa   # ruff, mypy --strict ja esimerkkien ajo
make pdf      # rakentaa python.pdf:n ja python-pikaopas.pdf:n
```

Kehityskontti on hakemistossa `.devcontainer/python`. Riippuvuudet on
lueteltu repositorion juuren README-tiedostossa.
