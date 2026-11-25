# NumPy-taulukot ilman kopiota

Numeerinen data kulkee Pythonissa NumPy-taulukkoina. Taulukko on
kuvaus muistialueesta: osoite, tietotyyppi, muoto ja *askeleet*
(*strides*), eli kuinka monta tavua siirrytään kunkin ulottuvuuden
seuraavaan alkioon. C++-funktio, joka saa tämän kuvauksen, voi lukea
ja kirjoittaa samaa muistia kuin Python ilman yhtään kopiota. Tämä on
tärkein yksittäinen syy siihen, että NumPy-pohjaiset laajennukset ovat
nopeita.

## Askeleet

Kaksiulotteinen `uint8`-taulukko, jonka muoto on (3, 4), on muistissa
12 peräkkäisenä tavuna. Sen askeleet ovat (4, 1): rivistä seuraavaan
siirrytään 4 tavua, sarakkeesta seuraavaan 1 tavu. Viipale
`k[:, ::2]` ei kopioi mitään. Se on uusi kuvaus samasta muistista,
jonka muoto on (3, 2) ja askeleet (4, 2). Transpoosi vaihtaa vain
askelten järjestyksen.

```{.dot otsikko="Kolme kuvausta samaan 12 tavuun. Jokaisessa solussa on sen alkion indeksi, joka kyseisessä tavussa sijaitsee; tyhjä solu ei kuulu kuvaukseen. Alkion (i, j) siirtymä on aina i · askel~0~ + j · askel~1~."}
digraph {
  rankdir=TB; nodesep=0.2; ranksep=0.2;
  node [shape=plain, style=""];
  m [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="4"><tr><td border="0" align="left" colspan="12"><i>muisti: 12 tavua, siirtymät 0–11</i></td></tr><tr><td width="34" height="22" fixedsize="true" bgcolor="#EEF1F6">0</td><td width="34" height="22" fixedsize="true" bgcolor="#EEF1F6">1</td><td width="34" height="22" fixedsize="true" bgcolor="#EEF1F6">2</td><td width="34" height="22" fixedsize="true" bgcolor="#EEF1F6">3</td><td width="34" height="22" fixedsize="true" bgcolor="#EEF1F6">4</td><td width="34" height="22" fixedsize="true" bgcolor="#EEF1F6">5</td><td width="34" height="22" fixedsize="true" bgcolor="#EEF1F6">6</td><td width="34" height="22" fixedsize="true" bgcolor="#EEF1F6">7</td><td width="34" height="22" fixedsize="true" bgcolor="#EEF1F6">8</td><td width="34" height="22" fixedsize="true" bgcolor="#EEF1F6">9</td><td width="34" height="22" fixedsize="true" bgcolor="#EEF1F6">10</td><td width="34" height="22" fixedsize="true" bgcolor="#EEF1F6">11</td></tr></table>>];
  a [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="4"><tr><td border="0" align="left" colspan="12"><i>k: muoto (3, 4), askeleet (4, 1); solussa indeksi (rivi, sarake)</i></td></tr><tr><td width="34" height="22" fixedsize="true" bgcolor="#F3E2C7">0,0</td><td width="34" height="22" fixedsize="true" bgcolor="#F3E2C7">0,1</td><td width="34" height="22" fixedsize="true" bgcolor="#F3E2C7">0,2</td><td width="34" height="22" fixedsize="true" bgcolor="#F3E2C7">0,3</td><td width="34" height="22" fixedsize="true" bgcolor="#FFFFFF">1,0</td><td width="34" height="22" fixedsize="true" bgcolor="#FFFFFF">1,1</td><td width="34" height="22" fixedsize="true" bgcolor="#FFFFFF">1,2</td><td width="34" height="22" fixedsize="true" bgcolor="#FFFFFF">1,3</td><td width="34" height="22" fixedsize="true" bgcolor="#F3E2C7">2,0</td><td width="34" height="22" fixedsize="true" bgcolor="#F3E2C7">2,1</td><td width="34" height="22" fixedsize="true" bgcolor="#F3E2C7">2,2</td><td width="34" height="22" fixedsize="true" bgcolor="#F3E2C7">2,3</td></tr></table>>];
  v [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="4"><tr><td border="0" align="left" colspan="12"><i>k[:, ::2]: muoto (3, 2), askeleet (4, 2)</i></td></tr><tr><td width="34" height="22" fixedsize="true" bgcolor="#F3E2C7">0,0</td><td width="34" height="22" fixedsize="true" bgcolor="#FFFFFF"> </td><td width="34" height="22" fixedsize="true" bgcolor="#F3E2C7">0,1</td><td width="34" height="22" fixedsize="true" bgcolor="#FFFFFF"> </td><td width="34" height="22" fixedsize="true" bgcolor="#F3E2C7">1,0</td><td width="34" height="22" fixedsize="true" bgcolor="#FFFFFF"> </td><td width="34" height="22" fixedsize="true" bgcolor="#F3E2C7">1,1</td><td width="34" height="22" fixedsize="true" bgcolor="#FFFFFF"> </td><td width="34" height="22" fixedsize="true" bgcolor="#F3E2C7">2,0</td><td width="34" height="22" fixedsize="true" bgcolor="#FFFFFF"> </td><td width="34" height="22" fixedsize="true" bgcolor="#F3E2C7">2,1</td><td width="34" height="22" fixedsize="true" bgcolor="#FFFFFF"> </td></tr></table>>];
  t [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="4"><tr><td border="0" align="left" colspan="12"><i>k.T: muoto (4, 3), askeleet (1, 4)</i></td></tr><tr><td width="34" height="22" fixedsize="true" bgcolor="#F3E2C7">0,0</td><td width="34" height="22" fixedsize="true" bgcolor="#FFFFFF">1,0</td><td width="34" height="22" fixedsize="true" bgcolor="#F3E2C7">2,0</td><td width="34" height="22" fixedsize="true" bgcolor="#FFFFFF">3,0</td><td width="34" height="22" fixedsize="true" bgcolor="#F3E2C7">0,1</td><td width="34" height="22" fixedsize="true" bgcolor="#FFFFFF">1,1</td><td width="34" height="22" fixedsize="true" bgcolor="#F3E2C7">2,1</td><td width="34" height="22" fixedsize="true" bgcolor="#FFFFFF">3,1</td><td width="34" height="22" fixedsize="true" bgcolor="#F3E2C7">0,2</td><td width="34" height="22" fixedsize="true" bgcolor="#FFFFFF">1,2</td><td width="34" height="22" fixedsize="true" bgcolor="#F3E2C7">2,2</td><td width="34" height="22" fixedsize="true" bgcolor="#FFFFFF">3,2</td></tr></table>>];
  m -> a -> v -> t [style=invis];
}
```

