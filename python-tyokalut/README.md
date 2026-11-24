# Python työkaluohjelmointiin

Tiivis suomenkielinen tutoriaali insinöörin työkalujen kirjoittamisesta
Pythonilla: komentorivityökalut, paketointi, teksti- ja binäärimuotojen
jäsentäminen, tiedostot, ulkoisten työkalujen ohjaus, NumPy, kuvaajat
ja testaus. Esimerkit liittyvät laitteisto- ja EDA-ympäristöihin.
Valmiit dokumentit:
[python-tyokalut.pdf](https://saperant.github.io/tutoriaalit/materiaalit/python-tyokalut.pdf)
ja pikaopas
[python-tyokalut-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/python-tyokalut-pikaopas.pdf).

## Sisältö

1. Johdanto – hyvän komentorivityökalun ominaisuudet
2. Komentorivityökalut – argparse, alikomennot, tarkistus, lokitus,
   paluuarvot ja putket
3. Paketointi ja jakelu – `pyproject.toml`, src-asettelu, venv, pipx
4. Tekstimuotojen jäsentäminen – säännölliset lausekkeet, tilakone,
   CSV → C-otsake, TOML, INI, JSON
5. Binäärimuodot – `struct`, tavujärjestys, bittikentät, oma
   tiedostomuoto tarkistussummineen
6. Tiedostot ja hakemistot – `pathlib`, atominen kirjoitus
7. Aliprosessit – komento listana, aikarajat, rinnakkaiset ajot
8. NumPy mittausdatalle – tietotyypit, broadcast, maskit, analyysi,
   rakenteiset tietotyypit
9. Kuvaajat tiedostoon – matplotlibin olio-rajapinta
10. Tyyppivihjeet ja testaus – `TypedDict`, pytest, fixturet,
    tilannekuvat
11. Lopuksi – nyrkkisäännöt ja lähteet

## Rakentaminen

```text
make testaa     # rakenne, esimerkit (ruff, mypy --strict, ajo), pytest
make pdf        # tutoriaali ja pikaopas PDF:ksi
make kuvat      # luvun 9 kuva (commitoidaan)
```

Esimerkit tarvitsevat Python 3.12:n, NumPyn ja matplotlibin; testit
pytestin. Kehityskontti: `.devcontainer/python-tyokalut`.

Lisenssi: CC BY-SA 4.0.
