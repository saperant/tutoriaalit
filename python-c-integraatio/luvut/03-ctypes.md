# C-kirjasto ctypesillä

Helpoin tapa kutsua C-koodia on vakiokirjaston `ctypes`. Se lataa
jaetun kirjaston ajon aikana ja kutsuu sen funktioita suoraan ilman
käännösvaihetta Python-puolella. Hinta on se, että `ctypes` ei näe
C-otsaketta: funktioiden tyypit kerrotaan sille käsin, eikä mikään
tarkista, että kerrottu vastaa todellista. Virhe ei näy poikkeuksena,
vaan väärinä arvoina tai kaatuneena tulkkina.

## Kirjaston rajapinta

Esimerkkikirjasto laskee CRC-32-tarkistussumman ja tilastoja. Sen
rajapinta on tavallista C:tä, ja se näyttää neljä asiaa, jotka
toistuvat lähes jokaisessa C-kirjastossa: puskuri ja pituus,
ulostuloparametrit ja virhe `errno`ssa, takaisinkutsu käyttäjän
osoittimen kanssa sekä kirjaston varaama muisti:

```{.c tiedosto="esimerkit/03-ctypes/tarkistus.h" osa="rajapinta"}
```

Kirjasto käännetään jaetuksi kirjastoksi, jota mikä tahansa kieli voi
ladata. Python-sidontoja se ei tunne:

```{.makefile tiedosto="esimerkit/Makefile" osa="saannot"}
```

Säännöistä vain ensimmäinen koskee tätä lukua. Muut kääntävät
myöhempien lukujen laajennusmoduulit.

## Lataus ja funktioiden tyypit

`ctypes.CDLL` lataa kirjaston. Polku muodostetaan skriptin
sijainnista, jotta ohjelma toimii mistä hakemistosta tahansa
käynnistettynä. Pelkällä nimellä (`CDLL("libtarkistus.so")`) haku
tehdään dynaamisen linkittäjän hakupoluista.

```{.python tiedosto="esimerkit/03-ctypes/main.py" osa="lataus"}
```

`argtypes` ja `restype` ovat pakolliset jokaiselle funktiolle. Ilman
niitä `ctypes` olettaa, että jokainen argumentti ja paluuarvo on
`int`. 64-bittisellä alustalla `int` on 32-bittinen, joten osoitin tai
`size_t` katkeaa puoliksi, ja liukuluku välitetään väärässä
rekisterissä. Ohjelma voi silti näyttää toimivan pienillä syötteillä.
`argtypes` myös tarkistaa kutsut: väärän tyyppinen argumentti antaa
`ArgumentError`in eikä muistivirhettä.

| C | ctypes |
|---|--------|
| `int`, `unsigned` | `c_int`, `c_uint` |
| `int32_t`, `uint64_t` | `c_int32`, `c_uint64` |
| `size_t`, `ssize_t` | `c_size_t`, `c_ssize_t` |
| `double` | `c_double` |
| `const char *` (merkkijono, tavut) | `c_char_p` |
| `T *` | `POINTER(T)` |
| `void *` | `c_void_p` |
| `T[n]` | `T * n` |
| funktio-osoitin | `CFUNCTYPE(paluu, argumentit...)` |

## Puskurit ja ulostuloparametrit

Python-funktio kääreenä piilottaa `ctypes`-yksityiskohdat
kutsujalta:

```{.python tiedosto="esimerkit/03-ctypes/main.py" osa="kaareet"}
```

- **`bytes` ja `c_char_p`.** `bytes`-olion sisältö välitetään
  osoittimena ilman kopiota. C ei saa kirjoittaa siihen, koska
  `bytes` on muuttumaton ja sama olio voi olla käytössä muualla.
  Kirjoitettava puskuri luodaan `ctypes.create_string_buffer(n)`illä
  tai `bytearray`sta (`(c_char * n).from_buffer(ba)`).
- **`(c_double * n)(*arvot)`** luo C-taulukon ja kopioi listan siihen.
  Suurille datamäärille tämä on hidasta. NumPy-taulukon osoite saadaan
  ilman kopiota: `a.ctypes.data_as(POINTER(c_double))`, kunhan
  taulukko on yhtenäinen ja oikean tyyppinen (luku 8).
- **`byref(x)`** välittää osoitteen ulostuloparametriin. Se on
  `pointer(x)`:ää kevyempi, koska se ei luo osoitinoliota.
- **`errno`.** `use_errno=True` latauksessa saa `ctypes`in
  tallentamaan `errno`n heti kutsun jälkeen. Muuten tulkki ehtii
  muuttaa sitä ennen kuin Python-koodi lukee sen. Virhe muutetaan
  `OSError`iksi, kuten vakiokirjasto tekee.

## Takaisinkutsut

Paloittain laskeva funktio kutsuu takaisinkutsua jokaisen palan
jälkeen. Takaisinkutsun tyyppi määritellään `CFUNCTYPE`llä samaan
tapaan kuin funktion tyyppi:

```{.python tiedosto="esimerkit/03-ctypes/main.py" osa="takaisinkutsu-tyyppi"}
```

Python-funktio kääritään tyyppiin, ja kääre välitetään C:lle:

```{.python tiedosto="esimerkit/03-ctypes/main.py" osa="paloittain"}
```

Kääre (`kutsu`) on Python-olio, joka omistaa C:lle annetun
konekielisen tynkäfunktion. Jos kääre vapautetaan, kun C vielä
säilyttää osoitinta, seuraava kutsu hyppää vapautettuun muistiin.
Tässä kääre on paikallinen muuttuja, joka elää koko C-kutsun ajan. Jos
C-kirjasto tallentaa takaisinkutsun myöhempää käyttöä varten
(tapahtumankäsittelijät, ajastimet), kääreestä on pidettävä viite
niin kauan kuin kirjasto voi kutsua sitä.

