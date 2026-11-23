# Tyypitys {.runko-omat-tyypit}

Python on dynaamisesti tyypitetty, mutta tyyppiannotaatiot ja
staattinen tarkistin ovat ammattimaisen Python-koodin oletus. Tulkki
ei tarkista annotaatioita, vaan ne tallentuvat olioiden
`__annotations__`-attribuuttiin. Tarkistuksen tekee erillinen työkalu,
kuten mypy tai Pyright, samalla tavalla kuin kääntäjä staattisesti
tyypitetyssä kielessä. Tämän tutoriaalin esimerkit tarkistetaan
`mypy --strict` -tilassa.

## Miksi tyypittää

Tyypit ovat tarkistettua dokumentaatiota. Ne kertovat, mitä funktio
ottaa ja palauttaa, ja tarkistin pitää ne totena koodin muuttuessa.
Suurin yksittäinen hyöty on `None`-arvon käsittely:

```{.python tiedosto="esimerkit/09-none.ei-kaanny.py"}
```

Mypy hylkää merkityn rivin:

```text
error: Item "None" of "str | None" has no attribute "upper"  [union-attr]
```

Yhdistetyyppi `A | B` (3.10) hyväksyy kummankin tyypin. `str | None`
(vanhemmassa koodissa `Optional[str]`) pakottaa käsittelemään
puuttuvan arvon. `if osoite is not None:` *kaventaa*
tyypin lohkon sisällä `str`-tyypiksi. Kaventavat myös `isinstance`,
`match`-hahmot, `assert` ja aikainen paluu.

## Perussyntaksi

| Merkintä | Merkitys |
|----------|----------|
| `x: int = 0` | muuttuja |
| `def f(a: str, *, n: int = 1) -> bool:` | funktio |
| `list[int]`, `dict[str, list[int]]`, `tuple[int, str]` | kokoelmat |
| `tuple[int, ...]` | vaihtelevan pituinen monikko |
| `Callable[[int, str], bool]` | kutsuttava |
| `Iterable[T]`, `Iterator[T]`, `Sequence[T]`, `Mapping[K, V]` | abstraktit kokoelmat (`collections.abc`) |
| `Any` | tarkistus pois päältä |
| `object` | mikä tahansa, mutta vain `object`-operaatiot sallittu |
| `Literal["r", "w"]` | tietyt arvot |
| `Final`, `ClassVar` | vakio, luokkamuuttuja |
| `Self` | metodin palauttama oma luokka |

Parametreissa käytetään abstrakteja tyyppejä (`Iterable`, `Mapping`,
`Sequence`) ja paluuarvoissa konkreettisia (`list`, `dict`): funktio
hyväksyy mahdollisimman paljon ja lupaa mahdollisimman tarkasti
(*Postelin periaate*). `Any` kytkee tarkistuksen pois ja leviää
hiljaa; `object` on turvallinen "mikä tahansa".

## Geneerisyys

Python 3.12 toi tyyppiparametreille oman syntaksin. Funktion tai
luokan nimen perään kirjoitetaan hakasulkeisiin tyyppimuuttujat:

```{.python tiedosto="esimerkit/09-geneerinen.py" osa="funktio"}
```

Mypy päättelee kutsusta `K = int` ja `V = str` ja tietää paluuarvon
olevan `dict[int, list[str]]`. Ennen 3.12:ta sama kirjoitettiin
`T = TypeVar("T")` -määrittelyillä, joita näkee yhä paljon.

Tyyppimuuttujaa voi rajata. `T: Vertailtava` hyväksyy vain tyypit,
jotka toteuttavat protokollan, eli joita voi vertailla:

```{.python tiedosto="esimerkit/09-geneerinen.py" osa="rajattu"}
```

Protokollan `__lt__` ottaa `Any`-tyyppisen argumentin, koska
sisäänrakennetut tyypit määrittelevät vertailun eri argumenttityypeillä;
tarkempi tyyppi ei täsmäisi `int`- ja `str`-tyyppeihin.

Geneerinen luokka ja `type`-lauseella määritelty tyyppialias:

```{.python tiedosto="esimerkit/09-geneerinen.py" osa="luokka"}
```

```{.tuloste tiedosto="esimerkit/09-geneerinen.odotettu"}
```

Tyyppiparametrit ovat olemassa vain tarkistimelle. Ajon aikana
`Jono[Tapahtuma]` on tavallinen `Jono`, eikä alkioiden tyyppiä
tarkisteta. Tämä vastaa Javan tyyppien häivytystä (*type erasure*),
ei C++:n malleja, jotka tuottavat oman koodin jokaiselle tyypille.

## Ulkoinen data

