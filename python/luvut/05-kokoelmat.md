# Kokoelmat ja merkkijonot {.runko-kokoelmat}

Pythonin sisäänrakennetut kokoelmat on toteutettu C:llä ja optimoitu
huolellisesti. Oikean kokoelman valinta on Python-ohjelman tärkein
yksittäinen suorituskykypäätös, koska kokoelman operaatiot tehdään
C-nopeudella ja oma silmukka Python-nopeudella. Algoritmien ja
tietorakenteiden teoria on taidoissa *Algoritmit* ja *Tietorakenteet*;
tässä luvussa keskitytään Pythonin toteutuksiin ja niiden hintoihin.

## Kokoelmat ja niiden hinnat

| Kokoelma | Toteutus | Halpaa | Kallista |
|----------|----------|--------|----------|
| `list` | dynaaminen taulukko | indeksointi, `append`, `pop()` | `insert(0, x)`, `pop(0)`, `x in` |
| `tuple` | muuttumaton taulukko | kuten `list`, vähemmän muistia | muutos (uusi monikko) |
| `dict` | hajautustaulu | haku, lisäys, poisto | ei mitään tavallisessa käytössä |
| `set` | hajautustaulu | `x in`, joukko-operaatiot | järjestys puuttuu |
| `deque` | lohkoista koottu kaksisuuntainen lista | `append`/`pop` molemmista päistä | indeksointi keskeltä |
| `heapq` (lista) | binäärikeko | pienin alkio, lisäys O(log n) | haku |
| `bisect` (lista) | lajiteltu taulukko | binäärihaku | lisäys O(n) |

`dict` säilyttää lisäysjärjestyksen (taattu 3.7:stä alkaen), joten
sitä voi käyttää myös järjestettynä kuvauksena. `set` ei säilytä
järjestystä, ja merkkijonojen hajautus satunnaistetaan joka
käynnistyksellä: joukon tulostusjärjestys vaihtelee ajosta toiseen.
Siksi tulosteet lajitellaan.

## Sanakirjat

```{.python tiedosto="esimerkit/05-kokoelmat.py" osa="dict"}
```

- `get(avain, oletus)` palauttaa oletuksen puuttuvalle avaimelle;
  `d[avain]` nostaa `KeyError`-poikkeuksen.
- `setdefault` lisää avaimen vain, jos sitä ei ole.
- `|` ja `|=` yhdistävät sanakirjat (3.9). Oikeanpuoleinen voittaa.
- `operator.itemgetter(1)` on nopeampi ja luettavampi
  lajitteluavain kuin `lambda p: p[1]`.

Ryhmittely on niin yleinen tehtävä, että standardikirjastossa on sille
omat tyypit: `defaultdict` luo puuttuvan arvon tehdasfunktiolla ja
`Counter` laskee esiintymiä.

```{.python tiedosto="esimerkit/05-kokoelmat.py" osa="ryhmittely"}
```

## Joukot, jonot ja lajittelu

Joukko-operaatiot korvaavat sisäkkäiset silmukat. Oikeustarkistus on
erotus: mitä vaaditaan, mutta ei ole myönnetty.

```{.python tiedosto="esimerkit/05-kokoelmat.py" osa="joukot"}
```

`deque` on oikea rakenne jonolle. `maxlen` tekee siitä
rengaspuskurin, joka pudottaa vanhimman alkion:

```{.python tiedosto="esimerkit/05-kokoelmat.py" osa="deque"}
```

Pythonin lajittelu (*Timsort*, 3.11:stä alkaen *Powersort*) on
*vakaa*: yhtä suurten alkioiden järjestys säilyy. Siksi monitasoinen
lajittelu voidaan tehdä ketjuna vähiten merkitsevästä avaimesta alkaen,
kun avaimet lajitellaan eri suuntiin:

```{.python tiedosto="esimerkit/05-kokoelmat.py" osa="lajittelu"}
```

```{.tuloste tiedosto="esimerkit/05-kokoelmat.odotettu"}
```

Kun kaikki avaimet ovat samaan suuntaan, yksi lajittelu monikkoavaimella
riittää: `key=lambda h: (h.ika, h.nimi)`. Numeerisen avaimen voi
kääntää miinusmerkillä. `min`, `max`, `sorted`, `heapq.nlargest` ja
`bisect` ottavat kaikki `key`-argumentin.

## Merkkijonot

Merkkijono on muuttumaton, joten jokainen muokkaus luo uuden olion.
Tärkeimmät metodit:

| Tehtävä | Metodi |
|---------|--------|
| pilkkominen | `split()` (välilyönnit), `split(",")`, `partition(":")`, `splitlines()` |
| yhdistäminen | `", ".join(osat)` |
| siistiminen | `strip()`, `removeprefix("x")`, `removesuffix(".txt")` |
| haku | `"x" in s`, `startswith`, `endswith`, `find` (-1), `index` (poikkeus) |
| muunnos | `lower()`, `casefold()` (vertailuun), `replace(a, b)` |
| tarkistus | `isdigit()`, `isalpha()`, `isspace()` |

