# Paketointi ja jakelu

Käsin käännetty laajennus toimii kehittäjän koneella. Muut tarvitsevat
paketin, jonka voi asentaa `pip install`illä ilman kääntäjää. Pythonin
binäärijakelun muoto on *pyörä* (*wheel*): zip-tiedosto, jossa on
paketin Python-tiedostot, käännetyt moduulit ja metatiedot, ja jonka
nimi kertoo, mille tulkille ja alustalle se on käännetty. Lähdekoodin
jakelu (*sdist*) on varalla niille alustoille, joille pyörää ei ole.

## Paketin rakenne

Esimerkkipaketti `nopeatarkiste` laskee CRC-32:n mille tahansa
puskurille. Rakenne noudattaa src-asettelua (taito *Python
työkaluohjelmointiin*):

```text
12-paketointi/
  pyproject.toml          projektin metatiedot ja rakennustyökalu
  setup.py                laajennusmoduulin käännös
  src/ydin.cpp            C++-lähde
  src/nopeatarkiste/
    __init__.py           julkinen rajapinta
    _ydin.pyi             käännetyn moduulin tyypit
    py.typed              merkki: paketissa on tyyppitiedot
  testit/                 pytest-testit asennettua pakettia vastaan
```

Käännetty moduuli on paketin sisällä alaviivalla alkavana nimenä
`_ydin`. Käyttäjät tuovat paketin `nopeatarkiste`, jonka
`__init__.py` päättää, mitä käännetystä osasta näytetään. Python-osaan
voi lisätä tarkistuksia, oletusarvoja ja puhtaita Python-funktioita
kääntämättä mitään uudelleen.

```{.cpp tiedosto="esimerkit/12-paketointi/src/ydin.cpp" osa="crc"}
```

`py::buffer` hyväksyy minkä tahansa puskuriprotokollaa tukevan olion:
`bytes`, `bytearray`, `memoryview` ja NumPy-taulukon. `request()`
lukitsee puskurin, joten esimerkiksi `bytearray`n kokoa ei voi muuttaa
laskun aikana, ja tulkkilukon voi vapauttaa turvallisesti.

## setuptools

`pyproject.toml` kertoo, millä työkalulla paketti rakennetaan ja mitä
sen rakentaminen vaatii:

```{.toml tiedosto="esimerkit/12-paketointi/pyproject.toml" osa="projekti"}
```

`[build-system].requires` asennetaan eristettyyn ympäristöön ennen
rakentamista, joten käyttäjän ei tarvitse asentaa pybind11:tä.
Laajennusmoduulit kuvataan setuptoolsissa yhä `setup.py`:ssä, mutta
vain ne: muut tiedot ovat `pyproject.toml`issa.

```{.python tiedosto="esimerkit/12-paketointi/setup.py" osa="setup"}
```

`Pybind11Extension` lisää pybind11:n otsakkeet, C++-standardin ja
piilotetun näkyvyyden. Esimerkkien Makefile rakentaa pyörän, asentaa
sen erilliseen hakemistoon ja ajaa testit asennettua pakettia
vastaan, ei lähdehakemistoa:

```{.makefile tiedosto="esimerkit/Makefile" osa="paketti"}
```

`--no-build-isolation` ja `--no-index` käyttävät jo asennettuja
rakennustyökaluja eivätkä hae mitään verkosta, jotta testi toimii
ilman verkkoyhteyttä. Tavallisesti pyörä rakennetaan komennolla
`python3 -m build` tai `pip wheel .`, jotka asentavat riippuvuudet
eristettyyn ympäristöön. Testit asennettua pakettia vastaan
paljastavat puuttuvat tiedostot: jos `_ydin.pyi` tai `py.typed`
puuttuisi `package-data`sta, pyörästä puuttuisi tyyppitieto, vaikka
lähdehakemistossa kaikki toimisi.

```{.tuloste tiedosto="esimerkit/12-paketointi/nayta.odotettu"}
```

Pyörän nimessä `cpXY-cpXY` kertoo tulkin version ja ABI:n, esimerkiksi
`cp312-cp312` Python 3.12:lle. Esimerkin tulosteessa versio on
yleistetty, jotta testi toimii millä tahansa versiolla. Alustan
tunniste `linux_x86_64` tarkoittaa, että pyörä toimii vain koneilla,
joiden kirjastot ovat samat kuin rakennuskoneen.

## CMake ja scikit-build-core

Suuremmissa projekteissa C++-osa rakennetaan jo valmiiksi CMakella.
Silloin `scikit-build-core` on luontevampi rakennustyökalu kuin
setuptools: se ajaa CMaken ja kokoaa tuloksen pyöräksi. Sama
rakenne nanobindilla näyttäisi tältä:

```text
# pyproject.toml
[build-system]
requires = ["scikit-build-core>=0.10", "nanobind>=2.0"]
build-backend = "scikit_build_core.build"

[project]
name = "nopeatarkiste"
version = "1.0.0"
requires-python = ">=3.12"

[tool.scikit-build]
wheel.py-api = "cp312"         # vakaa ABI Python 3.12:sta alkaen

# CMakeLists.txt
cmake_minimum_required(VERSION 3.18)
project(nopeatarkiste LANGUAGES CXX)
find_package(Python 3.12 REQUIRED COMPONENTS Interpreter
             Development.Module ${SKBUILD_SABI_COMPONENT})
find_package(nanobind CONFIG REQUIRED)
nanobind_add_module(_ydin STABLE_ABI NB_STATIC src/ydin.cpp)
install(TARGETS _ydin LIBRARY DESTINATION nopeatarkiste)
```

