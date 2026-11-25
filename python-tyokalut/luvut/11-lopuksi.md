# Lopuksi {.runko-lahteet}

## Nyrkkisäännöt

| Tilanne | Ratkaisu |
|---------|----------|
| Työkalun rajapinta | argparse, `main(argv) -> int`, `sys.exit(main())` |
| Tulos vai diagnostiikka | tulos tulosteeseen, diagnostiikka `logging`illa virhetulosteeseen |
| Onnistuminen | paluuarvo 0; virheet dokumentoiduilla arvoilla |
| Syötteen muoto | jäsennä reunalla tyypitetyiksi olioiksi |
| Monirivinen raportti | tilakone, joka huomaa keskeneräisen lohkon |
| CSV, JSON, TOML, INI | vakiokirjaston jäsentimet, ei `split` |
| Binääridata | `struct` kiinteällä tavujärjestyksellä, `memoryview`, NumPyn `frombuffer` |
| Oma tiedostomuoto | taikasana, versio, pituus, tarkistussumma |
| Polut | `pathlib`, lajiteltu läpikäynti, suhteessa skriptiin |
| Tiedosto jota joku lukee | atominen kirjoitus: tilapäistiedosto ja `os.replace` |
| Ulkoinen ohjelma | lista ilman komentotulkkia, aikaraja, tulkitse paluuarvo ja loki |
| Pitkä ajo | `Popen`, tuloste rivi kerrallaan, oma prosessiryhmä ja siivous `finally`-lohkossa |
| Monta ajoa | `ThreadPoolExecutor`, tulokset syötteen järjestyksessä |
| Numeerinen data | NumPy, ei silmukoita, tietotyyppi tietoisesti |
| Kuvaaja | `Figure`-olio ja `savefig`, ei `pyplot`ia työkalussa |
| Jakelu | `pyproject.toml`, src-asettelu, venv ja pipx |
| Luotettavuus | `mypy --strict`, ruff, pytest, tilannekuvat raporteille |
| Ohje | modulin dokumentaatiomerkkijono `--help`in kuvauksena, paluuarvot mukana |

## Mallit

- **Ohut `main`, puhtaat funktiot:** syöte, tuloste ja paluuarvo
  kytketään yhdessä paikassa, ja kaikki muu on testattavissa
  suoraan.
- **Jäsennä, älä validoi:** muunna syöte kerran tyypitetyksi olioksi,
  joka on luonnissa tarkistettu.
- **Kaikki virheet kerralla:** tarkista koko syöte ja raportoi kaikki
  virheet ennen kuin kirjoitat mitään.
- **Atominen julkaisu:** kirjoita sivuun ja vaihda nimi.
- **Eristetyt sivuvaikutukset:** aika, satunnaisuus ja ympäristö
  korvattavina, jotta tulokset toistuvat.

## Lähteet ja lisälukemista

- **Pythonin dokumentaatio** (<https://docs.python.org/3/>):
  moduulien `argparse`, `logging`, `re`, `struct`, `pathlib`,
  `subprocess` ja `concurrent.futures` sivut. Lisäksi *Logging HOWTO*
  ja *Regular Expression HOWTO* -oppaat.
- **Python Packaging User Guide** (<https://packaging.python.org>):
  `pyproject.toml`, rakennustyökalut, pipx ja julkaisu.
- **NumPyn dokumentaatio** (<https://numpy.org/doc/>): *Broadcasting*,
  *Structured arrays* ja *Random Generator* -sivut.
- **Matplotlibin dokumentaatio** (<https://matplotlib.org>): *Quick
  start guide* ja olio-rajapinta (`Figure`, `Axes`).
- **pytestin dokumentaatio** (<https://docs.pytest.org>): fixturet,
  parametrisointi ja `monkeypatch`.
- **mypy** (<https://mypy.readthedocs.io>) ja **ruff**
  (<https://docs.astral.sh/ruff/>): tarkistimien säännöt ja
  asetukset.
- **Command Line Interface Guidelines** (<https://clig.dev>):
  komentorivityökalujen suunnitteluperiaatteet.

## Mihin tästä eteenpäin

Taito *EDA-työkaluketjujen automatisointi* soveltaa näitä välineitä
laitteistosuunnittelun
työkaluketjuihin: synteesi- ja ajoitusraporttien jäsentämiseen,
regressioajoihin ja rekisterikuvauksista generoituun koodiin. Taito
*Python ja C/C++ yhteen* jatkaa suorituskykyyn: kun NumPy ei riitä,
osa työkalusta kirjoitetaan C++:lla ja kutsutaan Pythonista. Taito
*Laitteiston verifiointi* käyttää Pythonia testipenkkien
kirjoittamiseen (cocotb). Taito *Tekninen dokumentaatio* jatkaa
dokumentaatiomerkkijonoista työkalun käyttöohjeeseen ja
rajapintaviitteeseen.

## Lisenssi

Tämä tutoriaali ja sen esimerkkikoodit on lisensoitu Creative Commons
Nimeä–JaaSamoin 4.0 Kansainvälinen -lisenssillä (CC BY-SA 4.0,
<https://creativecommons.org/licenses/by-sa/4.0/deed.fi>). Teosta saa
kopioida, levittää ja muokata, kunhan alkuperäinen lähde mainitaan ja
muokatut versiot jaetaan samalla lisenssillä.
