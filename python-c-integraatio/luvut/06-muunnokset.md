# Muunnokset ja elinajat

Kun Python-olio kulkee C++-funktiolle, pybind11 tekee jommankumman
kahdesta asiasta. Joko se *muuntaa* olion C++-arvoksi, jolloin C++ saa
kopion, tai se *antaa viitteen* C++-olioon, joka on jo Python-olion
sisällä. Kumpi tapahtuu, riippuu tyypistä, ja ero näkyy sekä
nopeudessa että käytöksessä. Kääntäen, kun C++ palauttaa osoittimen
tai viittauksen, on päätettävä, kuka omistaa olion ja kuinka kauan se
elää. Luvun lopussa suunta käännetään: C++ kutsuu Python-funktiota ja
Python-luokka toteuttaa C++-rajapinnan.

## Kopio vai viite

Kaksi lähes samanlaista funktiota muuttavat argumenttinsa paikallaan:

```{.cpp tiedosto="esimerkit/06-muunnokset/muunnos.cpp" osa="kopio"}
```

```{.python tiedosto="esimerkit/06-muunnokset/main.py" osa="kopio"}
```

Tuloste näyttää eron:

```{.tuloste tiedosto="esimerkit/06-muunnokset/main.odotettu" rivit="1-2"}
```

