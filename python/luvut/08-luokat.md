# Luokat, dataluokat ja protokollat {.runko-omat-tyypit}

Pythonin luokat ovat joustavia: attribuutteja voi lisätä ajon aikana,
kaikki on julkista ja mikä tahansa metodi voidaan korvata. Joustavuus
tekee kurinalaisuudesta tärkeää. Tämä luku esittelee tavat, joilla
ammattimainen Python-koodi määrittelee omat tyyppinsä: dataluokat
arvo-olioille, erikoismetodit sisäänrakennetun kaltaiselle
käytökselle, protokollat rajapinnoille ja luettelotyypit tiloille.

## Luokan perusteet lyhyesti

- `__init__` alustaa olion; konstruktori on itse luokka-olion kutsu.
- `self` on eksplisiittinen ensimmäinen parametri.
- Yksityisyys on sopimus: `_nimi` on sisäinen. `__nimi` muuttaa nimeä
  (*name mangling*) perinnän törmäysten välttämiseksi, ei suojaksi.
- `@property` tekee metodista attribuutin. Julkinen attribuutti
  voidaan myöhemmin muuttaa ominaisuudeksi rikkomatta kutsujia, joten
  Pythonissa ei kirjoiteta `get_x`/`set_x`-pareja varmuuden vuoksi.
- `@classmethod` saa luokan (`cls`) ja sopii vaihtoehtoisiksi
  konstruktoreiksi, kuten `Versio.jasenna`. `@staticmethod` on
  luokan nimiavaruudessa oleva tavallinen funktio; moduulitason funktio
  on usein parempi.
- Perintä: `class B(A)`, `super().__init__(...)`. Moniperinnässä
  metodit haetaan *MRO*-järjestyksessä (`B.__mro__`).

## Dataluokat

`@dataclass` tuottaa luokalle `__init__`-, `__repr__`- ja
`__eq__`-metodit kenttien tyyppiannotaatioista. Valitsimet lisäävät
ominaisuuksia: `frozen=True` estää muutokset ja tekee oliosta
hajautettavan, `order=True` tuottaa vertailut kenttien järjestyksessä ja
`slots=True` käyttää `__slots__`-rakennetta, joka säästää muistia ja
estää kirjoitusvirheellisten attribuuttien luomisen.

```{.python tiedosto="esimerkit/08-dataluokat.py" osa="tilaus"}
```

```{.python tiedosto="esimerkit/08-dataluokat.py" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/08-dataluokat.odotettu"}
```

- Versiot lajittuvat numeerisesti (`1.9.0` ennen `1.10.0`), koska
  `order=True` vertaa kenttiä monikkona. Merkkijonoina ne lajittuisivat
  väärin.
- Muuttuva oletusarvo annetaan `field(default_factory=list)`-muodossa.
  `muutokset: list[str] = []` on virhe, jonka dataluokka estää.
