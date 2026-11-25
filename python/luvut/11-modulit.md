# Modulit, paketit ja projektin rakenne {.runko-modulit}

Python-ohjelma koostuu moduuleista: jokainen `.py`-tiedosto on moduuli
ja jokainen hakemisto, jossa on moduuleja, voi olla paketti. Tässä
luvussa käsitellään tuontijärjestelmän toiminta, ohjelman jakaminen
kerroksiin, projektin rakenne, `pyproject.toml`, virtuaaliympäristöt ja
riippuvuuksien hallinta. Yleiset käännös- ja CI-käytännöt ovat taidossa
*Käännösjärjestelmät, testaus ja CI*.

## Miten import toimii

`import malli` etsii moduulin hakupolulta `sys.path`, jonka
ensimmäinen alkio on käynnistetyn skriptin hakemisto. Löydetty moduuli
suoritetaan kerran ylhäältä alas, ja tuloksena syntyvä moduuliolio
tallennetaan `sys.modules`-välimuistiin. Seuraavat tuonnit palauttavat
saman olion. Tästä seuraa:

- Moduulitason koodi ajetaan tuonnin yhteydessä. Tiedostojen
  lukeminen, verkkoyhteydet ja raskas alustus moduulitasolla hidastavat
  jokaista tuojaa ja vaikeuttavat testausta.
- `if __name__ == "__main__":` erottaa käynnistyksen tuonnista: kun
  tiedosto ajetaan ohjelmana, sen `__name__` on `"__main__"`, ja kun se
  tuodaan, moduulin nimi.
- Kiertävä tuonti (A tuo B:n, joka tuo A:n) näkee puoliksi suoritetun
  moduulin, ja nimiä puuttuu. Se on merkki kerrosrakenteen
  rikkoutumisesta.
- `from malli import Tuote` sitoo nimen tuontihetken olioon. Jos
  moduulin nimi sidotaan myöhemmin uudelleen, tuoja ei näe muutosta.

Paketti on hakemisto, jossa on `__init__.py`. Paketin sisällä
käytetään suhteellisia tuonteja (`from .malli import Tuote`) tai
absoluuttisia paketin nimen kautta (`from varasto.malli import Tuote`).
`__all__` luettelee moduulin julkisen rajapinnan: se määrää, mitä
`from moduuli import *` tuo, ja dokumentoi lukijalle ja työkaluille,
mitkä nimet ovat julkisia.

## Kerrosrakenne

Esimerkkiohjelma on jaettu neljään moduuliin. Riippuvuudet kulkevat
yhteen suuntaan: `main` → `palvelu` → `malli`, ja `muisti` → `malli`.

```{.dot otsikko="Moduulien tuonnit (yhtenäiset nuolet). `muisti` toteuttaa moduulin `palvelu` määrittelemän protokollan tuomatta sitä, joten kumpikaan ei riipu toisesta."}
digraph {
  rankdir=LR; nodesep=0.7; ranksep=0.6;
  main [label="main.py\nkokoaa osat"];
  palvelu [label="palvelu.py\nVarastopalvelu\nprotokolla Tuotevarasto"];
  muisti [label="muisti.py\nMuistivarasto"];
  malli [label="malli.py\nTuote, VarastoVirhe"];
  main -> palvelu [label="tuo"];
  main -> muisti [label="tuo"];
  palvelu -> malli [label="tuo"];
  muisti -> malli [label="tuo"];
  muisti -> palvelu [style=dashed, label="  toteuttaa\n  protokollan"];
  { rank=same; palvelu; muisti; }
}
```

Toimialan tyypit eivät riipu mistään:

```{.python tiedosto="esimerkit/11-varasto/malli.py"}
```

Sovelluslogiikka määrittelee tarvitsemansa rajapinnan protokollana
(luku 8) eikä tunne toteutusta:

```{.python tiedosto="esimerkit/11-varasto/palvelu.py"}
```

Toteutus on oma moduulinsa. Se toteuttaa protokollan perimättä sitä,
joten `palvelu` ei riipu `muisti`-moduulista. Tietokantaversio olisi
toinen moduuli samalla rajapinnalla:

```{.python tiedosto="esimerkit/11-varasto/muisti.py"}
```

Pääohjelma kokoaa osat yhteen ja on ainoa paikka, joka tuntee kaikki
moduulit:

```{.python tiedosto="esimerkit/11-varasto/main.py"}
```

```{.tuloste tiedosto="esimerkit/11-varasto.odotettu"}
```

Malli on nimeltään *riippuvuuksien kääntäminen* (*dependency
inversion*): korkean tason logiikka määrittelee rajapinnan ja matalan
tason toteutus mukautuu siihen. Kokoamispaikka (*composition root*)
on pääohjelma. Testi voi antaa palvelulle valevaraston ilman
kirjastoja tai `mock.patch`-temppuja. Pythonissa riippuvuudet
välitetään yleensä konstruktorin parametreina; erillistä
riippuvuusinjektiokehystä tarvitaan harvoin.

Esimerkki on tavallinen hakemisto, jonka moduulit löytyvät, koska
`main.py` käynnistetään samasta hakemistosta. Oikeassa projektissa
moduulit kuuluvat pakettiin.

## Projektin rakenne

Kirjaston tai sovelluksen suositeltu rakenne on *src-rakenne*:

```text
varasto/
├── pyproject.toml
├── README.md
├── src/
│   └── varasto/
│       ├── __init__.py
│       ├── __main__.py      # python -m varasto
│       ├── malli.py
│       ├── palvelu.py
│       └── muisti.py
└── tests/
    ├── test_palvelu.py
    └── conftest.py          # pytestin yhteiset kiintopisteet
```

`src`-hakemisto estää vahingossa tapahtuvan tuonnin työhakemistosta:
testit ajetaan asennettua pakettia vasten, joten pakkausvirheet
paljastuvat. `__main__.py` tekee paketista ajettavan komennolla
`python -m varasto`.

Projektin kaikki asetukset ovat `pyproject.toml`-tiedostossa (PEP 621):

```text
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "varasto"
version = "1.2.0"
requires-python = ">=3.12"
dependencies = ["httpx>=0.27", "pydantic>=2.6,<3"]

[project.optional-dependencies]
dev = ["pytest>=8", "mypy>=1.10", "ruff>=0.5"]

[project.scripts]
varasto = "varasto.__main__:main"    # komentorivityökalu

[tool.ruff.lint]
select = ["E", "F", "B", "UP", "SIM"]

[tool.mypy]
strict = true
```

`[build-system]` kertoo, millä paketti rakennetaan (hatchling,
setuptools, flit, pdm-backend). `dependencies` luettelee
ajonaikaiset riippuvuudet väljillä rajoilla, jotta paketti sopii
yhteen muiden kanssa. `[tool.*]`-osiot ovat työkalujen asetuksia.
Tämän tutoriaalin esimerkkien tarkistusasetukset ovat samassa
muodossa paketin juuren `pyproject.toml`-tiedostossa (luku 9).

## Virtuaaliympäristöt ja riippuvuudet

Jokaisella projektilla on oma *virtuaaliympäristönsä*: hakemisto, jossa
on oma tulkkilinkki ja omat asennetut paketit. Järjestelmän
Pythoniin ei asenneta paketteja; Debian ja Ubuntu estävät sen
oletuksena (PEP 668).

```text
python3 -m venv .venv          # luo ympäristö
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -e ".[dev]"        # projekti muokattavana + kehitystyökalut
pip freeze > requirements.lock # tarkat versiot talteen
```

`pip install -e` asentaa projektin *muokattavana*: lähdekoodin
muutokset näkyvät ilman uudelleenasennusta. Sovellukselle (ei
kirjastolle) lukitaan tarkat versiot, jotta jokainen asennus on sama.
Nykyaikaiset työkalut kuten *uv*, Poetry ja PDM hoitavat ympäristön,
lukitustiedoston ja asennuksen yhdellä komennolla; esimerkiksi
`uv sync` luo ympäristön ja asentaa `uv.lock`-tiedoston mukaiset versiot
sekunneissa. Valinta on projektikohtainen, mutta `pyproject.toml` on
kaikille yhteinen.

Paketti julkaistaan rakentamalla *wheel*-tiedosto (`python -m build`
tai `uv build`) ja lähettämällä se PyPI:hin tai yrityksen omaan
pakettivarastoon.

## Käytännössä

- **Ei sivuvaikutuksia tuonnissa.** Moduulitasolla määritellään vain
  vakioita, funktioita ja luokkia. Käynnistys kuuluu `main`-funktioon
  ja `if __name__ == "__main__":` -lohkoon.
- **Kerrokset ja yksisuuntaiset riippuvuudet.** Toimialan malli ei
  tuo mitään sovelluksen omaa; infrastruktuuri (tietokanta, HTTP)
  riippuu mallista eikä päinvastoin. Kiertävä tuonti korjataan
  siirtämällä yhteinen osa omaan moduuliinsa, ei tuomalla funktion
  sisällä.
- **Protokolla rajalle, kokoaminen pääohjelmaan.** Riippuvuudet
  välitetään parametreina, mikä tekee testauksesta suoraviivaista.
- **src-rakenne, `pyproject.toml` ja virtuaaliympäristö** jokaiseen
  projektiin, myös pieneen. Lukitustiedosto sovelluksille.
- **Julkinen rajapinta näkyviin:** `__all__` ja alaviivalla alkavat
  sisäiset nimet. Paketin `__init__.py` tuo julkiset nimet, jotta
  käyttäjä kirjoittaa `from varasto import Tuote`.
- **Hinta:** tuonti suorittaa moduulin, ja suuret riippuvuudet (pandas,
  PyTorch) voivat viedä sekunteja. Komentorivityökalussa raskas tuonti
  siirretään funktion sisään, jos sitä tarvitaan vain osassa
  komennoista. `python -X importtime` näyttää tuontiajat.
- **Sudenkuopat:** oma moduuli, jonka nimi peittää
  standardikirjaston moduulin (`random.py`, `json.py`), `sys.path`-
  manipulointi tuontien korjaamiseksi ja paketit järjestelmän
  Pythoniin.

## Itsearviointi

- Osaat selittää, mitä `import` tekee, miksi moduulin koodi ajetaan
  vain kerran ja mitä `if __name__ == "__main__":` erottaa.
- Osaat jakaa ohjelman kerroksiin niin, että riippuvuudet kulkevat
  yhteen suuntaan, ja kääntää riippuvuuden protokollalla.
- Osaat järjestää projektin src-rakenteeseen ja kirjoittaa sille
  `pyproject.toml`-tiedoston riippuvuuksineen ja komentoineen.
- Osaat luoda virtuaaliympäristön, asentaa projektin muokattavana ja
  lukita sovelluksen riippuvuudet.
- Osaat tunnistaa ja korjata kiertävän tuonnin.
