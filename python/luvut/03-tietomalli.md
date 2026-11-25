# Tietomalli, tyypit ja muotoilu {.runko-tyypit}

Pythonin semantiikka on yksinkertainen mutta poikkeaa staattisista
kielistä: kaikki arvot ovat olioita, joilla on identiteetti, tyyppi ja
arvo, ja muuttujat ovat nimiä, jotka viittaavat olioihin. Lähes kaikki
"oudot" Python-bugit selittyvät tällä mallilla.

## Nimet ja oliot

Sijoitus sitoo nimen olioon. Se ei kopioi oliota eikä varaa nimelle
muistia:

```{.python tiedosto="esimerkit/03-nimet.py" osa="viittaus"}
```

`sama` ja `ostokset` ovat kaksi nimeä samalle listalle. `is` vertaa
identiteettiä ja `id()` palauttaa olion identiteetin (CPythonissa
muistiosoitteen). `list(ostokset)` luo uuden listan, joka viittaa samoihin
alkioihin. Sama pätee funktiokutsuun: parametri on uusi nimi kutsujan
oliolle. Tätä kutsutaan joskus *viittauksen välitykseksi arvona* (*call
by sharing*). Funktio voi muuttaa saamaansa listaa, mutta nimen
uudelleensitominen funktiossa ei näy kutsujalle.

```{.dot otsikko="Esimerkin tilanne lopussa. `sama` ja `ostokset` ovat saman listan kaksi nimeä. `kopio` on eri lista, mutta sen alkiot ovat samat merkkijono-oliot."}
digraph {
  rankdir=LR; nodesep=0.2; ranksep=0.55;
  node [shape=plain, style=""];
  kopio; sama; ostokset;
  node [shape=record, style=filled];
  l2 [label="<a>0|<b>1|<c>2|<d>3"];
  l1 [label="<a>0|<b>1|<c>2"];
  node [shape=box, style="rounded,filled"];
  kahvi [label="\"kahvi\""]; juusto [label="\"juusto\""];
  leipa [label="\"leipä\""]; maito [label="\"maito\""];
  kopio -> l2; sama -> l1; ostokset -> l1;
  l1:a -> maito; l1:b -> leipa; l1:c -> juusto;
  l2:a -> maito; l2:b -> leipa; l2:c -> juusto; l2:d -> kahvi;
}
```

## Muuttuvat ja muuttumattomat tyypit

| Muuttumattomat | Muuttuvat |
|----------------|-----------|
| `int`, `float`, `complex`, `bool`, `Decimal` | `list` |
| `str`, `bytes` | `bytearray` |
| `tuple`, `frozenset` | `set`, `dict` |
| `None`, funktiot, `@dataclass(frozen=True)` | tavalliset luokat |

Muuttumatonta oliota ei voi muuttaa. Operaatio, joka näyttää
muuttavan sitä, luo uuden olion ja sitoo nimen uudelleen:

```{.python tiedosto="esimerkit/03-nimet.py" osa="muuttumaton"}
```

Vain muuttumaton olio voi olla `dict`-avain tai `set`-alkio, koska
hajautusarvon on pysyttävä samana. Monikko (`tuple`) on muuttumaton
vain, jos sen alkiot ovat: `([], 1)` ei kelpaa avaimeksi.

Arvo ja identiteetti ovat eri asioita:

```{.python tiedosto="esimerkit/03-nimet.py" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/03-nimet.odotettu"}
```

`is`-operaattoria käytetään vain ainokaisille kuten `None`. CPython
jakaa pienet kokonaisluvut ja osan merkkijonoista välimuistista, joten
`a is b` voi olla tosi kahdelle luvulle sattumalta. Se on
toteutuksen yksityiskohta, eikä siihen saa luottaa.

## Muuttuva oletusarvo

Oletusarvo lasketaan kerran, kun `def`-lause suoritetaan, ja sama olio
on käytössä jokaisessa kutsussa:

```{.python tiedosto="esimerkit/03-oletusarvo.py" osa="ansa"}
```

