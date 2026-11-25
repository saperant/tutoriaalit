# Tulkkilukko ja säikeet

CPythonin tavallisessa tulkissa on *globaali tulkkilukko* (*global
interpreter lock*, GIL). Vain se säie, jolla lukko on, saa suorittaa
Python-koodia tai koskea Python-olioihin. Lukko suojaa tulkin sisäisiä
rakenteita, kuten viitelaskureita, ilman että jokaista oliota
tarvitsee lukita erikseen. Tulkki vaihtaa lukon säikeeltä toiselle
säännöllisesti ja aina, kun säie odottaa I/O:ta.

Laajennusmoduuli saa lukon mukanaan, kun Python kutsuu sitä, ja pitää
sitä koko kutsun ajan, ellei se vapauta sitä itse. Pitkä C++-laskenta
lukko varattuna pysäyttää siis kaikki muut Python-säikeet. Toisaalta
C++-koodi, joka on vapauttanut lukon, voi laskea rinnakkain muiden
säikeiden kanssa, mihin puhdas Python ei pysty.

## Lukon vapauttaminen

Esimerkkifunktio odottaa, että toinen säie asettaa lipun. Lippu
asetetaan Python-säikeestä, joten se tarvitsee lukon:

```{.cpp tiedosto="esimerkit/10-gil/rinnakkain.cpp" osa="odotus"}
```

`py::gil_scoped_release` on RAII-olio. Muodostin vapauttaa lukon ja
purkaja ottaa sen takaisin, myös poikkeuksen sattuessa. nanobindissa
sama on `nb::gil_scoped_release`, ja C-API:ssa makroparit
`Py_BEGIN_ALLOW_THREADS` ja `Py_END_ALLOW_THREADS`.

```{.python tiedosto="esimerkit/10-gil/main.py" osa="odotus"}
```

```{.ajoituskaavio otsikko="Kaksi koetta aikajanalla (periaatekuva, ei mittakaavassa: ensimmäisen kokeen odotus kestää 500 ms:n aikarajaan asti). Alin rivi kertoo, kummalla säikeellä tulkkilukko on; viivoitus tarkoittaa, että lukko on vapaa tai säie on päättynyt."}
{"signal": [
  ["lukko varattuna",
   {"name": "pääsäie", "wave": "=.......=..", "data": ["C++: odota_lippua, aikaraja", "False"]},
   {"name": "asettaja", "wave": "=.=.....=..", "data": ["nukkuu", "odottaa lukkoa", "asettaa"]},
   {"name": "lukko", "wave": "=.......=..", "data": ["pääsäie", "asettaja"]}],
  {},
  ["lukko vapautettuna",
   {"name": "pääsäie", "wave": "=....=.....", "data": ["C++: odota_lippua", "True"]},
   {"name": "asettaja", "wave": "=.=..x.....", "data": ["nukkuu", "asettaa"]},
   {"name": "lukko", "wave": "x.=..=.....", "data": ["asettaja", "pääsäie"]}]
]}
```

Ensimmäisessä kokeessa C++ odotti lukko varattuna. Asettajasäie
heräsi unestaan mutta ei päässyt suorittamaan seuraavaa riviään, joten
odotus päättyi aikarajaan. Toisessa kokeessa lukko oli vapaana, ja
lippu asettui heti.

Lukon vapauttamisessa on yksi ehdoton sääntö: **vapautettuna ei
kosketa yhteenkään Python-olioon.** Ei viitelaskuria, ei metodikutsua,
ei poikkeuksen nostamista Python-rajapinnalla. Myös pybind11:n
`py::object`, `py::array` ja `py::list` ovat Python-olioita. Data
luetaan C++-muuttujiin ennen vapautusta, ja tulos muunnetaan
Python-olioksi vasta, kun lukko on otettu takaisin.

## C++-säikeet

C++-säikeet eivät tarvitse lukkoa, kunhan ne käsittelevät vain
C++-dataa. NumPy-taulukon muisti on tavallista muistia, joten sen
osoite luetaan lukon kanssa, ja itse lasku tehdään ilman:

```{.cpp tiedosto="esimerkit/10-gil/rinnakkain.cpp" osa="saikeet"}
```

```{.python tiedosto="esimerkit/10-gil/main.py" osa="saikeet"}
```

`std::jthread` liittyy säikeeseensä purkajassaan, joten lohkon
lopussa kaikki säikeet ovat valmiita ennen kuin lukko otetaan
takaisin. Taulukko pysyy elossa koko laskun ajan, koska `a` on
funktion argumentti, joka pitää siitä viitteen. Jos Python-säie
muuttaisi taulukkoa samaan aikaan, se olisi datakilpa kuten missä
tahansa jaetussa muistissa. Lukko ei suojaa NumPy-taulukon sisältöä.