Takaisinkutsussa nostettua poikkeusta ei voi välittää C-koodin läpi.
`ctypes` tulostaa sen virhetulosteeseen, eikä C-koodi voi luottaa
saamaansa paluuarvoon. Siksi takaisinkutsu ei saa päästää poikkeuksia
ulos, ja keskeytys ilmaistaan paluuarvolla, kuten rajapinta
määrittelee.
C-kirjasto kertoo keskeytyksestä `errno`lla `ECANCELED`.

## Kirjaston varaama muisti

`heksana` palauttaa kirjaston `malloc`illa varaaman merkkijonon. Sen
vapauttaa kirjasto omalla funktiollaan:

```{.python tiedosto="esimerkit/03-ctypes/main.py" osa="heksana"}
```

Paluutyyppi on `c_void_p` eikä `c_char_p`. `c_char_p`-paluuarvo
muunnetaan heti `bytes`-olioksi, ja alkuperäinen osoite katoaa, joten
muisti vuotaisi. Osoite talletetaan, sisältö kopioidaan
`string_at`illa, ja `finally` vapauttaa muistin myös, jos dekoodaus
epäonnistuu.

Vapautus kirjaston omalla funktiolla on sääntö, ei tyyliseikka.
Kirjasto voi käyttää eri C-ajonaikaista kirjastoa tai omaa
muistinhallintaansa kuin kutsuja, ja Windowsissa jokaisella DLL:llä voi
olla oma kekonsa. Toisen kirjaston `malloc`illa varatun muistin
vapauttaminen omalla `free`llä on määrittelemätöntä käytöstä.

```{.tuloste tiedosto="esimerkit/03-ctypes/main.odotettu"}
```

CRC vastaa vakiokirjaston `zlib.crc32`:ta, joten C-toteutus on
oikein. Tyhjä syöte antaa `EINVAL`in, ja keskeytys pysäytti
laskennan kolmannen palan sijaan toisen jälkeen.

## cffi

cffi on `ctypes`in vaihtoehto, joka lukee tyypit C-määrittelyistä:

```text
from cffi import FFI
ffi = FFI()
ffi.cdef("uint32_t crc32_laske(const uint8_t *data, size_t n);")
lib = ffi.dlopen("./build/libtarkistus.so")
print(lib.crc32_laske(b"abc", 3))
```

Tyyppejä ei siis kirjoiteta toiseen kertaan Pythonin tyyppiolioina.
cffi:n *API-tila* (`ffi.set_source` ja `ffi.compile`) kääntää
C-kääntäjällä pienen laajennusmoduulin, joka tarkistaa määrittelyt
otsaketta vasten. Se on nopeampi ja turvallisempi kuin `ctypes` tai
cffi:n *ABI-tila* (`dlopen`), koska kääntäjä huomaa väärät tyypit.
cffi on myös PyPy-tulkin suosittelema tapa kutsua C:tä. Se ei kuulu
vakiokirjastoon, joten tämä tutoriaali ei käytä sitä esimerkeissä.

## Käytännössä

- **`argtypes` ja `restype` jokaiselle funktiolle**, myös
  `restype = None` `void`-funktioille. Puuttuva määrittely on
  `ctypes`in yleisin virhe, eikä se aina näy heti: pienet kokonaisluvut
  kulkevat oikein, ja vasta katkennut osoitin kaatuu.
- **Kääri jokainen C-funktio Python-funktioon**, joka muuntaa tyypit,
  tarkistaa paluuarvon ja nostaa poikkeuksen. Muu koodi ei näe
  `ctypes`iä.
- **Paluuarvo `c_void_p`, kun kirjasto varaa muistin**, ja vapautus
  kirjaston omalla funktiolla `finally`-lohkossa.
- **Pidä takaisinkutsun kääre elossa** niin kauan kuin C voi kutsua
  sitä. Tallenna se olion attribuuttiin, jos kirjasto säilyttää
  osoitinta.
- **`ctypes` vapauttaa tulkkilukon** jokaisen kutsun ajaksi (luku 9),
  joten pitkä C-kutsu ei estä muita Python-säikeitä. Kutsun oma
  hinta on silti mikrosekunnin luokkaa, joten tuhansia pieniä kutsuja
  silmukassa ei kannata tehdä.
- **Sudenkuoppa:** rakenteet. `ctypes.Structure`n kenttien järjestys,
  tyypit ja kohdistus on kirjoitettava täsmälleen kuin C-otsakkeessa.
  Pieni ero siirtää kaikkia kenttiä. Tähän cffi:n API-tila tai
  pybind11 on turvallisempi.
- **Milloin `ctypes` riittää:** muutama funktio valmiissa
  C-kirjastossa, eikä käännösvaihetta haluta. Laajalle tai usein
  kutsutulle rajapinnalle kannattaa tehdä laajennusmoduuli.

## Itsearviointi

- Osaat ladata jaetun kirjaston `ctypes`illä ja määritellä funktioiden
  argumentti- ja paluutyypit oikein.
- Osaat välittää puskurit ja ulostuloparametrit sekä muuttaa `errno`n
  Python-poikkeukseksi.
- Osaat välittää Python-funktion C:n takaisinkutsuksi ja perustella,
  miksi kääreestä on pidettävä viite.
- Osaat käsitellä kirjaston varaaman muistin niin, ettei se vuoda eikä
  vapaudu väärällä vapautusfunktiolla.
