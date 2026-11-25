# Laajennusmoduuli pybind11:llä

*Laajennusmoduuli* on jaettu kirjasto, jonka Python tuo kuten
tavallisen moduulin: `import mittari` etsii hakupolulta tiedoston
`mittari.cpython-312-x86_64-linux-gnu.so` ja kutsuu sen
alustusfunktiota `PyInit_mittari`. Alustusfunktio luo moduuliolion,
funktiot ja luokat Pythonin C-API:lla (luku 11).

pybind11 on otsakekirjasto, joka kirjoittaa tämän koodin C++-mallien
avulla. Sidonta on yksi rivi funktiota kohden: pybind11 päättelee
argumenttien ja paluuarvon tyypit C++-funktion tyypistä ja tuottaa
tyyppimuunnokset ja virheiden käsittelyn. Toisin kuin `ctypes`, se näkee
C++-tyypit, joten väärä tyyppi on käännösvirhe tai Python-poikkeus, ei
kaatunut tulkki.

## C++-luokka

Esimerkki laskee juoksevaa keskiarvoa ja keskihajontaa Welfordin
algoritmilla. Luokka on tavallista C++:aa eikä tiedä Pythonista
mitään. Virheellinen arvo ja tyhjä otos ovat poikkeuksia:

```{.cpp tiedosto="esimerkit/05-pybind11/mittari.cpp" osa="luokka"}
```

## Sidonnat

`PYBIND11_MODULE(nimi, m)` määrittelee moduulin alustusfunktion. Nimen
on oltava sama kuin tiedostonimen alku, muuten `import` ei löydä
alustusfunktiota:

```{.cpp tiedosto="esimerkit/05-pybind11/mittari.cpp" osa="moduuli"}
```

- **`py::class_<T>`** luo Python-luokan, jonka oliot sisältävät C++-olion.
  `py::init<>()` sitoo oletusmuodostimen. Muodostimet, joilla on
  argumentteja, sidotaan muodossa `py::init<int, double>()`.
- **`.def`** sitoo metodin. `py::arg("x")` antaa argumentille nimen,
  jolloin sitä voi kutsua avainsana-argumenttina (`t.lisaa(x=1.0)`), ja
  nimi näkyy ohjeessa ja virheilmoituksissa. Merkkijono on
  ohjeteksti (`help(t.lisaa)`).
- **`.def_property_readonly`** tekee getteristä Python-ominaisuuden.
  Python-käyttäjä kirjoittaa `t.keskiarvo` eikä `t.keskiarvo()`.
- **Erikoismetodit** `__len__` ja `__repr__` sidotaan kuten muut
  metodit. Lambda sopii, kun C++-luokassa ei ole valmista vastinetta.
- **`m.def`** sitoo vapaan funktion, myös lambdan.

Tyyppimuunnokset tulevat otsakkeista. `<pybind11/pybind11.h>`
osaa perustyypit (`int`, `double`, `bool`, `std::string`), ja
`<pybind11/stl.h>` lisää säiliöt: `std::vector` ↔ `list`,
`std::map` ↔ `dict`, `std::optional` ↔ `None` tai arvo. Muunnoksilla
on hintansa, johon palataan luvussa 6.

## Poikkeukset

pybind11 muuntaa C++-poikkeukset Python-poikkeuksiksi automaattisesti
vakiotaulukon mukaan:

| C++ | Python |
|-----|--------|
| `std::invalid_argument`, `std::domain_error` | `ValueError` |
| `std::out_of_range` | `IndexError` |
| `std::length_error` | `ValueError` |
| `std::bad_alloc` | `MemoryError` |
| `std::overflow_error` | `OverflowError` |
| `std::runtime_error`, muut `std::exception` | `RuntimeError` |
| `py::value_error`, `py::type_error` jne. | vastaava Python-poikkeus |

Kirjaston oma poikkeus rekisteröidään `py::register_exception`illa.
Kolmas argumentti antaa Python-puolen yläluokan: `TyhjaOtos` on
`ValueError`in aliluokka, joten käyttäjä voi napata sen kummalla
nimellä tahansa. Tämä on hyvä tapa, koska kutsujat tuntevat
vakiopoikkeukset, ja tarkempi luokka on silti saatavilla.

## Käyttö Pythonista

Moduuli tuodaan ja sitä käytetään kuten mitä tahansa Python-moduulia:

```{.python tiedosto="esimerkit/05-pybind11/main.py" osa="kaytto"}
```

```{.python tiedosto="esimerkit/05-pybind11/main.py" osa="poikkeukset"}
```