Ruff tunnistaa virheen (sääntö B006), ja esimerkki vaientaa
varoituksen `noqa`-kommentilla vain havainnollistaakseen sitä. Oikea
tapa on vartija-arvo `None`:

```{.python tiedosto="esimerkit/03-oletusarvo.py" osa="oikein"}
```

```{.tuloste tiedosto="esimerkit/03-oletusarvo.odotettu"}
```

Sama ilmiö koskee kaikkia oletusarvoja: `def f(aika=datetime.now())`
jäädyttää ajan moduulin latausajankohtaan.

## Kopiointi

`copy.copy` tekee *matalan kopion*: uusi ulkosäiliö, samat alkiot.
`copy.deepcopy` kopioi rekursiivisesti:

```{.python tiedosto="esimerkit/03-kopiointi.py" osa="kopio"}
```

Jaettu sisälista syntyy huomaamatta myös silloin, kun sisäkkäinen
lista luodaan kertolaskulla:

```{.python tiedosto="esimerkit/03-kopiointi.py" osa="ruudukko"}
```

```{.tuloste tiedosto="esimerkit/03-kopiointi.odotettu"}
```

Matala kopio näkee alkuperäisen sisälistaan lisätyn `"Dan"`-alkion,
mutta ei uutta ulkolistan alkiota. Viipale `lista[:]`, `list(lista)`,
`dict(d)` ja `d.copy()` ovat kaikki matalia kopioita. Syvä kopio on
hidas ja harvoin tarpeen: usein parempi ratkaisu on muuttumaton
rakenne, jota ei tarvitse kopioida.

```{.dot otsikko="Matala kopio jakaa sisälistat alkuperäisen kanssa, syvä kopio ei. Uusi alkio `['Eli']` lisättiin vain listaan `vuorot`."}
digraph {
  rankdir=LR; nodesep=0.22; ranksep=0.6;
  node [shape=plain, style=""];
  syva; matala; vuorot;
  node [shape=record, style=filled];
  us [label="<a>0|<b>1"];
  um [label="<a>0|<b>1"];
  uv [label="<a>0|<b>1|<c>2"];
  sa [label="{\"Ada\"|\"Bob\"}"];
  sc [label="\"Cia\""];
  a [label="{\"Ada\"|\"Bob\"|\"Dan\"}"];
  c [label="\"Cia\""];
  e [label="\"Eli\""];
  syva -> us; matala -> um; vuorot -> uv;
  us:a -> sa; us:b -> sc;
  um:a -> a; um:b -> c;
  uv:a -> a; uv:b -> c; uv:c -> e;
}
```

Tulosteen kolmannella rivillä yksi sijoitus muutti jokaista riviä:
`[[0] * 3] * 3` toistaa kolme kertaa viittauksen samaan sisälistaan.
Koostelauseke suorittaa lausekkeen `[0] * 3` jokaisella kierroksella
ja luo siksi kolme eri listaa.

```{.dot otsikko="`[[0] * 3] * 3` luo yhden sisälistan ja kolme viittausta siihen; koostelauseke luo kolme sisälistaa."}
digraph {
  rankdir=LR; nodesep=0.2; ranksep=0.55;
  node [shape=plain, style=""];
  erilliset; jaettu;
  node [shape=record, style=filled];
  ue [label="<a>0|<b>1|<c>2"];
  uj [label="<a>0|<b>1|<c>2"];
  e3 [label="{0|0|0}"]; e2 [label="{0|0|0}"]; e1 [label="{1|0|0}"];
  j [label="{1|0|0}"];
  erilliset -> ue; jaettu -> uj;
  ue:a -> e1; ue:b -> e2; ue:c -> e3;
  uj:a -> j; uj:b -> j; uj:c -> j;
}
```

## Luvut

- `int` on mielivaltaisen tarkka. Ylivuotoa ei ole, mutta suuret
  luvut ovat hitaita.
- `float` on IEEE 754 -kaksoistarkkuuden liukuluku. Vertailuun käytetään
  `math.isclose`.
- `Decimal` on desimaaliluku, jonka tarkkuus ja pyöristys määritellään.
  Rahalle aina `Decimal` (tai kokonaisluvut senteissä). Luodaan
  merkkijonosta: `Decimal("0.1")`, ei `Decimal(0.1)`.