Jokaisella säikeellä on oma osasumma, ja osat summataan lopuksi.
Jaettu summamuuttuja vaatisi atomisen operaation tai lukon, ja
vierekkäiset `osat`-alkiot voivat silti hidastaa toisiaan, kun ne
ovat samalla välimuistirivillä (*false sharing*). Tässä tämä ei
haittaa, koska jokainen säie kirjoittaa omaan muuttujaansa vain
silmukassa. Suorituskykykriittisessä koodissa osasumma pidetään
paikallisena muuttujana ja kirjoitetaan taulukkoon kerran lopussa.

## Python-kutsu C++-säikeestä

Kun C++-säie kutsuu Python-funktiota, sen on ensin otettava lukko.
`py::gil_scoped_acquire` tekee sen ja luo säikeelle tarvittaessa
Pythonin säietilan:

```{.cpp tiedosto="esimerkit/10-gil/rinnakkain.cpp" osa="takaisinkutsu"}
```

```{.python tiedosto="esimerkit/10-gil/main.py" osa="takaisinkutsu"}
```

```{.tuloste tiedosto="esimerkit/10-gil/main.odotettu"}
```

Kutsuja vapauttaa lukon ennen kuin odottaa taustasäiettä. Jos se
pitäisi lukkoa ja odottaisi säiettä, joka odottaa lukkoa, ohjelma
jumittuisi lopullisesti: tämä on kielten rajan yleisin lukkiutuminen.
Sama tilanne syntyy, kun C++-kirjasto kutsuu takaisinkutsua omasta
säikeestään ja kutsuja odottaa kirjastoa lukko varattuna.

## Vapaasäikeinen Python

Python 3.13:sta alkaen CPythonista on erillinen käännös ilman
tulkkilukkoa (PEP 703). Se tunnistetaan nimestä `python3.13t`, ja
Python 3.14:ssä se on virallisesti tuettu. Siinä Python-säikeet
ajavat Python-koodia aidosti rinnakkain, ja tulkin sisäiset
rakenteet on suojattu olio- ja rakennekohtaisilla lukoilla.

Laajennusmoduuleille tämä tarkoittaa kahta asiaa:

- **Moduulin on ilmoitettava olevansa säieturvallinen.** Esimerkin
  moduuli tekee sen pybind11:n valitsimella `py::mod_gil_not_used()`.
  nanobindissa sama on CMake-funktion `nanobind_add_module` valitsin
  `FREE_THREADED`. Jos ilmoitus puuttuu, vapaasäikeinen tulkki ottaa
  lukon uudelleen käyttöön koko prosessille ja varoittaa siitä,
  jolloin rinnakkaisuus katoaa.
- **Ilmoitus on lupaus.** Moduulin oma globaali tila, välimuistit ja
  C++-olioiden jaettu käyttö on suojattava itse, koska lukko ei enää
  sarjallista kutsuja. Esimerkin globaali lippu on `std::atomic`.
  `gil_scoped_release` ja `gil_scoped_acquire` ovat vapaasäikeisessä
  tulkissa vaarattomia, joten sama koodi toimii molemmissa.

Vapaasäikeinen tulkki on eri ABI, ja sille käännetään omat pyörät
(luku 12), joiden tunnisteessa on `t`, esimerkiksi `cp313t`.

## Käytännössä

- **Vapauta lukko jokaisessa pitkässä kutsussa**, joka ei koske
  Python-olioihin: laskenta, I/O, odotus. Raja on noin millisekunti;
  lyhyissä kutsuissa vapautus maksaa enemmän kuin hyödyttää.
- **Lue data ennen vapautusta, muunna tulos jälkeen.** Vapautettu
  lohko käsittelee vain C++-tyyppejä.
- **`gil_scoped_acquire` jokaisessa C++-säikeessä**, joka koskee
  Pythoniin, ja lyhyesti: ota, kutsu, vapauta.
- **Älä odota lukko varattuna** säiettä, joka voi tarvita lukkoa.
- **Suunnittele vapaasäikeisyyttä varten nyt.** Globaali muuttuva tila
  on ongelma jo nyt monessa Python-säikeessä, ja ilman lukkoa se on
  datakilpa.
- **Sudenkuoppa:** poikkeus vapautetussa lohkossa on turvallinen, koska
  RAII ottaa lukon takaisin ennen kuin pybind11 muuntaa poikkeuksen.
  Python-poikkeuksen (`py::error_already_set`) luominen vapautetussa
  lohkossa ei ole.

## Itsearviointi

- Osaat selittää, mitä tulkkilukko suojaa ja miksi laajennus pitää sitä
  oletuksena koko kutsun ajan.
- Osaat vapauttaa lukon pitkän C++-laskennan ajaksi ja kertoa, mitä
  vapautetussa lohkossa saa ja ei saa tehdä.
- Osaat laskea C++-säikeillä NumPy-taulukosta ja kutsua Python-funktiota
  C++-säikeestä lukitsematta ohjelmaa.
- Osaat kertoa, mitä vapaasäikeinen Python vaatii laajennusmoduulilta.