`partition` on `split`-kutsua turvallisempi, kun erotin esiintyy
korkeintaan kerran: se palauttaa aina kolme osaa. `removesuffix`
poistaa tarkan päätteen, kun taas `rstrip(".txt")` poistaa
*merkkijoukon* merkkejä lopusta, mikä on yleinen virhe.

Merkkijono rakennetaan osista `join`-metodilla. Silmukassa toistettu
`s += osa` on periaatteessa neliöllinen, koska jokainen lisäys kopioi
koko merkkijonon. CPython optimoi tapauksen usein paikalliselle
muuttujalle, mutta optimointiin ei voi luottaa (PyPy ei tee sitä, eikä
se toimi attribuutille). `join` on aina lineaarinen.

## Säännölliset lausekkeet

`re`-moduuli toteuttaa säännölliset lausekkeet. Lauseke käännetään
kerran `re.compile`-kutsulla ja tallennetaan moduulitason vakioksi.
Esimerkki laskee tekstin yleisimmät sanat:

```{.python tiedosto="esimerkit/05-sanat.py" osa="sanat"}
```

```{.tuloste tiedosto="esimerkit/05-sanat.syote"}
```

```{.tuloste tiedosto="esimerkit/05-sanat.odotettu"}
```

`Counter.most_common` palauttaa yhtä yleiset sanat siinä
järjestyksessä, jossa ne ensimmäisen kerran kohdattiin, joten tulos on
toistettava. `total()` (3.10) laskee kaikkien määrien summan.
Säännöllinen lauseke kirjoitetaan raakamerkkijonona `r"..."`, jolloin
kenoviivoja ei tarvitse kahdentaa. Monimutkaisen lausekkeen
voi kirjoittaa usealle riville kommentein lipulla `re.VERBOSE`.

## Muita standardikirjaston kokoelmia

- `collections.OrderedDict`: `move_to_end` ja `popitem(last=False)`
  LRU-välimuistiin.
- `collections.ChainMap`: kerrostetut asetukset (komentorivi, ympäristö,
  oletukset) ilman yhdistämistä.
- `array.array`: tiivis numeerinen taulukko (esim. 8 tavua per
  `float`, listassa noin 32 tavua per alkio).
- `heapq`: prioriteettijono listan päällä; `heapq.merge` yhdistää
  lajiteltuja sarjoja laiskasti.
- `types.MappingProxyType`: vain luku -näkymä sanakirjaan.

Raskaaseen numeeriseen laskentaan käytetään NumPyä. Se tallentaa luvut
tiiviiseen C-taulukkoon ja tekee operaatiot koko taulukolle kerralla
(*vektorointi*): `a * 2 + b` ilman Python-silmukkaa on tyypillisesti
10–100 kertaa nopeampi kuin listasilmukka. NumPy on ulkoinen kirjasto,
eikä sitä käsitellä tässä tarkemmin.

## Käytännössä

- **Valitse kokoelma operaatioiden mukaan.** Jäsenyystesti toistuvasti
  → `set`. Jono → `deque`. Haku avaimella → `dict`. Muuttumaton tietue
  → `tuple` tai jäädytetty dataluokka. Väärä valinta tekee lineaarisesta
  algoritmista neliöllisen ilman, että koodi näyttää kalliilta.
- **Ryhmittele `defaultdict`- ja `Counter`-tyypeillä.** Ne korvaavat
  "jos avain puuttuu, luo" -haarat ja ovat nopeampia.
- **Rakenna merkkijono `join`-kutsulla** ja tulosta muotoilemalla, ei
  `+`-ketjuilla.
- **Lajittele avaimella, älä vertailufunktiolla.** `key` lasketaan
  kerran alkiota kohden. `functools.cmp_to_key` on olemassa vain
  vanhan koodin siirtämiseen.
- **Deterministinen tuloste:** älä tulosta joukkoja tai luota
  `set`-iteroinnin järjestykseen testeissä, lokeissa tai
  tiedostomuodoissa. Lajittele ensin.
- **Hinta:** listan alkio on 8 tavun viittaus erilliseen olioon, joten
  miljoonan liukuluvun lista vie noin 32 Mt; `array` tai NumPy noin 8 Mt.
  Hajautustaulut varaavat tilaa väljästi, jotta haku pysyy nopeana.
- **Sudenkuoppa:** kokoelman muuttaminen sitä iteroitaessa. Sanakirjan
  koon muutos iteroinnin aikana nostaa `RuntimeError`-poikkeuksen;
  listan kanssa alkioita ohitetaan hiljaa. Iteroi kopiota
  (`list(d)`) tai rakenna uusi kokoelma.

## Itsearviointi

- Osaat kertoa `list`-, `dict`-, `set`- ja `deque`-operaatioiden hinnat
  ja valita kokoelman niiden perusteella.
- Osaat ryhmitellä ja laskea `defaultdict`- ja `Counter`-tyypeillä.
- Osaat lajitella usean avaimen mukaan ja selittää, miksi vakaa
  lajittelu mahdollistaa ketjutetun lajittelun.
- Osaat käsitellä merkkijonoja oikeilla metodeilla ja tiedät, miksi
  `rstrip(".txt")` ja silmukassa toistettu `+=` ovat virheitä.
- Osaat käyttää käännettyä säännöllistä lauseketta tekstin
  jäsentämiseen.