- `__post_init__` validoi olion luonnin yhteydessä. Kelvoton olio ei
  synny lainkaan (*parse, don't validate*).
- `dataclasses.replace` luo muokatun kopion jäädytetystä oliosta.

Dataluokka on oikea valinta tietueille ja arvo-olioille. Tavallinen
luokka on parempi, kun olio kapseloi tilaa ja sen invariantteja, ja
ulkoiseen dataan liittyvään validointiin käytetään usein kirjastoa
kuten Pydantic. `typing.NamedTuple` on muuttumaton tietue, joka on
samalla monikko; sitä käytetään, kun paluuarvo halutaan purkaa.

## Erikoismetodit

Erikoismetodit (*dunder methods*, kahdet alaviivat) liittävät luokan
kielen operaattoreihin ja sisäänrakennettuihin funktioihin. Esimerkki
rahatyypistä, joka pyöristää sentteihin ja estää eri valuuttojen
yhdistämisen:

```{.python tiedosto="esimerkit/08-raha.py" osa="raha"}
```

```{.python tiedosto="esimerkit/08-raha.py" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/08-raha.odotettu"}
```

`__add__` antaa `+`-operaattorin ja sitä kautta `sum`-funktion, `__lt__`
riittää `min`-, `max`- ja `sorted`-funktioille, ja `__str__` määrää
tulostuksen. Jäädytetyn dataluokan kenttää ei voi asettaa tavallisesti,
joten `__post_init__` käyttää `object.__setattr__`-kutsua. Rivin
`from __future__ import annotations` ansiosta metodien annotaatiot
voivat viitata luokkaan `Raha` ennen kuin se on määritelty.

| Metodi | Käyttö | Metodi | Käyttö |
|--------|--------|--------|--------|
| `__repr__`, `__str__` | `repr()`, `str()`, `print` | `__len__` | `len()`, totuusarvo |
| `__eq__`, `__hash__` | `==`, `dict`-avain | `__iter__` | `for`, purku |
| `__lt__` ym. | vertailu, lajittelu | `__contains__` | `in` |
| `__add__`, `__mul__` | aritmetiikka | `__getitem__` | `olio[i]` |
| `__enter__`, `__exit__` | `with` | `__call__` | `olio()` |
| `__bool__` | `if olio:` | `__format__` | f-merkkijonon määre |

Jos luokka määrittelee `__eq__`-metodin, sen on määriteltävä myös
`__hash__` tai oltava hajauttamaton. Dataluokka hoitaa tämän:
`frozen=True` tuottaa molemmat. Kun operaatio ei tue toisen operandin
tyyppiä, metodi palauttaa `NotImplemented`, jolloin Python kokeilee
toisen operandin käänteistä metodia (`__radd__`).

## Protokollat ja abstraktit kantaluokat

Pythonissa on kaksi tapaa ilmaista rajapinta. `typing.Protocol`
määrittelee *rakenteellisen* rajapinnan: mikä tahansa luokka, jolla on
oikeat metodit, kelpaa ilman perintää. Tämä on duck typing, jonka mypy
tarkistaa.

```{.python tiedosto="esimerkit/08-protokollat.py" osa="protokolla"}
```

`Muistivarasto` ei tiedä `Tallennin`-protokollasta mitään, mutta mypy
hyväksyy sen, koska metodien allekirjoitukset täsmäävät. Rajapinta
määritellään sen käyttäjän puolelle, ja toteutukset voivat olla muissa
moduuleissa tai kolmansien osapuolten kirjastoissa. Luvun 11 esimerkki
käyttää tätä riippuvuuksien kääntämiseen.

`abc.ABC` on *nimellinen* rajapinta: aliluokan on perittävä se, ja
`@abstractmethod`-metodit on toteutettava ennen kuin olion voi luoda.
ABC sopii, kun kantaluokka jakaa toteutusta (*template method*):

```{.python tiedosto="esimerkit/08-protokollat.py" osa="abc"}
```

```{.tuloste tiedosto="esimerkit/08-protokollat.odotettu"}
```

Mypy huomaa abstraktin luokan instansioinnin jo tarkistuksessa;
esimerkki ohittaa sen kommentilla `type: ignore[abstract]` näyttääkseen
ajonaikaisen virheen.

## Luettelotyypit

`enum.Enum` määrittelee suljetun joukon nimettyjä arvoja. Yhdessä
`match`-lauseen ja `typing.assert_never`-funktion kanssa mypy tarkistaa,
että jokainen arvo käsitellään:

```{.python tiedosto="esimerkit/08-tila.py" osa="tila"}
```

```{.tuloste tiedosto="esimerkit/08-tila.odotettu"}
```

Jos luetteloon lisätään arvo `ARKISTOITU` eikä `match`-lauseeseen
lisätä tapausta, viimeinen haara tarjoaa `assert_never`-funktiolle
`Tila.ARKISTOITU`-arvon, ja mypy raportoi virheen. Näin tilakone pysyy
kattavana. `StrEnum` ja `IntEnum` ovat merkkijonoina ja lukuina
toimivia luetteloita, esimerkiksi tiedostomuotoja ja rajapintoja varten.

## Käytännössä

- **Dataluokka tietueille, jäädytettynä oletuksena.**
  `@dataclass(frozen=True, slots=True)` tuottaa hajautettavan,
  vertailukelpoisen ja muistitehokkaan arvo-olion. Muutos tehdään
  `replace`-kutsulla.
- **Arvo-olio primitiivien sijaan** (*value object*): `Raha`, `Versio`
  ja `Sahkoposti` validoivat itsensä kerran, ja virheellinen arvo ei
  pääse järjestelmään. Tämä korjaa *primitive obsession* -ongelman.
- **Protokolla rajapinnaksi, ABC jaetulle toteutukselle.** Protokolla
  ei sido toteutusta kantaluokkaan ja sopii testien valeolioille. Syvä
  perintähierarkia on Pythonissa harvinainen; koostaminen on oletus.
- **Vaihtoehtoiset konstruktorit luokkametodeina:** `Versio.jasenna`,
  `datetime.fromisoformat`, `Path.home`.
- **Luettelo ja kattava `match` tiloille** merkkijonovakioiden sijaan.
- **Hinta:** tavallinen olio pitää attribuuttinsa sanakirjassa
  (`__dict__`), noin 100–200 tavua tyhjänäkin. `__slots__` (tai
  `slots=True`) pudottaa koon murto-osaan ja nopeuttaa attribuuttihakua
  hieman. Miljoonien olioiden ohjelmissa ero on merkittävä.
- **Sudenkuopat:** `__eq__` ilman `__hash__`-metodia, luokka-attribuutti
  muuttuvana oletusarvona (`class A: x = []` jaetaan kaikkien olioiden
  kesken) ja `isinstance`-ketjut, jotka kuuluisivat polymorfiseen
  metodiin tai `match`-lauseeseen.

## Itsearviointi

- Osaat määritellä dataluokan valitsimilla `frozen`, `slots` ja
  `order`, validoida sen `__post_init__`-metodissa ja muokata sitä
  `replace`-kutsulla.
- Osaat toteuttaa arvotyypin erikoismetodeilla niin, että se toimii
  operaattoreiden, `sum`-, `min`- ja `sorted`-funktioiden kanssa.
- Osaat valita `Protocol`- ja `ABC`-rajapinnan välillä ja perustella
  valinnan.
- Osaat mallintaa tilat luettelotyypillä ja tehdä `match`-lauseesta
  mypyn tarkistaman kattavan.
- Osaat kertoa, mitä `__slots__` säästää ja milloin sillä on merkitystä.
