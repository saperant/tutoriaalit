# Pythonin C-API ja viitelaskenta

pybind11, nanobind, Cython ja `ctypes` ovat kaikki Pythonin
C-rajapinnan päällä. Rajapinta on tulkin oma: jokainen Python-olio on
C:ssä `PyObject *`, ja jokainen operaatio, attribuutin hausta
yhteenlaskuun, on C-funktio. Tässä luvussa kirjoitetaan pieni
laajennus suoraan C-API:lla. Tavoite ei ole, että laajennukset
kirjoitettaisiin näin, vaan että ymmärretään, mitä sidontakirjastot
tekevät, ja osataan lukea C-API:a käyttävää koodia ja sen virheitä.

## Viitelaskenta

CPython vapauttaa olion, kun sen viitemäärä putoaa nollaan. Python-
koodissa tulkki pitää laskurit kunnossa. C-koodissa sen tekee
ohjelmoija makroilla `Py_INCREF` ja `Py_DECREF`. Jokainen
`PyObject *` -osoitin on jompaakumpaa lajia:

- **Uusi viite** (*new reference*, *strong reference*): osoittimen
  haltija omistaa yhden viitteen ja vastaa sen vapauttamisesta
  `Py_DECREF`illä. Useimmat oliota palauttavat funktiot antavat uuden
  viitteen, esimerkiksi `PyObject_GetIter`, `PyIter_Next` ja
  `PyFloat_FromDouble`.
- **Lainattu viite** (*borrowed reference*): osoitin on käytettävissä,
  mutta joku muu omistaa viitteen. Sitä ei vapauteta, ja se on voimassa
  vain niin kauan kuin omistaja pitää olion elossa. Esimerkiksi
  `PyList_GET_ITEM` lainaa viitteen listan alkioon, ja funktion
  argumentit ovat lainattuja.

Dokumentaatio kertoo jokaisen funktion kohdalla, kumpaa lajia sen
paluuarvo on. Kaksi virhetyyppiä ovat yleisiä. Unohtunut `Py_DECREF`
vuotaa olion, eikä sitä huomaa muuten kuin kasvavasta muistista.
Ylimääräinen `Py_DECREF` tai lainatun viitteen vapautus vapauttaa
olion, jota joku muu vielä käyttää, ja kaatuu myöhemmin jossain aivan
muualla.

## Iterointi ja virheet

Funktio laskee minkä tahansa iteroitavan summan:

```{.c tiedosto="esimerkit/10-c-api/raaka.c" osa="summa"}
```

Virheet käsitellään C-API:ssa kahdella tavalla yhtä aikaa: funktio
asettaa *virhetilan* (poikkeuksen, joka odottaa nostamista) ja palauttaa
erikoisarvon, tavallisesti `NULL`. Kutsujan on tarkistettava
paluuarvo, siivottava omat viitteensä ja palautettava myös `NULL`,
jolloin poikkeus etenee Pythoniin.

- `PyObject_GetIter` asettaa `TypeError`in, jos argumentti ei ole
  iteroitava. Funktio vain palauttaa `NULL`.
- `PyFloat_AsDouble` palauttaa `-1.0` sekä virheessä että luvulle
  `-1.0`, joten virhe erotetaan `PyErr_Occurred`illa.
- `PyIter_Next` palauttaa `NULL` sekä iteroinnin loppuessa että
  virheessä. Ero nähdään jälleen `PyErr_Occurred`illa.
- Jokainen poistumispolku vapauttaa iteraattorin. Suuremmissa
  funktioissa käytetään C:n `goto`-siivousta: kaikki virhepolut
  hyppäävät funktion loppuun, jossa vapautetaan `Py_XDECREF`illä
  (joka sallii `NULL`in).

## Lainattu viite paluuarvona

Toinen funktio palauttaa listan ensimmäisen alkion:

```{.c tiedosto="esimerkit/10-c-api/raaka.c" osa="ensimmainen"}
```

`PyList_GET_ITEM` lainaa viitteen, mutta funktion paluuarvon on oltava
uusi viite: kutsuja vapauttaa sen, kun ei enää tarvitse sitä. Siksi
alkio palautetaan `Py_NewRef`illä, joka kasvattaa laskuria ja palauttaa
saman osoittimen. Jos `Py_NewRef` unohtuu, jokainen kutsu pienentää
alkion viitemäärää yhdellä, ja alkio vapautetaan, vaikka lista
yhä viittaa siihen.

Testi kutsuu funktiota satatuhatta kertaa ja vertaa viitemäärän
ennen ja jälkeen. `sys.getrefcount` palauttaa olion viitemäärän
(yhden enemmän, koska argumentti on itsekin viite):

```{.python tiedosto="esimerkit/10-c-api/main.py" osa="viitteet"}
```

```{.tuloste tiedosto="esimerkit/10-c-api/main.odotettu"}
```

Viitemäärän vertailu on yksinkertainen ja tehokas tapa testata
C-API-koodia. Vuoto kasvattaa määrää, ylimääräinen vapautus pienentää
sitä, ja silmukka tekee pienestäkin virheestä näkyvän.

