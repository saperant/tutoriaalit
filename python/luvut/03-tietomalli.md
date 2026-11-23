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

```{.tuloste tiedosto="esimerkit/03-kopiointi.odotettu"}
```

Matala kopio näkee alkuperäisen sisälistaan lisätyn `"Dan"`-alkion,
mutta ei uutta ulkolistan alkiota. Viipale `lista[:]`, `list(lista)`,
`dict(d)` ja `d.copy()` ovat kaikki matalia kopioita. Syvä kopio on
hidas ja harvoin tarpeen: usein parempi ratkaisu on muuttumaton
rakenne, jota ei tarvitse kopioida.

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
- **Sudenkuoppa:** `[[0] * 3] * 3` toistaa viittauksen samaan
  sisälistaan. Taulukko luodaan koostelausekkeella
  `[[0] * 3 for _ in range(3)]`.

## Itsearviointi

- Osaat selittää, miksi sijoitus ja parametrin välitys eivät kopioi,
  ja ennustaa, milloin muutos näkyy toisen nimen kautta.
- Osaat luetella muuttuvat ja muuttumattomat perustyypit ja kertoa,
  miksi vain muuttumaton kelpaa sanakirjan avaimeksi.
- Osaat korjata muuttuvan oletusarvon ansan ja tunnistat sen
  koodikatselmoinnissa.
- Osaat valita matalan ja syvän kopion välillä.
- Osaat muotoilla tulosteen f-merkkijonolla ja käyttää `!r`- ja
  `=`-määreitä virheilmoituksissa.
- Osaat lukea ja validoida syötteen niin, että virheellinen rivi
  raportoidaan eikä kaada ohjelmaa.