JSON, ympäristömuuttujat ja tietokantarivit tulevat ohjelmaan
tyypittöminä: `json.loads` palauttaa `Any`-tyypin. Rajalle
kirjoitetaan jäsennin, joka tarkistaa datan ja palauttaa tarkasti
tyypitetyn arvon. Sen jälkeen tarkistin luottaa tyyppiin.

```{.python tiedosto="esimerkit/09-json.py" osa="tyypit"}
```

- `TypedDict` kuvaa sanakirjan, jolla on kiinteät avaimet. Se sopii
  JSON-rakenteille, jotka halutaan pitää sanakirjoina.
- `Literal` rajaa arvot tiettyihin vakioihin.
- `NewType` luo erillisen tyypin ilman ajonaikaista hintaa:
  `AsiakasId` on ajon aikana `int`, mutta mypy ei hyväksy tavallista
  `int`-arvoa sen paikalle. Näin asiakastunnus ja tilausnumero eivät
  mene sekaisin.

```{.python tiedosto="esimerkit/09-json.py" osa="jasennys"}
```

```{.tuloste tiedosto="esimerkit/09-json.odotettu"}
```

Käsin kirjoitettu jäsennin on työläs. Tuotantokoodissa samaan
käytetään usein kirjastoa kuten Pydantic tai msgspec, joka johtaa
validoinnin suoraan tyyppimäärittelystä.

## Mypyn käyttö

Mypyn asetukset ovat `pyproject.toml`-tiedostossa:

```{.toml tiedosto="pyproject.toml"}
```

`strict = true` vaatii annotaatiot kaikkiin funktioihin ja kieltää
`Any`-tyypin hiljaisen leviämisen. `python_version` tarkistaa koodin
kohdeversiota vasten: jos koodi käyttää uudemman version
standardikirjastoa, mypy huomaa sen. Vanhaan koodikantaan tarkistus
otetaan käyttöön vähitellen: ensin ilman `strict`-tilaa ja
moduulikohtaisilla poikkeuksilla, sitten tiukemmin.

`# type: ignore[virhekoodi]` vaientaa yksittäisen virheen. Koodi
kirjoitetaan aina hakasulkeisiin, jotta muut virheet samalla rivillä
eivät peity, ja asetus `warn_unused_ignores` (osa `strict`-tilaa)
ilmoittaa tarpeettomiksi käyneistä ohituksista. `reveal_type(x)` näyttää
tarkistuksessa, minkä tyypin mypy päätteli.

## Käytännössä

- **Tyypitä rajapinnat aina, sisäinen koodi tarvittaessa.** Julkiset
  funktiot ja luokat annotoidaan täysin; paikallisten muuttujien
  tyypin mypy päättelee.
- **Jäsennä rajalla** (*parse, don't validate*): ulkoinen data
  muunnetaan tyypitetyksi arvoksi heti saapuessaan, ja sisäinen koodi
  käsittelee vain sitä. `Any` ei saa vuotaa rajan yli.
- **Abstraktit tyypit parametreihin.** `Iterable[str]` hyväksyy
  listan, monikon ja generaattorin; `list[str]` vain listan.
- **`NewType` ja `Literal` sekaantumisalttiille arvoille**: tunnisteet,
  yksiköt, tilat.
- **Tarkistin CI:hin.** Annotaatiot ilman tarkistusta rapistuvat ja
  valehtelevat. `mypy --strict` tai Pyright ajetaan jokaisessa
  muutoksessa (taito *Käännösjärjestelmät, testaus ja CI*).
- **Hinta:** annotaatiot eivät maksa ajon aikana juuri mitään. Ne
  arvioidaan kerran määrittelyn yhteydessä (3.14:stä alkaen laiskasti),
  eivätkä ne hidasta kutsuja.
- **Sudenkuopat:** `Any`, joka tulee `json.loads`-kutsusta tai
  tyypittämättömästä kirjastosta ja leviää hiljaa; `cast`, joka on
  pelkkä väite ilman tarkistusta; ja oletus, että tyyppi tarkistetaan
  ajon aikana.

## Itsearviointi

- Osaat annotoida funktiot ja kokoelmat ja valita abstraktin tai
  konkreettisen tyypin parametriin ja paluuarvoon.
- Osaat käsitellä `T | None`-tyypin ja kaventaa sen.
- Osaat kirjoittaa geneerisen funktion ja luokan Python 3.12:n
  syntaksilla ja rajata tyyppimuuttujan protokollalla.
- Osaat tyypittää ulkoisen datan `TypedDict`-, `Literal`- ja
  `NewType`-tyypeillä ja jäsentää sen rajalla.
- Osaat ottaa mypyn käyttöön `pyproject.toml`-asetuksilla ja käyttää
  `type: ignore` -ohitusta hallitusti.