Taulukko on *C-yhtenäinen* (*C-contiguous*), jos sen alkiot ovat
muistissa peräkkäin rivi kerrallaan, ja *Fortran-yhtenäinen*, jos
sarake kerrallaan. Viipaleet ja transpoosit eivät yleensä ole
yhtenäisiä. C++-koodin, joka olettaa yhtenäisen muistin ja laskee
indeksit itse (`p[y * w + x]`), on joko tarkistettava se tai
vaadittava kopio. Koodi, joka käyttää askeleita, toimii kaikille
taulukoille.

Tieto on Pythonin *puskuriprotokollassa* (PEP 3118), jota NumPy,
`bytes`, `bytearray`, `memoryview` ja `array.array` toteuttavat.
pybind11:n `py::buffer` ja `py::array` sekä nanobindin `nb::ndarray`
lukevat sen.

## Paikallaan muokkaava funktio

`py::array_t<T>` on NumPy-taulukko, jonka alkiotyyppi on `T`.
`mutable_unchecked<2>()` antaa kaksiulotteisen näkymän, jonka
indeksointi `k(y, x)` laskee osoitteen askelista ilman rajojen
tarkistusta:

```{.cpp tiedosto="esimerkit/08-numpy/kuva.cpp" osa="kynnys"}
```

Sidonnassa argumentti merkitään `noconvert`illa:

```{.cpp tiedosto="esimerkit/08-numpy/kuva.cpp" osa="sidonta"}
```

Ilman `noconvert`ia pybind11 muuntaisi väärän tyyppisen taulukon
`uint8`:ksi, ja muunnos on kopio. Funktio kynnystäisi kopion, ja
kutsujan taulukko pysyisi ennallaan ilman virheilmoitusta. Funktiolle,
joka muuttaa argumenttiaan, muunnos on aina virhe:

```{.python tiedosto="esimerkit/08-numpy/main.py" osa="kynnys"}
```

```{.tuloste tiedosto="esimerkit/08-numpy/main.odotettu"}
```

Viipaleen kynnystys muutti vain parillisia sarakkeita alkuperäisessä
taulukossa. Sama funktio käsitteli viipaleen ilman kopiota, koska
näkymä noudattaa askeleita.

`unchecked` ei tarkista indeksejä eikä ulottuvuuksien määrää
silmukassa. `unchecked<2>()` tarkistaa kerran, että taulukko on
kaksiulotteinen, ja nostaa muuten poikkeuksen. Indeksit ovat
kutsujan vastuulla, kuten `std::vector`in `operator[]`issa.

## Uusi taulukko tuloksena

Kun funktio palauttaa uuden taulukon, syötteen voi muuntaa
vapaasti. `py::array::forcecast` hyväksyy minkä tahansa
numeerisen syötteen, myös Python-listan, ja `c_style` takaa
yhtenäisen muistin. Kumpikin voi kopioida syötteen, mutta kopio ei
haittaa, koska syötettä vain luetaan:

```{.cpp tiedosto="esimerkit/08-numpy/kuva.cpp" osa="sumennus"}
```

```{.python tiedosto="esimerkit/08-numpy/main.py" osa="sumennus"}
```

`py::array_t<float> tulos({h, w})` varaa uuden NumPy-taulukon, jonka
Python omistaa. Funktio täyttää sen ja palauttaa sen ilman kopiota.

## C++:n muisti NumPy-taulukkona

Joskus muisti on C++-olion omaa: kameran kehyspuskuri, simulaation
tila tai kirjaston sisäinen taulukko. Sen voi antaa Pythonille
NumPy-taulukkona, joka osoittaa C++:n muistiin:

```{.cpp tiedosto="esimerkit/08-numpy/kuva.cpp" osa="puskuri"}
```

Neljäs muodostimen argumentti on *perusolio* (`base`). NumPy-taulukko
pitää siitä viitteen, joten C++-olio elää niin kauan kuin yksikin
taulukko osoittaa sen muistiin. Sidonta välittää perusolioksi
Python-olion itse (`itse`), joka sisältää `Kehys`-olion:

```{.python tiedosto="esimerkit/08-numpy/main.py" osa="puskuri"}
```

```{.dot otsikko="Kuka pitää muistin elossa. Taulukko ei omista dataansa, mutta sen perusolio on `Kehys`-olion sisältävä Python-olio, joten muisti säilyy, kunnes viimeinen taulukko on poistettu."}
digraph {
  rankdir=LR; nodesep=0.4; ranksep=0.6;
  nimi [shape=plain, style="", label=<<i>taulukko (Python-nimi)</i>>];
  arr [label="numpy.ndarray\nowndata = False"];
  olio [label="Python-olio,\njossa Kehys"];
  muisti [label="Kehyksen puskuri\n(C++:n muisti)", fillcolor="#F3E2C7"];
  nimi -> arr;
  arr -> olio [label="base: viite"];
  arr -> muisti [label="data: osoitin", style=dashed];
  olio -> muisti [label="omistaa"];
}
```

Python kirjoitti C++:n muistiin, ja C++ näki muutoksen. `owndata` on
`False`, koska taulukko ei omista muistiaan. `del kehys` poisti
viimeisen nimen, mutta kehys pysyi elossa taulukon kautta. Ilman
perusoliota taulukko osoittaisi vapautettuun muistiin.

Sama pätee, kun muisti ei ole Python-olion sisällä: C++:n
`std::vector` voidaan siirtää kapseliin (`py::capsule`), jonka
purkajafunktio vapauttaa vektorin, ja kapseli annetaan perusolioksi.