- `Fraction` on tarkka murtoluku.
- `/` palauttaa aina `float`-arvon, `//` on lattiajako ja `%` jakojäännös
  samalla merkillä kuin jakaja. `divmod(a, b)` palauttaa molemmat.
- `bool` on `int`-tyypin alityyppi: `True + True == 2`.

Tyyppimuunnokset ovat eksplisiittisiä: `int("42")`, `float("2.5")`,
`str(42)`. Virheellinen syöte nostaa `ValueError`-poikkeuksen.

## Päivämäärät ja ajat

`datetime`-olio on joko *aikavyöhykkeellinen* (*aware*, `tzinfo`
asetettu) tai *naiivi* (ei vyöhykettä). Naiivi aika ei kerro, mistä
hetkestä on kyse, ja se on tuotantokoodin yleinen virhelähde:

```{.python tiedosto="esimerkit/03-aika.py" osa="aika"}
```

```{.tuloste tiedosto="esimerkit/03-aika.odotettu"}
```

- Ajanhetket tallennetaan ja lasketaan UTC-aikana ja muunnetaan
  paikalliseksi vasta näytettäessä. Nykyhetki on
  `datetime.now(tz=UTC)`; pelkkä `datetime.now()` palauttaa naiivin
  paikallisen ajan.
- Naiivia ja aikavyöhykkeellistä aikaa ei voi verrata eikä vähentää
  toisistaan: Python nostaa `TypeError`-poikkeuksen sen sijaan, että
  arvaisi.
- Esimerkin `timezone` on kiinteä siirtymä. Oikeat aikavyöhykkeet
  kesäaikasääntöineen antaa `zoneinfo.ZoneInfo("Europe/Helsinki")`,
  joka lukee käyttöjärjestelmän aikavyöhyketietokantaa (Windowsissa
  asennetaan paketti `tzdata`).
- Kestot mitataan kellolla `time.monotonic()` tai tarkemmalla
  `time.perf_counter()`. Seinäkello voi hypätä taaksepäin, kun
  järjestelmän aikaa korjataan.

## Merkkijonot ja muotoilu

`str` on muuttumaton Unicode-merkkijono, `bytes` tavujono. Raja niiden
välillä ylitetään eksplisiittisesti: `teksti.encode("utf-8")` ja
`data.decode("utf-8")`. Tiedostot avataan aina koodaus mainiten
(`open(p, encoding="utf-8")`), koska oletus riippuu käyttöjärjestelmästä.

Tulostus muotoillaan *f-merkkijonoilla*. Kaksoispisteen jälkeen tulee
muotoilumääre, jonka tulkitsee olion `__format__`-metodi:

```{.python tiedosto="esimerkit/03-muotoilu.py" osa="muotoilu"}
```

```{.tuloste tiedosto="esimerkit/03-muotoilu.odotettu"}
```

| Määre | Merkitys |
|-------|----------|
| `<8` `>8` `^8` | tasaus vasemmalle, oikealle, keskelle leveyteen 8 |
| `.2f` `,.2f` | kaksi desimaalia; tuhaterotin |
| `.1%` `.3e` | prosentti; tieteellinen esitys |
| `08b` `#x` `03d` | binääri nollilla täytettynä; heksa etuliitteellä; nollatäyttö |
| `!r` | `repr()`: ohjelmoijalle tarkoitettu esitys |
| `=` | lauseke ja arvo, virheenjäljitykseen |
| `%d.%m.%Y` | päivämäärän muoto (`strftime`) |

`str(olio)` on käyttäjälle tarkoitettu esitys ja `repr(olio)`
ohjelmoijalle. Hyvä `repr` näyttää, miten olio luodaan uudelleen,
kuten `Decimal('1234.5')`. Lokiviesteissä ja virheissä käytetään
`!r`-muotoa, jolloin tyhjä merkkijono ja välilyönnit näkyvät.

## Syötteen lukeminen

