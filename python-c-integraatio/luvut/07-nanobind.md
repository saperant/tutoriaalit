# nanobind

nanobind on pybind11:n alkuperäisen kirjoittajan uudempi kirjasto,
joka tekee saman työn pienemmällä ja nopeammalla toteutuksella. Sen
rajapinta muistuttaa pybind11:tä niin paljon, että siirtyminen on
suurelta osin nimien vaihtoa, mutta se on rajattu tarkoituksella:
osa pybind11:n harvinaisista ominaisuuksista puuttuu, ja muutamat
oletukset ovat tiukempia. Tavoite on, että sidonnat kääntyvät
nopeammin, tuottavat pienempiä binäärejä ja kutsut ovat halvempia.

## Sama luokka nanobindilla

Luvun 5 tilastoluokan sidonta nanobindilla näyttää lähes samalta:

```{.cpp tiedosto="esimerkit/07-nanobind/tilasto_nb.cpp" osa="moduuli"}
```

| pybind11 | nanobind |
|----------|----------|
| `PYBIND11_MODULE(nimi, m)` | `NB_MODULE(nimi, m)` |
| `py::class_`, `py::init`, `py::arg` | `nb::class_`, `nb::init`, `nb::arg` |
| `def_property_readonly`, `def_property` | `def_prop_ro`, `def_prop_rw` |
| `py::register_exception` | `nb::exception` |
| `<pybind11/stl.h>` kaikille säiliöille | oma otsake tyyppiä kohden, esim. `<nanobind/stl/vector.h>` |
| `py::array_t` | `nb::ndarray` (luku 8) |
| holder-tyypit (`shared_ptr` luokan parametrina) | `<nanobind/stl/shared_ptr.h>`, ei holder-parametria |
| `pybind11-stubgen` (erillinen) | `nanobind.stubgen` mukana |

Muunnosotsakkeet ovat erillisiä, jotta käännösyksikkö sisältää vain
tarvittavat mallit. Unohtunut otsake on yleinen virhe:
`std::string`-paluuarvo ilman otsaketta `<nanobind/stl/string.h>`
kääntyy, mutta kutsu antaa ajon aikana `TypeError`in, koska tyypille
ei löydy muunninta.

## Tärkeimmät erot

- **Kevyemmät oliot.** nanobind tallentaa C++-olion suoraan
  Python-olion sisään eikä erilliseen holderiin, ja sen tyyppitiedot
  ovat tiiviimpiä. Kutsu ja olion luonti ovat siksi halvempia.
- **Tiukemmat säännöt.** Moniperintää sidottujen luokkien välillä ei
  tueta, eikä joitain pybind11:n harvinaisia
  muunnosmekanismeja ole. Tämä on tarkoituksellista: ominaisuudet
  hidastaisivat yleistä tapausta.
- **Vuotojen raportointi.** Kun tulkki sulkeutuu, nanobind tulostaa
  varoituksen olioista, tyypeistä ja funktioista, jotka jäivät
  vapauttamatta. Varoitus kertoo viittausvuodosta, joka pybind11:llä
  jäisi huomaamatta.
- **Oma ydinkirjasto.** pybind11 on pelkkiä otsakkeita. nanobindin
  yhteinen osa, `libnanobind`, käännetään kerran ja linkitetään
  jokaiseen moduuliin. Esimerkkien Makefile kääntää sen tiedostosta
  `nb_combined.cpp` (luku 3:n säännöt). Oikeissa projekteissa sen
  tekee CMake-funktio `nanobind_add_module`.
- **Vakaa ABI ja vapaasäikeinen tulkki** ovat tuettuja
  rakennusvalitsimina (`STABLE_ABI`, `FREE_THREADED`), ks. luvut 9
  ja 12.

## Vertailu

Esimerkki käyttää molempia moduuleita samassa ohjelmassa ja vertaa
yksittäisen metodikutsun hintaa. Tyyppi `Lisattava` on rakenteellinen
protokolla, joten sama funktio ajoittaa kumman tahansa luokan:

```{.python tiedosto="esimerkit/07-nanobind/main.py" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/07-nanobind/main.odotettu"}
```

Testattu raja on väljä. Esimerkin koneella nanobind-kutsu oli noin
kolme kertaa nopeampi, koska pybind11 käy jokaisessa kutsussa läpi
yleisemmän ylikuormitusten ja muunnosten koneiston. Ero näkyy vain,
kun kutsuja on paljon ja jokainen tekee vähän työtä, kuten tässä.
Kun yksi kutsu käsittelee kokonaisen taulukon, sidontakirjaston osuus
katoaa (luku 11).

Molemmat moduulit toimivat samassa tulkissa, mutta ne eivät tunne
toistensa tyyppejä: `mittari.Tilasto`a ei voi antaa nanobind-funktiolle.
Siirtymä voidaan siis tehdä moduuli kerrallaan, kunhan moduulien
välillä kulkee vain Pythonin omia tyyppejä tai NumPy-taulukoita.

Binäärikoossa ero riippuu sidontojen määrästä. Näin pienissä
moduuleissa kumpikin oli riisuttuna muutama sata kilotavua, koska
kiinteä osa hallitsee. Suurissa, satoja luokkia sisältävissä
sidonnoissa nanobind-moduulit ovat projektin mittausten mukaan
moninkertaisesti pienempiä ja kääntyvät nopeammin.

## Kumpi valitaan

- **Uusi projekti:** nanobind, jos sen ominaisuudet riittävät. Se on
  nopeampi kaikilla mittareilla, ja sen tiukemmat oletukset estävät
  virheitä.
- **Olemassa oleva pybind11-projekti:** pybind11, ellei kutsujen hinta
  tai käännösaika ole todettu ongelmaksi. Siirto on mekaaninen mutta
  koskee jokaista sidontaa.
- **Moniperintä, vanha C++-standardi tai erikoiset muunnokset:**
  pybind11. nanobind vaatii C++17:n.

## Käytännössä

- **Sama rakenne, eri nimet.** Taidot siirtyvät suoraan, ja luvun 6
  periaatteet (kopio vai viite, elinajat) pätevät samoina.
  nanobindin politiikat ovat `nb::rv_policy` ja `nb::keep_alive`.
- **Ota vuotovaroitukset vakavasti.** Ne ovat yleensä
  viittaussyklejä tai globaaleja Python-olioita C++-puolella.
- **Muista muunnosotsakkeet** jokaiselle STL-tyypille, jota rajalla
  käytetään.
- **Mittaa ennen siirtoa.** Kun moduuli tekee paljon työtä kutsua
  kohden, sidontakirjaston vaihto ei näy kokonaisajassa.

## Itsearviointi

- Osaat kirjoittaa saman sidonnan pybind11:llä ja nanobindilla ja
  tunnet nimien vastaavuudet.
- Osaat kertoa nanobindin tärkeimmät erot: kevyemmät oliot, rajatut
  ominaisuudet, vuotojen raportointi ja ydinkirjasto.
- Osaat valita sidontakirjaston projektille perustellusti.
