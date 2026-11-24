# Muunnokset ja elinajat

Kun Python-olio kulkee C++-funktiolle, pybind11 tekee jommankumman
kahdesta asiasta. Joko se *muuntaa* olion C++-arvoksi, jolloin C++ saa
kopion, tai se *antaa viitteen* C++-olioon, joka on jo Python-olion
sisällä. Kumpi tapahtuu, riippuu tyypistä, ja ero näkyy sekä
nopeudessa että käytöksessä. Kääntäen, kun C++ palauttaa osoittimen
tai viittauksen, on päätettävä, kuka omistaa olion ja kuinka kauan se
elää.

## Kopio vai viite

Kaksi lähes samanlaista funktiota muuttavat argumenttinsa paikallaan:

```{.cpp tiedosto="esimerkit/06-muunnokset/muunnos.cpp" osa="kopio"}
```

```{.python tiedosto="esimerkit/06-muunnokset/main.py" osa="kopio"}
```

Ensimmäiset kaksi riviä tulosteessa näyttävät eron:

```{.tuloste tiedosto="esimerkit/06-muunnokset/main.odotettu"}
```

`tuplaa` muutti listaa, mutta Python-lista pysyi ennallaan. Otsake
`<pybind11/stl.h>` muuntaa listan uudeksi `std::vector<double>`iksi
ennen kutsua, ja funktio muutti tätä väliaikaista vektoria.
Viittausparametri ei auta, koska viitattava olio on kopio. Sama koskee
paluuarvoja: palautettu `std::vector` muunnetaan uudeksi listaksi.

Automaattinen muunnos on oikea valinta pienille arvoille ja
argumenteille, joita funktio vain lukee. Sen hinta on lineaarinen
datan koon suhteen, ja jokainen alkio muunnetaan erikseen
Python-oliosta. Miljoonan alkion lista muunnetaan miljoonalla
tyyppitarkistuksella joka kutsussa (luku 11).

`Laskurit` on *läpinäkymätön* tyyppi. `PYBIND11_MAKE_OPAQUE` kieltää
automaattisen muunnoksen, ja `py::bind_vector` luo Python-luokan, joka
sisältää C++-vektorin ja tarjoaa listan rajapinnan (`len`,
indeksointi, `append`, iterointi). Python ja C++ käsittelevät samaa
vektoria, joten muutokset näkyvät molemmille, eikä mitään kopioida.

```{.cpp tiedosto="esimerkit/06-muunnokset/muunnos.cpp" osa="sidonta"}
```

`PYBIND11_MAKE_OPAQUE` on kirjoitettava ennen kuin tyyppiä käytetään
missään, ja kaikkien saman ohjelman moduulien on oltava siitä samaa
mieltä. Muuten sama C++-tyyppi muunnetaan yhdessä moduulissa ja
välitetään viitteenä toisessa.

Suurelle numeeriselle datalle läpinäkymätön vektori ei ole paras
ratkaisu. NumPy-taulukko on Pythonin yhteinen kieli numeeriselle
datalle, ja sen voi välittää C++:lle ilman kopiota (luku 8).

## Paluuarvojen omistajuus

Kun C++-funktio palauttaa arvon, pybind11 siirtää sen uuteen
Python-olioon, ja Python omistaa sen. Kun funktio palauttaa
osoittimen tai viittauksen, pybind11 ei tiedä, kuka omistaa olion.
Sidonta kertoo sen *paluuarvopolitiikalla*:

| Politiikka | Merkitys |
|------------|----------|
| `take_ownership` | Python omistaa ja tuhoaa olion (osoittimien oletus) |
| `copy`, `move` | Python saa oman kopion (arvon ja viittauksen oletus) |
| `reference` | Python ei omista: C++:n on pidettävä olio elossa |
| `reference_internal` | kuten `reference`, ja palautettu olio pitää `self`in elossa |
| `automatic` | valitaan tyypin mukaan (oletus) |

`reference` on vaarallinen: jos C++ tuhoaa olion, Python-olio osoittaa
vapautettuun muistiin. `reference_internal` sopii metodeille, jotka
palauttavat viittauksen olion omaan sisältöön, kuten säiliön alkioon.
Python-olio pitää säiliön elossa niin kauan kuin viittaus on käytössä.

Väärä politiikka on vaarallinen kumpaankin suuntaan. Jos metodi
palauttaa osoittimen olion jäseneen ja sidonta jättää sen
oletukseksi `take_ownership`, Python yrittää tuhota jäsenen, jota se
ei omista.

## Elinaikojen sitominen