Vapaasäikeisessä Pythonissa (luku 9) lainatut viitteet ovat
vaarallisempia: toinen säie voi poistaa alkion listasta ja vapauttaa
sen, kun lainattua osoitinta vielä käytetään. Python 3.13 lisäsi
siksi funktioita, jotka palauttavat uuden viitteen, kuten
`PyList_GetItemRef`.

## Moduulin määrittely

Moduuli on taulukko funktioita ja kuvaus, jonka alustusfunktio
`PyInit_<nimi>` antaa tulkille:

```{.c tiedosto="esimerkit/10-c-api/raaka.c" osa="moduuli"}
```

`METH_O` kertoo, että funktio ottaa täsmälleen yhden argumentin.
`METH_VARARGS | METH_KEYWORDS` ja `PyArg_ParseTupleAndKeywords` ovat
yleinen tapa useammalle argumentille, ja `METH_FASTCALL` välttää
argumenttituplan luomisen. `PY_SSIZE_T_CLEAN` ennen otsaketta
vaaditaan Python 3.10–3.12:ssa, jos argumentteja jäsennetään
`#`-muotoilumerkeillä. Python 3.13:ssa se on oletus.

Esimerkin *yksivaiheinen alustus* (`PyModule_Create`) on vanhin ja
lyhin tapa. *Monivaiheinen alustus* (PEP 489, `PyModuleDef_Init` ja
`Py_mod_exec`-paikat) on nykyinen suositus. Se tukee alitulkkeja ja
moduulin uudelleenlatausta, ja vapaasäikeisyys ilmoitetaan siinä
`Py_mod_gil`-paikalla. pybind11 3 käyttää sitä.

## Mitä sidontakirjastot tekevät

Luvun 5 `.def("lisaa", &Tilasto::lisaa, py::arg("x"))` tuottaa C++-
mallien avulla suunnilleen tämän luvun koodin:

- argumenttien jäsennys ja tyyppitarkistus (`PyFloat_AsDouble` ja
  virhetila),
- C++-olion haku Python-oliosta ja metodin kutsu,
- C++-poikkeuksen nappaus ja muunnos virhetilaksi,
- paluuarvon muunnos uudeksi viitteeksi,
- viitelaskenta: `py::object` on RAII-kääre, joka kutsuu
  `Py_DECREF`iä purkajassaan, kuten `std::shared_ptr`.

Viimeinen kohta on tärkein. C++:n RAII tekee viitelaskennasta
automaattista samalla tavalla kuin muistinhallinnasta, ja siksi
sidontakirjastoilla kirjoitettu koodi on turvallisempaa kuin käsin
kirjoitettu C-API-koodi.

## Rajoitettu API

Python-otsakkeet sisältävät tulkin sisäisiä rakenteita, jotka
muuttuvat versioiden välillä. Siksi laajennus on käännettävä jokaiselle
Python-versiolle erikseen. *Rajoitettu API* (*Limited API*) on
osajoukko, joka on lupattu vakaaksi: makro `Py_LIMITED_API` ennen
otsaketta piilottaa kaiken muun. Sillä käännetty laajennus toimii
kaikissa myöhemmissä 3.x-versioissa. Binäärimuotoa kutsutaan *vakaaksi
ABI:ksi*, ja pyörän tunniste on `abi3` (luku 12).

Rajoitettu API ei sisällä esimerkin `PyList_GET_ITEM`- ja
`PyList_GET_SIZE`-makroja, jotka lukevat listan rakennetta suoraan,
vaan niiden funktioversiot (`PyList_GetItem`, `PyList_Size`).
Funktiokutsu on hieman hitaampi, ja se on vakaan ABI:n hinta.

## Käytännössä

- **Älä kirjoita laajennuksia raa'alla C-API:lla**, jos pybind11 tai
  nanobind on mahdollinen. Viitelaskenta ja virhepolut ovat helppo
  tehdä väärin, ja virheet näkyvät kaukana syystään.
- **Tarkista dokumentaatiosta jokaisen funktion viitelaji.** "Return
  value: New reference" tai "Borrowed reference" lukee jokaisen
  funktion kohdalla.
- **Paluuarvo on aina uusi viite.** Lainattu viite palautetaan
  `Py_NewRef`illä.
- **Virhe: aseta virhetila, siivoa, palauta `NULL`.** Jos kutsuttu
  funktio asetti virheen, älä korvaa sitä omallasi.
- **Testaa viitemäärä silmukassa** `sys.getrefcount`illa, ja aja
  testit Pythonin debug-käännöksellä (`python3-dbg`), joka tarkistaa
  viitelaskureita jatkuvasti.
- **Sudenkuoppa:** lainattu viite olioon, jonka joku muu voi
  vapauttaa välissä. Mikä tahansa Python-kutsu voi ajaa Python-koodia
  (`__del__`, `__eq__`) ja muuttaa listaa, josta viite lainattiin.
  Kasvata viitemäärää ennen kuin kutsut mitään.

## Itsearviointi

- Osaat erottaa uuden ja lainatun viitteen ja käsitellä kummankin
  oikein.
- Osaat käsitellä C-API:n virheet: virhetila, erikoisarvo ja siivous
  jokaisella poistumispolulla.
- Osaat testata viitelaskennan oikeellisuuden.
- Osaat selittää, mitä sidontakirjasto tekee yhden metodisidonnan
  takana ja mitä rajoitettu API tarkoittaa.
