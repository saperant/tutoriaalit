# Ohjausrakenteet ja funktiot {.runko-ohjaus}

Pythonin `if`, `for` ja `while` ovat tuttuja. Tässä luvussa käsitellään
se, mikä niissä on Python-kohtaista: iterointi ilman indeksejä,
rakenteellinen hahmonsovitus, parametrien lajit, sulkeumat ja
dekoraattorit.

## Silmukat ilman indeksejä

Pythonin `for` käy läpi *iteroitavan* olion, ei indeksiväliä. Indeksiä
tarvitaan harvoin:

| Tarve | Idiomi |
|-------|--------|
| alkio ja järjestysnumero | `for i, x in enumerate(alkiot, start=1)` |
| kaksi sarjaa rinnakkain | `for a, b in zip(xs, ys, strict=True)` |
| avain ja arvo | `for avain, arvo in d.items()` |
| käänteinen järjestys | `for x in reversed(alkiot)` |
| lajiteltuna | `for x in sorted(alkiot, key=...)` |
| luku 0..n-1 | `for i in range(n)` |

`zip(..., strict=True)` nostaa poikkeuksen, jos sarjat ovat eri
pituisia; ilman sitä pidempi sarja katkeaa hiljaa. Silmukan `else`-haara
suoritetaan, jos silmukka päättyi ilman `break`-lausetta. Se korvaa
"löytyikö"-lippumuuttujan, mutta on monelle lukijalle vieras, joten
erillinen funktio ja `return` on usein selkeämpi.

Koostelauseke (*comprehension*) rakentaa kokoelman yhdellä
lausekkeella: `[x * x for x in xs if x > 0]`, `{k: v for k, v in pa}`,
`{x.nimi for x in rivit}`. Se on luettavampi ja nopeampi kuin
`append`-silmukka. Kun lauseke kasvaa yli yhden rivin tai siinä on
sivuvaikutuksia, tavallinen silmukka on parempi.

## Rakenteellinen hahmonsovitus

`match` (Python 3.10) vertaa arvoa *hahmoihin* ja purkaa sen samalla.
Se ei ole C:n `switch`: hahmo voi tarkistaa rakenteen, pituuden,
tyypin ja sisällön. Esimerkki jäsentää komentotulkin käskyjä:

```{.python tiedosto="esimerkit/04-komennot.py" osa="match"}
```

```{.tuloste tiedosto="esimerkit/04-komennot.syote"}
```

```{.tuloste tiedosto="esimerkit/04-komennot.odotettu"}
```

- Listahahmo `["lisää", nimi, maara]` täsmää kolmen alkion listaan,
  jonka ensimmäinen alkio on `"lisää"`, ja sitoo kaksi muuta nimiin.
- `if`-vartija tarkentaa hahmoa. Jos vartija ei täyty, kokeillaan
  seuraavaa hahmoa, joten `["lisää", *_]` sieppaa väärän muotoiset
  lisäyskäskyt.
- `*_` täsmää mihin tahansa loppuun ja `_` mihin tahansa arvoon.
- Hahmot kokeillaan järjestyksessä, joten tarkat hahmot ennen yleisiä.
- `shlex.split` pilkkoo rivin kuten komentotulkki, joten lainausmerkeissä
  oleva `"kuusiokolo mutteri"` on yksi sana.

Silmukan `if tulos := suorita(...)` käyttää *sijoituslauseketta*
(*walrus*-operaattori, 3.8). Se sitoo nimen ja palauttaa arvon samassa
lausekkeessa. Sopivia paikkoja ovat silmukan ja ehdon yhdistelmät; muualla
tavallinen sijoitus on selkeämpi.

Hahmo voi olla myös luokka (`case Piste(x=0, y=y)`), sanakirja
(`case {"tyyppi": "virhe", "viesti": str(viesti)}`) tai vakio
(`case Tila.VALMIS`). Luvussa 8 `match` kattaa luettelotyypin kaikki
arvot.

## Parametrien lajit

Python-funktion parametrit voivat olla paikkaan sidottuja, nimettyjä
tai molempia. `/` erottaa vain paikan mukaan annettavat ja `*` vain
nimellä annettavat:

```{.python tiedosto="esimerkit/04-funktiot.py" osa="parametrit"}
```

Vain nimellä annettavat asetukset tekevät kutsuista luettavia
(`ylikirjoita=True` eikä pelkkä `True`) ja sallivat parametrien
järjestyksen muuttamisen rikkomatta kutsujia. Vain paikan mukaan
annettavat parametrit taas jättävät nimen vapaaksi muuttaa.

`*args` kerää ylimääräiset paikka-argumentit monikoksi ja `**kwargs`
nimetyt sanakirjaksi. Kutsussa `*` ja `**` purkavat kokoelman
argumenteiksi:

```{.python tiedosto="esimerkit/04-funktiot.py" osa="vaihteleva"}
```

`functools.partial` sitoo osan argumenteista ja palauttaa uuden
kutsuttavan:

```{.python tiedosto="esimerkit/04-funktiot.py" osa="partial"}
```

```{.tuloste tiedosto="esimerkit/04-funktiot.odotettu"}
```

## Näkyvyys ja sulkeumat

Nimen haku etenee järjestyksessä paikallinen, sulkeva funktio,
moduuli (*globaali*) ja sisäänrakennettu (*LEGB*). Sijoitus tekee
nimestä paikallisen koko funktiossa, joten ulomman nimen muuttaminen
vaatii esittelyn `nonlocal` (sulkeva funktio) tai `global` (moduuli).
Molemmat ovat merkki tilasta, joka kannattaisi usein siirtää olioon.