`Ketju` säilyttää osoittimia `Vahvistus`-olioihin mutta ei omista
niitä. C++:ssa kutsujan vastuulla on pitää vaiheet elossa ketjua
kauemmin:

```{.cpp tiedosto="esimerkit/06-muunnokset/muunnos.cpp" osa="elinaika"}
```

Pythonissa käyttäjä kirjoittaa luontevasti
`ketju.lisaa(Vahvistus(2.0))`. Väliaikaisen olion ainoa viite on
argumentti, joten Python tuhoaisi sen heti kutsun jälkeen, ja ketju
jäisi osoittamaan vapautettuun muistiin. `py::keep_alive<1, 2>()`
kertoo, että argumentti 1 (`self`, ketju) pitää argumentin 2 (vaihe)
elossa. pybind11 tallentaa viitteen ketjun Python-olioon, ja vaihe
vapautetaan vasta ketjun jälkeen.

```{.python tiedosto="esimerkit/06-muunnokset/main.py" osa="elinaika"}
```

Tulosteen kolme viimeistä riviä näyttävät, että väliaikaiset vaiheet
pysyivät elossa (`elossa: 2`), vaiheen viittaus piti ketjun ja sen
kautta vaiheet elossa vielä `del ketju`:n jälkeen, ja kaikki
vapautettiin, kun viimeinen viite katosi. `elossa`-laskuri on
luokan staattinen jäsen, joka laskee muodostimen ja purkajan kutsut.
Se on hyvä tapa testata elinaikoja.

Ilman `keep_alive`a ohjelma ei välttämättä kaadu heti. Vapautettu
muisti voi sisältää vanhan arvon pitkään, ja virhe näkyy vasta, kun
muisti käytetään uudelleen. Tällaiset virheet löytyvät parhaiten
AddressSanitizerilla (taito *C-kieli*), jolloin laajennus käännetään
lipulla `-fsanitize=address` ja tulkki ajetaan
`LD_PRELOAD=$(gcc -print-file-name=libasan.so)`-muuttujalla.

## Älykkäät osoittimet

Jos C++-oliot ovat jaetussa omistuksessa, luokka sidotaan
`std::shared_ptr`illä: `py::class_<T, std::shared_ptr<T>>`. Silloin
Python-olio ja C++-koodi jakavat saman viitelaskurin, ja olio elää,
kunnes molemmat ovat luopuneet siitä. `std::unique_ptr`-paluuarvo
siirtää omistuksen Pythonille. pybind11 3:n `py::smart_holder`
(`py::classh`) tukee molempia ja myös omistuksen siirtoa Pythonista
takaisin C++:lle `std::unique_ptr`-argumenttina. Raakaosoittimet ja
viittaukset tarvitsevat aina politiikan ja usein `keep_alive`n.

## Käytännössä

- **Automaattinen muunnos kopioi.** `std::vector`, `std::map` ja
  `std::string` -parametrit ja paluuarvot ovat kopioita. Funktion,
  joka muuttaa argumenttiaan, on otettava läpinäkymätön tyyppi tai
  NumPy-taulukko, tai sen on palautettava uusi arvo.
- **Paluuarvo arvona aina kun voi.** Arvo siirretään Pythonille
  omistukseen, eikä elinaikaa tarvitse miettiä.
- **Viittaus jäseneen: `reference_internal`.** Viittaus tai osoitin
  muuhun: mieti, kuka omistaa, ja kirjoita politiikka näkyviin.
- **Säilötty osoitin: `keep_alive`.** Jokainen metodi, joka tallentaa
  argumenttinsa osoittimen, tarvitsee sen.
- **Testaa elinajat laskurilla** ja aja testit AddressSanitizerin
  kanssa. Elinaikavirhe ei näy tavallisessa testiajossa.
- **Sudenkuoppa:** `PYBIND11_MAKE_OPAQUE` eri tavalla eri
  käännösyksiköissä. Laita se yhteiseen otsakkeeseen, jonka kaikki
  sidontatiedostot sisällyttävät.

## Itsearviointi

- Osaat kertoa, milloin pybind11 kopioi argumentin ja milloin antaa
  viitteen, ja tehdä tyypistä läpinäkymättömän.
- Osaat valita paluuarvopolitiikan osoittimelle ja viittaukselle.
- Osaat sitoa olioiden elinajat `keep_alive`lla ja
  `reference_internal`illa ja testata ne.
- Osaat valita `shared_ptr`-, `unique_ptr`- ja raakaosoitinsidonnan
  välillä omistajuuden mukaan.
