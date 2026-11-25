# Lopuksi {.runko-kaytannot .runko-lahteet}

## Nyrkkisäännöt

| Tilanne | Ratkaisu |
|---------|----------|
| Ohjelma on hidas | profiloi ensin, vektoroi NumPylla ennen C++:aa |
| Valmis C-kirjasto, muutama funktio | `ctypes`, `argtypes` ja `restype` jokaiselle |
| Laaja C-kirjasto | cffi:n API-tila tai laajennusmoduuli |
| C++-kirjasto kaikille kielille | C-rajapinta: kahva, virhekoodit, versio |
| C++-koodi vain Pythonille | nanobind uuteen, pybind11 olemassa olevaan |
| Poikkeus rajalla | C:ssä virhekoodiksi, sidonnoissa Python-poikkeukseksi |
| Funktio muuttaa argumenttiaan | läpinäkymätön tyyppi tai taulukko `noconvert`illa |
| C++ säilyttää osoittimen | `keep_alive` tai jaettu omistus |
| Viittaus olion sisään | `reference_internal` |
| Numeerinen data | NumPy-taulukko, askeleet huomioiden, ei listaa |
| C++:n muisti Pythonille | näkymä perusolion kanssa |
| Pitkä C++-kutsu | vapauta tulkkilukko, älä koske Python-olioihin |
| C++-säie kutsuu Pythonia | `gil_scoped_acquire` |
| Raaka C-API | uusi vai lainattu viite, virhetila ja `NULL` |
| Monta pientä kutsua | siirrä silmukka C++:aan, kutsu erinä |
| Jakelu | `pyproject.toml`, pyörä, manylinux, cibuildwheel |
| Monta Python-versiota | vakaa ABI (`abi3`) nanobindilla tai C-API:lla |

## Mallit

- **Mittaa, vektoroi, käännä:** natiivikoodiin vasta, kun profiloija on
  näyttänyt peräkkäisen silmukan, jota NumPy ei ratkaise.
- **Läpinäkymätön kahva:** C-rajapinta, jonka takana toteutus voi
  muuttua rikkomatta kutsujia.
- **Ohut sidonta, puhdas C++:** C++-koodi ei tiedä Pythonista, ja
  sidonnat kuvaavat vain rajan.
- **Omistaja näkyviin:** jokaisella rajan ylittävällä osoittimella on
  nimetty omistaja ja elinaika, ja Python-puolella se näkyy
  `with`-lohkona, `keep_alive`na tai perusoliona.
- **Erät, ei alkiot:** kutsu maksaa kiinteän hinnan, joten yksi kutsu
  tekee paljon työtä.
- **Testaa rajaa:** viitemäärät, elinaikalaskurit ja asennettu pyörä,
  koska rajan virheet eivät näy tavallisissa testeissä.

## Lähteet ja lisälukemista

- **Pythonin dokumentaatio** (<https://docs.python.org/3/>):
  `ctypes`-moduuli, *Extending and Embedding the Python Interpreter*
  ja *Python/C API Reference Manual*, erityisesti viitelaskentaa ja
  rajoitettua API:a käsittelevät sivut.
- **pybind11:n dokumentaatio** (<https://pybind11.readthedocs.io>):
  luokat, paluuarvopolitiikat, `keep_alive`, NumPy ja GIL.
- **nanobindin dokumentaatio** (<https://nanobind.readthedocs.io>):
  erot pybind11:een (*Porting guide*), `nb::ndarray`, vakaa ABI ja
  vapaasäikeisyys.
- **cffi** (<https://cffi.readthedocs.io>): ABI- ja API-tila.
- **NumPyn dokumentaatio** (<https://numpy.org/doc/>): *The N-dimensional
  array*, askeleet ja puskuriprotokolla.
- **Python Packaging User Guide** (<https://packaging.python.org>):
  pyörät, alustatunnisteet ja binäärilaajennukset.
- **scikit-build-core** (<https://scikit-build-core.readthedocs.io>),
  **cibuildwheel** (<https://cibuildwheel.pypa.io>) ja
  **auditwheel** (<https://github.com/pypa/auditwheel>).
- **Python free-threading guide** (<https://py-free-threading.github.io>):
  laajennusmoduulien siirtäminen vapaasäikeiseen tulkkiin.
- **PEP 3118** (puskuriprotokolla), **PEP 489** (monivaiheinen alustus),
  **PEP 600** (manylinux), **PEP 703** (vapaasäikeinen CPython) ja
  **PEP 384** (vakaa ABI): <https://peps.python.org>.

## Jatkotaidot

Taito *C++:n suorituskyky* jatkaa siitä, mihin tämä tutoriaali
jättää: kun silmukka on siirretty C++:aan, sen nopeus riippuu
välimuisteista, vektorikäskyistä ja muistin asettelusta. Taito
*GPU-laskenta* siirtää saman laskennan näytönohjaimelle, ja
`nb::ndarray` välittää taulukot sinne ja takaisin. Taito
*Käännösjärjestelmät, testaus ja CI* käsittelee CMakea ja CI-putkia,
joissa pyörät rakennetaan, ja taito *Objektitiedostot, linkitys ja
ABI* sitä, mitä jaetun kirjaston latauksessa tapahtuu.