Sisäfunktio, joka viittaa ulomman funktion nimiin, on *sulkeuma*. Se
sitoo nimen, ei arvoa:
`[lambda: i for i in range(3)]` tuottaa kolme funktiota, jotka kaikki
palauttavat 2. Arvo sidotaan oletusarvolla (`lambda i=i: i`) tai
`functools.partial`-kutsulla.

`lambda` on yhden lausekkeen nimetön funktio. Se sopii
`key=`-argumentiksi; nimetty funktio on parempi kaikkeen muuhun, koska
sillä on nimi pinojäljessä ja dokumentaatio.

## Dekoraattorit

Funktio on olio, joten sen voi välittää, palauttaa ja korvata.
*Dekoraattori* on funktio, joka ottaa funktion ja palauttaa uuden.
Merkintä `@koriste` funktion yläpuolella tarkoittaa samaa kuin
`f = koriste(f)`. Dekoraattorilla lisätään funktion ympärille toimintaa,
joka ei kuulu sen omaan logiikkaan: uudelleenyritys, ajanotto,
oikeustarkistus, välimuisti.

Seuraava dekoraattori yrittää kutsua uudelleen tilapäisen virheen
jälkeen. Parametrinen dekoraattori on kolmen funktion sisäkkäinen
rakenne: ulompi ottaa asetukset, keskimmäinen funktion ja sisin
korvaa kutsun:

```{.python tiedosto="esimerkit/04-dekoraattori.py" osa="yrita"}
```

```{.python tiedosto="esimerkit/04-dekoraattori.py" osa="kaytto"}
```

- `functools.wraps` kopioi alkuperäisen funktion nimen ja
  dokumentaation kääreeseen. Ilman sitä pinojäljissä ja dokumentaatiossa
  näkyisi `kaare`.
- Tyyppiparametrit `[**P, R]` (Python 3.12) kertovat mypylle, että
  kääre ottaa samat parametrit (`P`) ja palauttaa saman tyypin (`R`)
  kuin alkuperäinen. Tyyppiparametreja käsitellään luvussa 9.
- Esimerkki sieppaa vain `TilapainenVirhe`-poikkeuksen. Ohjelmointivirhettä
  ei kannata yrittää uudelleen. Tuotantoversio odottaisi kasvavan ajan
  yritysten välillä (*exponential backoff*).

Standardikirjaston `functools.cache` muistaa funktion tulokset
argumenttien perusteella (*memoisaatio*). Se muuttaa eksponentiaalisen
rekursion polynomiseksi:

```{.python tiedosto="esimerkit/04-dekoraattori.py" osa="cache"}
```

```{.tuloste tiedosto="esimerkit/04-dekoraattori.odotettu"}
```

`cache` kasvaa rajatta, joten pitkäikäisessä palvelussa käytetään
`lru_cache(maxsize=...)`. Argumenttien on oltava hajautettavia, ja
metodiin sovellettuna välimuisti pitää `self`-olion elossa.

## Käytännössä

- **Iteroi suoraan, älä indeksoi.** `enumerate`, `zip` ja `items`
  poistavat indeksivirheet ja ovat nopeampia kuin `range(len(...))`.
- **Vartijalauseet** (*guard clause*): virhetapaukset käsitellään ensin
  ja palataan aikaisin, jolloin pääpolku ei sisenny syvälle.
- **Avainsanaparametrit asetuksille.** Totuusarvo- ja lukuasetukset
  annetaan `*`-merkin jälkeen, jotta kutsu dokumentoi itsensä.
- **`match` rakenteelle, `if` ehdoille.** Hahmonsovitus on omimmillaan,
  kun syötteellä on muoto (komento, JSON-viesti, jäsennyspuu). Yksi tai
  kaksi vertailua kirjoitetaan `if`-lauseena.
- **Dekoraattori poikkileikkaaville asioille.** Uudelleenyritys,
  lokitus ja välimuisti dekoraattoreina pitävät funktion logiikan
  puhtaana. Aina `functools.wraps`.
- **Hinta:** funktiokutsu on CPythonissa kymmeniä nanosekunteja eli
  monta kertaa kalliimpi kuin C:ssä, ja dekoraattori lisää kutsun
  jokaiseen kutsuun. Kuumassa silmukassa pieni apufunktio voi näkyä
  profiilissa, mutta selkeys on silti oletus (luku 13).
- **Sudenkuopat:** silmukkamuuttujan myöhäinen sidonta sulkeumassa,
  `global` piilotettuna tilana ja `lambda` nimettynä funktiona
  (`f = lambda ...`, ruff varoittaa).

## Itsearviointi

- Osaat kirjoittaa silmukat `enumerate`-, `zip`- ja `items`-idiomeilla
  ja tiedät, mitä `strict=True` suojaa.
- Osaat jäsentää rakenteellista syötettä `match`-lauseella
  vartijoineen ja `*_`-hahmoineen.
- Osaat suunnitella funktion parametrit `/`- ja `*`-erottimilla ja
  purkaa argumentit `*`- ja `**`-operaattoreilla.
- Osaat selittää sulkeuman myöhäisen sidonnan ja korjata sen.
- Osaat kirjoittaa tyypitetyn, parametrisen dekoraattorin
  `functools.wraps`-kutsun kanssa ja käyttää `functools.cache`-
  välimuistia.