## Tietotyyppi

NumPy-taulukon tietotyyppi (`dtype`) on osa sen kuvausta. Tavallisin
virhe on `float64`-taulukko `float32`-funktiolle: NumPyn oletustyyppi
on `float64`, ja `np.array([1, 2, 3])` on `int64`. Funktio, joka lukee
syötteensä, voi sallia muunnoksen. Funktio, joka kirjoittaa
argumenttiinsa, ei voi. Funktiossa, jonka on oltava nopea, muunnoksen
kopio kannattaa yleensä estää myös luettaessa, jotta kutsuja huomaa
väärän tyypin eikä maksa kopiota tietämättään.

| NumPy | C++ |
|-------|-----|
| `np.uint8`, `np.int32`, `np.int64` | `std::uint8_t`, `std::int32_t`, `std::int64_t` |
| `np.float32`, `np.float64` | `float`, `double` |
| `np.complex128` | `std::complex<double>` |
| `np.bool_` | `bool` |

## nanobindin ndarray

nanobindin `nb::ndarray` kirjoittaa rajoitteet tyyppiin:
alkiotyyppi, ulottuvuuksien määrä, yhtenäisyys ja laite. Taulukko,
joka ei täytä niitä, muunnetaan tai hylätään jo kutsussa:

```{.cpp tiedosto="esimerkit/08-numpy/kuva_nb.cpp" osa="ndarray"}
```

```{.python tiedosto="esimerkit/08-numpy/main.py" osa="ndarray"}
```

`const float` kertoo, että funktio vain lukee. Ilman `noconvert`ia
epäyhtenäinen viipale kopioitiin yhtenäiseksi, ja tulos oli silti
oikein. `noconvert`in kanssa sama viipale hylättiin. Kumpi on oikein,
riippuu funktiosta, mutta valinta tehdään tietoisesti.

`nb::ndarray` ei ole sidottu NumPyyn. Sama funktio hyväksyy PyTorchin,
JAX:n, TensorFlow'n ja CuPyn taulukot DLPack-protokollan kautta, ja
`nb::device::cuda` -rajoitteella näytönohjaimen muistissa olevat
taulukot. Paluuarvona `nb::ndarray<nb::numpy, ...>` tuottaa
NumPy-taulukon, ja perusolion tilalla on `owner`-argumentti.

## Käytännössä

- **Paikallaan muokkaava funktio: tarkka tyyppi ja `noconvert`.**
  Muuten muunnos tekee kopion, ja muutokset katoavat hiljaa.
- **Lukeva funktio: muunnos sallittu**, mutta mieti, haluatko kutsujan
  maksavan kopion tietämättään. Suurille taulukoille hylkäys on usein
  parempi.
- **Noudata askeleita** `unchecked`-näkymillä tai tarkista
  yhtenäisyys. Älä laske indeksejä itse olettaen yhtenäistä muistia.
- **C++:n muisti näkymänä vain perusolion kanssa.** Taulukko, joka
  osoittaa muistiin ilman omistajaa, on roikkuva osoitin.
- **Uusi taulukko varataan Pythonin taulukoksi** (`py::array_t<T>({h,
  w})`) ja täytetään. Näin vältetään kopio `std::vector`ista.
- **Sudenkuoppa:** `np.array([...])` on `int64` tai `float64`.
  Testaa sidonnat oletustyypeillä, koska käyttäjät kutsuvat niillä.

## Itsearviointi

- Osaat selittää NumPy-taulukon muodon, askeleet ja yhtenäisyyden ja
  sen, miksi viipale ei kopioi.
- Osaat kirjoittaa C++-funktion, joka muokkaa NumPy-taulukkoa
  paikallaan, ja estää hiljaisen kopion `noconvert`illa.
- Osaat antaa C++-olion muistin Pythonille NumPy-taulukkona niin, että
  perusolio pitää omistajan elossa.
- Osaat kirjoittaa taulukon rajoitteet `nb::ndarray`n tyyppiin ja
  valita muunnoksen ja hylkäyksen välillä.