`input()` lukee yhden rivin, ja `sys.stdin` on tiedosto-olio, jota voi
iteroida rivi kerrallaan. Syöte on aina epäluotettavaa: se jäsennetään,
validoidaan ja virheellinen rivi raportoidaan rivinumeron kanssa.

```{.python tiedosto="esimerkit/03-syote.py" osa="syote"}
```

```{.tuloste tiedosto="esimerkit/03-syote.syote"}
```

```{.tuloste tiedosto="esimerkit/03-syote.odotettu"}
```

Virheellinen rivi tulostuu virhevirtaan muodossa
`rivi 5: ei luku: 'kymmenen'`, joten se ei sekoitu varsinaiseen
tulosteeseen. Funktio palauttaa sekä arvot että virheet eikä tulosta
itse mitään: kutsuja päättää, mitä virheille tehdään. Tyhjä syöte
kaataisi ohjelman nollalla jakoon; tuotantokoodi tarkistaisi sen.

## Käytännössä

- **Sijoitus on nimeäminen, ei kopiointi.** Kun funktio saa listan
  tai sanakirjan, se joko jättää sen ennalleen tai sen nimi kertoo
  muutoksesta (`lajittele_paikallaan`). Standardikirjaston tapa on
  sama: `lista.sort()` muuttaa listaa ja palauttaa `None`-arvon,
  `sorted(lista)` palauttaa uuden listan.
- **Muuttumattomuus oletuksena.** Monikko, `frozenset` ja jäädytetty
  dataluokka ovat turvallisia jakaa, kelpaavat avaimiksi eivätkä
  tarvitse kopioita. Muuttuva rakenne valitaan, kun sitä todella
  muutetaan.
- **Vartija-arvo `None`** (*sentinel*) korvaa muuttuvan oletusarvon.
  Jos `None` on kelvollinen arvo, käytetään omaa vartijaa
  `_PUUTTUU = object()`.
- **`is None`, ei `== None`.** `==` kutsuu `__eq__`-metodia, jonka luokka
  voi määritellä miten haluaa. `is` on nopea ja yksiselitteinen.
- **Raja ulkomaailmaan.** Tavut muunnetaan merkkijonoiksi heti
  syötteessä ja takaisin vasta tulosteessa (*Unicode sandwich*).
  Sama koskee lukuja: syöte jäsennetään ja validoidaan kerran rajalla,
  ja sisällä liikkuvat vain oikean tyyppiset arvot.
- **Hinta:** jokainen kokonaisluku on kasassa oleva olio (28 tavua),
  ja aritmetiikka tarkistaa tyypit ajon aikana. Lukuja on halvempi
  käsitellä joukkona kuin yksitellen: `sum()`, `array`-moduuli tai NumPy.
- **Sudenkuopat:** `[[0] * 3] * 3` toistaa viittauksen samaan
  sisälistaan; taulukko luodaan koostelausekkeella
  `[[0] * 3 for _ in range(3)]`. Naiivi `datetime.now()` tallennettuna
  tietokantaan tai lokiin on paikallista aikaa ilman tietoa
  vyöhykkeestä; käytä `datetime.now(tz=UTC)`.

## Itsearviointi

- Osaat selittää, miksi sijoitus ja parametrin välitys eivät kopioi,
  ja ennustaa, milloin muutos näkyy toisen nimen kautta.
- Osaat luetella muuttuvat ja muuttumattomat perustyypit ja kertoa,
  miksi vain muuttumaton kelpaa sanakirjan avaimeksi.
- Osaat korjata muuttuvan oletusarvon ansan ja tunnistat sen
  koodikatselmoinnissa.
- Osaat valita matalan ja syvän kopion välillä ja piirtää, mitkä
  oliot kopio jakaa alkuperäisen kanssa.
- Osaat erottaa naiivin ja aikavyöhykkeellisen ajan, käsitellä
  ajanhetket UTC-aikana ja mitata keston monotonisella kellolla.
- Osaat muotoilla tulosteen f-merkkijonolla ja käyttää `!r`- ja
  `=`-määreitä virheilmoituksissa.
- Osaat lukea ja validoida syötteen niin, että virheellinen rivi
  raportoidaan eikä kaada ohjelmaa.
