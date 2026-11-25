# Paketointi ja jakelu

Yksittäinen skripti riittää omaan käyttöön. Kun työkalua käyttää koko
tiimi tai CI, se paketoidaan: asennus tuo komennon polulle,
riippuvuudet on lueteltu, versio on tiedossa ja asennuksen voi
toistaa. Pythonissa paketin kuvaus on yksi tiedosto, `pyproject.toml`.

Taito *Python* esittelee projektin rakenteen, virtuaaliympäristöt ja
`pyproject.toml`-tiedoston kentät. Tämä luku kertaa ne yhden
esimerkkipaketin avulla ja keskittyy siihen, mikä on komentorivityökalulle
erityistä: komennon sisääntulo, versio, asennus pipxillä ja paketin
rakenteen testaus. Luvun jälkeisten lukujen esimerkit ovat silti
yksittäisiä skriptejä, jotta jokaisen voi ajaa sellaisenaan.

## Projektin rakenne

Esimerkin paketti `lokikoonti` noudattaa *src-asettelua*:

```text
03-paketti/
├── pyproject.toml          paketin kuvaus
├── README.md
├── src/lokikoonti/
│   ├── __init__.py         versio
│   ├── __main__.py         python -m lokikoonti
│   └── cli.py              komentorivi
└── tests/test_paketti.py
```

src-hakemiston ansiosta testit eivät voi tuoda pakettia
työhakemistosta ohi asennuksen, joten ne testaavat samaa, mitä käyttäjä
saa.

## pyproject.toml

```{.toml tiedosto="esimerkit/03-paketti/pyproject.toml" osa="projekti"}
```

- `[build-system]` kertoo, millä paketti rakennetaan. setuptools on
  yleisin. hatchling ja flit ovat kevyempiä vaihtoehtoja, eikä
  valinnalla ole käyttäjälle merkitystä.
- `requires-python` estää asennuksen liian vanhaan Pythoniin.
  Esimerkiksi tyyppimerkintä `X | None` vaatii vähintään 3.10.
- `dependencies` luettelee ajonaikaiset riippuvuudet väljin
  versiorajoin (`numpy>=2.0`). Tarkat versiot kuuluvat sovelluksen
  lukitustiedostoon, eivät kirjaston kuvaukseen.
- `[project.scripts]` luo asennuksessa komennon `lokikoonti`, joka
  kutsuu funktiota `lokikoonti.cli:main` ja välittää sen paluuarvon
  käyttöjärjestelmälle.

Versio kysytään asennetun paketin metatiedoista. Kehityshakemistosta
ajettaessa paketti ei ole asennettu, joten varalla on paketin oma vakio:

```{.python tiedosto="esimerkit/03-paketti/src/lokikoonti/cli.py" osa="versio"}
```

`__main__.py` mahdollistaa ajon muodossa `python -m lokikoonti`, mikä on
kätevää, kun komento ei ole polulla:

```{.python tiedosto="esimerkit/03-paketti/src/lokikoonti/__main__.py"}
```

Muu komentorivi on tuttua argparsea:

```{.python tiedosto="esimerkit/03-paketti/src/lokikoonti/cli.py" osa="komento"}
```

## Asennus: venv ja pipx

```text
python3 -m venv .venv            # projektikohtainen ympäristö
. .venv/bin/activate
pip install -e '.[kehitys]'      # muokattava asennus + kehitystyökalut
lokikoonti --version

pipx install .                   # työkalu omaan ympäristöönsä
pipx install git+https://git.esimerkki.fi/tyokalut/lokikoonti.git
```

- **Virtuaaliympäristö (venv) ja muokattava asennus (`-e`)** ovat
  kehittäjän työtapa: riippuvuudet pysyvät erossa järjestelmän
  Pythonista, ja lähdekoodin muutokset näkyvät ilman uudelleenasennusta.
- **pipx** asentaa komentorivityökalun omaan venviinsä ja tuo komennon
  polulle. Se sopii työkaluille, joita käytetään projektista
  riippumatta.
- **Pyöräpaketti (wheel)** on valmiiksi rakennettu asennuspaketti:
  `python3 -m build` tuottaa hakemistoon `dist/` tiedostot, jotka voi
  julkaista sisäiseen pakettivarastoon.

Esimerkin paketti testataan kehityshakemistosta asentamatta sitä
(`PYTHONPATH=src`), koska testiympäristössä ei ole verkkoa
riippuvuuksien hakemiseen. Testit tarkistavat paketin rakenteen:

```{.python tiedosto="esimerkit/03-paketti/tests/test_paketti.py" osa="testit"}
```

Ensimmäinen testi varmistaa, että jokainen `[project.scripts]`-merkintä
osoittaa olemassa olevaan funktioon. Kirjoitusvirhe tässä kohdassa ei
näy ennen asennusta, ja silloin komento kaatuu käyttäjälle.

## Käytännössä

- **Yksi lähde versiolle.** Esimerkissä versio on kahdessa paikassa,
  ja testi pitää ne samoina. Vaihtoehto on dynaaminen versio, jonka
  rakennustyökalu lukee versionhallinnan tagista (setuptools-scm).
- **Työkalu riippuu vähästä.** Jokainen riippuvuus on asennettava
  kaikkialle, missä työkalua ajetaan, myös suljettuun
  suunnitteluympäristöön, jossa ei ole verkkoa. Vakiokirjasto riittää
  yllättävän pitkälle.
- **Lukitse sovellukset, älä kirjastoja.** Kirjaston `dependencies`
  sallii versiovälin. Sovelluksen tai CI-ympäristön tarkat versiot
  lukitaan erikseen (`pip freeze`, `uv.lock`, `requirements.txt`
  tiivisteineen).
- **Sudenkuoppa:** skripti, joka muokkaa `sys.path`-listaa löytääkseen
  omat moduulinsa. Se toimii vain yhdessä hakemistossa ja yhdellä
  koneella. Paketti ja asennus ratkaisevat saman ongelman
  pysyvästi.
- **Sudenkuoppa:** `pip install --user` tai `sudo pip install`
  järjestelmän Pythoniin. Ne rikkovat käyttöjärjestelmän omia
  Python-ohjelmia. Käytä venviä tai pipxiä.

## Itsearviointi

- Osaat kirjoittaa `pyproject.toml`-tiedoston, jossa on riippuvuudet,
  valinnaiset kehitysriippuvuudet ja komentorivin sisääntulo.
- Osaat perustella src-asettelun ja `__main__.py`-tiedoston.
- Osaat asentaa työkalun venviin muokattavana ja pipxillä
  komentorivityökaluksi.
- Osaat testata paketin rakenteen: sisääntulot ja versio.