`nanobind_add_module` kääntää nanobindin ydinkirjaston ja asettaa
liput. pybind11:llä vastaava funktio on `pybind11_add_module`. CMake
on myös paikka, jossa laajennus linkitetään muihin C++-kirjastoihin
`target_link_libraries`illa. Tätä rakennetta ei ajeta tämän
tutoriaalin testeissä, koska scikit-build-core haetaan verkosta.

## manylinux ja auditwheel

Linux-pyörä, joka on käännetty uudella jakelulla, ei välttämättä toimi
vanhemmalla: se voi tarvita uudemman `glibc`in tai `libstdc++`:n kuin
kohdekoneella on. *manylinux*-standardi (PEP 600) ratkaisee tämän.
Pyörä käännetään vanhalla `glibc`illä, ja tunniste kertoo pienimmän
tuetun version, esimerkiksi `manylinux_2_28_x86_64` (glibc 2.28 tai
uudempi). PyPI hyväksyy vain manylinux-pyöriä, ei `linux_x86_64`-
pyöriä.

- **Rakennuskontit.** PyPA julkaisee manylinux-kontit, joissa on vanha
  `glibc` ja uusi kääntäjä. C++-standardikirjasto linkitetään niissä
  niin, että uusien C++-ominaisuuksien vaatimat osat tulevat
  pyörän mukana.
- **`auditwheel repair`** tarkistaa, mitä jaettuja kirjastoja moduuli
  käyttää. Järjestelmän peruskirjastojen ulkopuoliset kirjastot,
  kuten `libpng` tai `libzstd`, se kopioi pyörän sisään ja muuttaa
  moduulin hakupolun osoittamaan niihin. Sitten se antaa pyörälle
  oikean manylinux-tunnisteen.
- **musllinux** on sama muslia käyttäville jakeluille, kuten Alpinelle.
- **macOS ja Windows:** `delocate` ja `delvewheel` tekevät saman
  työn.

## cibuildwheel

Laajennukselle tarvitaan pyörä jokaiselle tuetulle Python-versiolle
ja alustalle: viisi Python-versiota kertaa Linux, macOS ja Windows
kertaa x86-64 ja ARM on kymmeniä pyöriä. `cibuildwheel` rakentaa ne
CI-palvelussa. Linuxissa se ajaa jokaisen version manylinux-kontissa
ja `auditwheel`in, ja se ajaa testit jokaista rakennettua pyörää
vastaan:

```text
# pyproject.toml
[tool.cibuildwheel]
build = "cp312-* cp313-* cp313t-*"
enable = ["cpython-freethreading"]       # cp313t
test-requires = ["pytest", "numpy"]
test-command = "pytest {project}/testit"
```

## Vakaa ABI

Vakaan ABI:n (luku 10) avulla yksi pyörä alustaa kohden riittää
kaikille Python-versioille tietystä versiosta alkaen. Tunniste
`cp312-abi3` tarkoittaa, että pyörä toimii Python 3.12:ssa ja
kaikissa uudemmissa 3.x-versioissa. Rakennusmatriisi kutistuu
versioiden määrällä.

- **nanobind** tukee vakaata ABI:a Python 3.12:sta alkaen
  (`STABLE_ABI`).
- **pybind11** ei tue sitä, koska se käyttää tulkin sisäisiä
  rakenteita.
- **Raaka C-API ja Cython** tukevat sitä makrolla `Py_LIMITED_API`.
- **Hinta:** osa nopeista makroista on funktiokutsuja, ja jotkin
  ominaisuudet puuttuvat. Vapaasäikeinen tulkki ei vielä tue vakaata
  ABI:a, joten sille tarvitaan omat pyörät (`cp313t`).

## Käytännössä

- **`pyproject.toml` ja src-asettelu**, käännetty moduuli paketin
  sisällä alaviivalla alkavana nimenä ja Python-tiedosto julkisena
  rajapintana.
- **Tyyppitiedot mukaan:** `.pyi` ja `py.typed` `package-data`an, ja
  testi, joka tarkistaa ne pyörästä.
- **Testaa asennettua pyörää**, ei lähdehakemistoa. Lähteestä ajetut
  testit eivät huomaa puuttuvia tiedostoja.
- **setuptools pieniin, scikit-build-core CMake-projekteihin.**
  Rakennustyökalu on toteutusyksityiskohta, jonka voi vaihtaa
  käyttäjien huomaamatta.
- **Jakeluun manylinux ja cibuildwheel**, ei omalla koneella käännettyjä
  pyöriä.
- **Vakaa ABI**, kun versioiden määrä kasvaa ja nanobind tai C-API on
  käytössä.
- **Sudenkuoppa:** sdist ilman C++-lähteitä tai ilman otsakkeita.
  Rakenna sdististä pyörä CI:ssä, jotta puuttuvat tiedostot huomataan
  ennen julkaisua.

## Itsearviointi

- Osaat paketoida laajennusmoduulin `pyproject.toml`illa ja
  setuptoolsilla niin, että tyyppitiedot tulevat mukaan.
- Osaat rakentaa pyörän ja testata asennettua pakettia.
- Osaat selittää pyörän nimen tunnisteet, manylinuxin ja
  `auditwheel`in tehtävän.
- Osaat kertoa, milloin vakaa ABI kannattaa ja mitä se maksaa.