```{.dot otsikko="Miksi lista ei muuttunut. Automaattinen muunnos rakentaa listasta väliaikaisen vektorin, ja funktio muuttaa sitä. Läpinäkymätön tyyppi on Python-olio, jonka sisällä C++-vektori on, joten funktio saa viittauksen samaan vektoriin."}
digraph {
  rankdir=LR; nodesep=0.35; ranksep=0.55;
  subgraph cluster_a {
    label="tuplaa(arvot): automaattinen muunnos"; color="#C9CED6"; style=rounded;
    lista [label="Python-lista\n[1.0, 2.0, 3.0]", fillcolor="#FFFFFF"];
    vali [label="väliaikainen\nstd::vector<double>", style="rounded,dashed,filled"];
    f1 [label="tuplaa(vector&)"];
    lista -> vali [label="kopio alkio\nkerrallaan"];
    f1 -> vali [label="muuttaa"];
  }
  subgraph cluster_b {
    label="kasvata(laskurit): läpinäkymätön tyyppi"; color="#C9CED6"; style=rounded;
    olio [label="Python-olio Laskurit,\nsisällä std::vector<int64_t>", fillcolor="#F3E2C7"];
    f2 [label="kasvata(vector&)"];
    f2 -> olio [label="muuttaa\nsamaa vektoria"];
  }
}
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
tyyppitarkistuksella joka kutsussa (luku 9).

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

```{.tuloste tiedosto="esimerkit/06-muunnokset/main.odotettu" rivit="3-5"}
```

```{.dot otsikko="Viitteet Python-olioiden välillä esimerkissä. `keep_alive<1, 2>` lisää viitteen ketjusta kumpaankin vaiheeseen, ja `reference_internal` viitteen palautetusta vaiheesta ketjuun. C++:n omat osoittimet (katkoviiva) eivät pidä mitään elossa."}
digraph {
  rankdir=LR; nodesep=0.4; ranksep=0.7;
  eka [shape=plain, style="", label=<<i>eka (Python-nimi)</i>>];
  ketju [label="Ketju\n(Python-olio)"];
  v1 [label="Vahvistus(2.0)"];
  v2 [label="Vahvistus(10.0)"];
  eka -> v1;
  ketju -> v1 [label="keep_alive"];
  ketju -> v2 [label="keep_alive"];
  v1 -> ketju [label="reference_internal", constraint=false];
  ketju -> v1 [style=dashed, label="C++: osoitin", fontcolor="#6B7280"];
  ketju -> v2 [style=dashed];
}
```

Tuloste näyttää, että väliaikaiset vaiheet
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

## Python-koodi C++:n kutsumana

Tähän asti Python on kutsunut C++:aa. Usein suunta on myös toinen:
C++-kirjasto ilmoittaa tapahtumasta takaisinkutsulla, tai sen rajapinta
on abstrakti luokka, jonka toteutus halutaan kirjoittaa Pythonilla.
Kummassakin tapauksessa C++ pitää hallussaan Python-oliota, joten
tämän luvun kysymys, kuka pitää kenet elossa, kääntyy toisin päin.

### Tallennettu takaisinkutsu

Otsake `<pybind11/functional.h>` muuntaa Python-kutsuttavan
`std::function`-olioksi. Kääre omistaa viitteen Python-funktioon,
joten funktio elää niin kauan kuin `std::function`, tässä hälyttimen
jäsenenä:

```{.cpp tiedosto="esimerkit/06-muunnokset/takaisin.cpp" osa="funktio"}
```

```{.python tiedosto="esimerkit/06-muunnokset/main.py" osa="takaisinkutsu"}
```

```{.tuloste tiedosto="esimerkit/06-muunnokset/main.odotettu" rivit="6-7"}
```

Sidottu metodi `ylitykset.append` pitää listan elossa, ja hälytin
pitää metodin. Toinen rivi näyttää virhepolun: takaisinkutsun nostama
Python-poikkeus muuttuu C++-poikkeukseksi `py::error_already_set`,
kulkee C++-koodin läpi ja palaa kutsujalle alkuperäisenä
`ValueError`ina. C++-koodin on siksi oltava poikkeusturvallista
(RAII), vaikka se itse ei heittäisi mitään. Viitteestä voi myös syntyä
kehä: jos takaisinkutsu viittaa hälyttimeen itseensä, kumpikaan ei
vapaudu, koska Pythonin roskienkeruu ei näe `std::function`in sisään.
Kehä katkaistaan asettamalla käsittelijä tyhjäksi tai käyttämällä
heikkoa viitettä (`weakref`).

Jokainen takaisinkutsu on kielten rajan ylitys C++:sta Pythoniin ja
maksaa saman kuin kutsu toiseen suuntaan (luku 9). Jos C++ kutsuu
funktiota omasta säikeestään, sen on ensin otettava tulkkilukko
(luku 10).

### Virtuaalifunktion ylikirjoitus Pythonista

Kun C++-rajapinta on abstrakti luokka, Python-luokka voi periä sen.
C++:n virtuaalitaulu ei kuitenkaan tiedä Python-metodeista, joten
väliin tarvitaan *trampoliiniluokka*, joka ylikirjoittaa jokaisen
virtuaalifunktion ja ohjaa kutsun Python-oliolle:

```{.cpp tiedosto="esimerkit/06-muunnokset/takaisin.cpp" osa="trampoliini"}
```

```{.cpp tiedosto="esimerkit/06-muunnokset/takaisin.cpp" osa="sidonta"}
```

```{.python tiedosto="esimerkit/06-muunnokset/main.py" osa="periva"}
```

```{.python tiedosto="esimerkit/06-muunnokset/main.py" osa="trampoliini"}
```

```{.tuloste tiedosto="esimerkit/06-muunnokset/main.odotettu" rivit="8-9"}
```

`summa_suodatettuna` on tavallinen C++-funktio, joka kutsuu
virtuaalifunktiota. Kun argumentti on Python-luokan olio, kutsu
päätyy trampoliinin kautta Python-metodiin. Makro
`PYBIND11_OVERRIDE_PURE` etsii metodin Python-oliosta ja nostaa
virheen, jos sitä ei ole; `PYBIND11_OVERRIDE` kutsuisi silloin
C++-kantaluokan toteutusta. Jos Python-luokka määrittelee oman
`__init__`-metodin, sen on kutsuttava `super().__init__()`, jotta
C++-osa oliosta rakentuu. nanobindissa vastaavat välineet ovat
`nb::callable`, otsake `<nanobind/stl/function.h>` ja makrot
`NB_TRAMPOLINE` ja `NB_OVERRIDE_PURE`.

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
- **Tallennettu takaisinkutsu omistaa viitteen.** Varo kehää, jossa
  takaisinkutsu viittaa olioon, joka säilyttää sen, ja muista, että
  Python-poikkeus kulkee C++-koodin läpi.
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
- Osaat välittää Python-funktion C++:lle takaisinkutsuksi ja kertoa,
  kuka pitää sen elossa ja mitä sen nostamalle poikkeukselle tapahtuu.
- Osaat toteuttaa C++:n abstraktin rajapinnan Python-luokalla
  trampoliinin avulla.
- Osaat valita `shared_ptr`-, `unique_ptr`- ja raakaosoitinsidonnan
  välillä omistajuuden mukaan.
