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
6. Tiedostot ja hakemistot – `pathlib`, atominen kirjoitus, `shutil`
7. Aliprosessit – komento listana, aikarajat, pitkän ajon seuranta,
   rinnakkaiset ajot
8. NumPy mittausdatalle – tietotyypit, broadcast, maskit, analyysi,
   rakenteiset tietotyypit
9. Kuvaajat tiedostoon – matplotlibin olio-rajapinta
10. Testaus – kellon ja ympäristön eristäminen, parametrisointi,
    doctest, tilannekuvat
11. Lopuksi – nyrkkisäännöt ja lähteet

## Rakentaminen

```text
make testaa     # rakenne, esimerkit (ruff, mypy --strict, ajo), pytest
make pdf        # tutoriaali ja pikaopas PDF:ksi
make kuvat      # lukujen 8 ja 9 kuvat (commitoidaan)
```

Esimerkit tarvitsevat Python 3.12:n, NumPyn ja matplotlibin; testit
pytestin. Kehityskontti: `.devcontainer/python-tyokalut`.
Esimerkkien avaaminen kehityskontissa ja ajaminen: ks. [Kehitysympäristöt ja Dev Containers](../kehitysymparistot/), luku 2.

Lisenssi: CC BY-SA 4.0.