```{.tuloste tiedosto="esimerkit/05-pybind11/main.odotettu"}
```

Väärän tyyppinen argumentti antaa `TypeError`in, jonka viesti
luettelee hyväksytyt tyypit. pybind11 kokeilee ylikuormitettuja
sidontoja järjestyksessä ja nostaa virheen, jos mikään ei sovi.
Ensimmäinen osuma voittaa, joten tarkempi ylikuormitus (`int`)
kirjoitetaan ennen yleisempää (`double`).

## Tyyppivihjeet

Laajennusmoduulista ei ole Python-lähdettä, joten `mypy` ja editorit
eivät tiedä sen tyyppejä. Ne luetaan *tynkätiedostosta* (`.pyi`), joka
on moduulin vieressä tai hakupolulla:

```{.python tiedosto="esimerkit/05-pybind11/mittari.pyi" osa="tyypit"}
```

Tynkätiedoston voi kirjoittaa käsin tai tuottaa työkalulla
`pybind11-stubgen`, joka tuo moduulin ja lukee sidontojen tiedot.
nanobind tuottaa tynkätiedostot itse (`nanobind.stubgen`). Tuotettu
tiedosto kannattaa tarkistaa, koska C++-tyypin vastine ei aina ole
paras Python-tyyppi: `std::vector<double>`-argumentti hyväksyy minkä
tahansa jonon, mutta tuotettu tynkä voi sanoa `list[float]`.

Sidontojen ohjetekstit (`def`in merkkijonoargumentti) ja
tynkätiedosto ovat myös laajennusmoduulin rajapintadokumentaation
lähde: Sphinxin `autodoc` tuo käännetyn moduulin ja lukee ne kuten
Python-moduulin docstringit (taito *Tekninen dokumentaatio*).

## Kääntäminen

Laajennus on jaettu kirjasto, jonka nimen pääte kertoo tulkin version
ja alustan. Esimerkkien Makefile kääntää sen suoraan kääntäjällä:

```text
g++-14 -O2 -std=c++20 -fPIC -fvisibility=hidden -Wall -Wextra -Werror \
    $(python3 -m pybind11 --includes) -shared mittari.cpp \
    -o mittari$(python3-config --extension-suffix)
```

Linuxissa laajennusta ei linkitetä `libpython`iin: symbolit tulevat
tulkista, joka lataa moduulin. Siksi sama moduuli toimii sekä
staattisesti että dynaamisesti linkitetyssä tulkissa. Oikeissa
projekteissa käännöksen hoitaa rakennusjärjestelmä (luku 12).

## Käytännössä

- **C++-luokka ei tiedä Pythonista.** Sidonnat ovat erillisessä
  tiedostossa tai lohkossa, ja C++-koodia voi testata ja käyttää
  ilman Pythonia.
- **`py::arg` jokaiselle argumentille.** Nimet tekevät rajapinnasta
  pythonmaisen ja virheilmoituksista luettavia.
- **Ominaisuudet gettereille**, erikoismetodit (`__len__`,
  `__repr__`, `__iter__`, `__eq__`) Python-protokollille. Hyvä sidonta
  näyttää Python-luokalta eikä C++-luokan kopiolta.
- **Omat poikkeukset vakiopoikkeusten aliluokiksi.** Käyttäjä voi
  napata `ValueError`in tietämättä kirjastosta mitään.
- **Tynkätiedosto mukaan**, jotta `mypy --strict` toimii moduulin
  käyttäjillä.
- **Sudenkuoppa:** moduulin nimi. `PYBIND11_MODULE(mittari, m)` ja
  tiedosto `mittari.cpython-*.so` kuuluvat yhteen. Ristiriita antaa
  virheen `ImportError: dynamic module does not define module export
  function`.
- **Sudenkuoppa:** käännetty moduuli toimii vain sille
  Python-versiolle ja alustalle, jolle se käännettiin. Python 3.12:lla
  käännetty moduuli ei lataudu Python 3.13:een. Vakaa ABI (luku 12)
  lieventää tätä.

## Itsearviointi

- Osaat sitoa C++-luokan, sen metodit ja ominaisuudet sekä vapaat
  funktiot pybind11:llä.
- Osaat muuntaa C++-poikkeukset Python-poikkeuksiksi ja rekisteröidä
  oman poikkeuksen vakiopoikkeuksen aliluokaksi.
- Osaat kirjoittaa laajennusmoduulille tynkätiedoston, jotta
  tyyppitarkistus toimii.
- Osaat kääntää laajennusmoduulin käsin ja selittää tiedostonimen
  päätteen.
