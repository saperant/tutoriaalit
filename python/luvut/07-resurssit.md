# Muistinhallinta ja resurssit {.runko-muisti}

Python hallitsee muistin automaattisesti, mutta ei muita resursseja:
tiedostot, verkkoyhteydet, lukot ja tietokantatransaktiot on
vapautettava hallitusti. Tämän luvun ydin on `with`-lause, Pythonin
vastine C++:n RAII:lle ja Javan try-with-resources-lauseelle.

## Viitelaskenta ja roskienkeruu

CPython pitää jokaisessa oliossa *viitelaskuria*. Kun nimi sidotaan
olioon, olio lisätään listaan tai välitetään funktiolle, laskuri
kasvaa; kun viittaus poistuu, se pienenee. Kun laskuri putoaa nollaan,
olio vapautetaan heti. Siksi CPythonissa tiedosto-olio, johon ei enää
viitata, sulkeutuu käytännössä samalla rivillä.

Viitelaskenta ei vapauta *viittaussyklejä*, kuten kahta oliota, jotka
viittaavat toisiinsa. Niitä varten CPythonissa on lisäksi
sukupolvipohjainen *syklinen roskienkeruu*, joka käynnistyy
varausmäärien perusteella. Tästä seuraa:

- Olion elinaika ei ole ohjelmoijan hallinnassa. `del nimi` poistaa
  vain nimen, ei oliota, jos muita viittauksia on.
- `__del__`-metodi (*finalisoija*) ajetaan, kun olio vapautetaan, mutta
  ajankohtaa ei taata: syklissä se voi viivästyä, eikä sitä ajeta
  välttämättä lainkaan ohjelman päättyessä. PyPy ei käytä
  viitelaskentaa lainkaan. Siksi `__del__` ei sovi resurssien
  vapauttamiseen.
- `weakref`-moduulin heikko viittaus ei kasvata laskuria. Sitä
  käytetään välimuisteissa ja tarkkailijoissa, jotka eivät saa pitää
  oliota elossa.
- `sys.getsizeof` kertoo olion oman koon; säiliön alkiot eivät sisälly
  siihen. `tracemalloc` kertoo, mikä rivi varasi muistia.

Muistivuoto Pythonissa on lähes aina viittaus, joka jää eloon:
kasvava moduulitason välimuisti, tapahtumakuuntelijoiden lista tai
`functools.cache` metodilla.

## with ja kontekstinhallinta

`with`-lause takaa, että siivous tehdään, poistuttiinpa lohkosta
normaalisti, `return`-lauseella tai poikkeuksella. Olio, joka toimii
`with`-lauseessa, on *kontekstinhallitsija* (*context manager*): sen
`__enter__` kutsutaan lohkon alussa ja `__exit__` lopussa. `__exit__`
saa poikkeuksen tiedot ja voi niellä poikkeuksen palauttamalla `True`.

Standardikirjastossa kontekstinhallitsijoita ovat muun muassa
tiedostot, lukot, `tempfile`-tiedostot, `socket`-oliot,
`ThreadPoolExecutor` ja `decimal.localcontext`.

Oman kontekstinhallitsijan kirjoittaa helpoimmin generaattorina
`contextlib.contextmanager`-dekoraattorilla. `yield`-lausetta edeltävä
koodi on `__enter__`, `yield` antaa arvon `as`-nimelle, ja sen jälkeinen
koodi on `__exit__`. Esimerkki on tietokantatransaktio, joka vahvistetaan
onnistuessa ja perutaan virheessä:

```{.python tiedosto="esimerkit/07-konteksti.py" osa="transaktio"}
```

```{.python tiedosto="esimerkit/07-konteksti.py" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/07-konteksti.odotettu"}
```

- `try`/`except`/`else`/`finally` jakaa vastuut: `except` peruu ja
  nostaa poikkeuksen uudelleen (`raise` ilman argumenttia), `else`
  vahvistaa vain onnistuessa ja `finally` sulkee kursorin aina.
- Poikkeus jatkaa matkaansa kutsujalle. Kontekstinhallitsija siivoaa
  mutta ei piilota virhettä.
- `contextlib.closing` tekee kontekstinhallitsijan mistä tahansa
  oliosta, jolla on `close`-metodi. sqlite3-yhteyden oma
  `with`-lause hallitsee transaktiota, ei sulje yhteyttä; nimistä ei
  voi päätellä, mitä `with` tekee, joten se tarkistetaan dokumentaatiosta.

## Vaihteleva määrä resursseja

Kun resurssien määrä selviää vasta ajon aikana, sisäkkäiset
`with`-lauseet eivät riitä. `contextlib.ExitStack` kerää
kontekstinhallitsijat ja siivousfunktiot ja purkaa ne käänteisessä
järjestyksessä:

```{.python tiedosto="esimerkit/07-exitstack.py" osa="exitstack"}
```

```{.tuloste tiedosto="esimerkit/07-exitstack.odotettu"}
```

Jos kolmannen tiedoston avaaminen epäonnistuu, kaksi ensimmäistä
suljetaan silti. `ExitStack` on myös tapa rakentaa luokka, joka omistaa
useita resursseja: luokka pitää pinon ja sulkee sen omassa
`__exit__`-metodissaan.

## Tiedostot ja polut

`pathlib.Path` on polkujen olio-rajapinta. `/` yhdistää polkuja,
`read_text`, `write_text`, `exists`, `mkdir`, `glob` ja `rglob` korvaavat
`os.path`-funktiot ja suurimman osan `open`-kutsuista. Koodaus annetaan
aina eksplisiittisesti.

Tiedoston päälle kirjoittaminen ei ole atomista: jos ohjelma kaatuu
kesken, tiedosto jää puolikkaaksi. Asetukset, tilatiedostot ja
välimuistit tallennetaan siksi väliaikaiseen tiedostoon samaan
hakemistoon, joka vaihdetaan paikalleen yhdellä
käyttöjärjestelmäkutsulla:

```{.python tiedosto="esimerkit/07-tiedostot.py" osa="atominen"}
```

```{.python tiedosto="esimerkit/07-tiedostot.py" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/07-tiedostot.odotettu"}
```

`os.replace` on POSIX-järjestelmissä atominen, kun lähde ja kohde ovat
samassa tiedostojärjestelmässä; siksi väliaikainen tiedosto luodaan
kohteen hakemistoon. `fsync` varmistaa, että data on levyllä ennen
vaihtoa. Esimerkki yksinkertaistaa: jos kirjoitus epäonnistuu,
väliaikainen tiedosto jää levylle, ja tuotantoversio poistaisi sen
`except`-haarassa.

## Käytännössä

- **Jokainen resurssi `with`-lauseeseen.** Tiedosto, yhteys, lukko ja
  transaktio vapautetaan `with`-lauseella, ei `close`-kutsulla eikä
  `__del__`-metodilla. Ruff varoittaa `open`-kutsusta ilman
  `with`-lausetta (SIM115).
- **Kontekstinhallitsija rajapinnaksi.** Kun luokka omistaa resurssin,
  se toteuttaa `__enter__`- ja `__exit__`-metodit, ja kertaluonteinen
  "tee tämä ja siivoa" -logiikka kirjoitetaan `@contextmanager`-
  generaattorina. Kutsuja ei voi unohtaa siivousta.
- **`ExitStack` dynaamiselle määrälle** ja luokille, jotka omistavat
  useita resursseja.
- **Atominen tallennus** väliaikaisen tiedoston ja `os.replace`-kutsun
  avulla kaikkeen, minkä puolikas versio olisi vahinko.
- **Hinta:** jokainen olio kantaa viitelaskuria ja tyyppiosoitinta, ja
  laskurin päivitys on mukana lähes jokaisessa operaatiossa. Syklinen
  roskienkeruu pysäyttää ohjelman hetkeksi; suurissa olioverkoissa se
  näkyy viiveenä. `gc.freeze()` ennen prosessien haarautusta ja
  syklien välttäminen vähentävät sitä.
- **Sudenkuopat:** `__del__` resurssien vapauttamiseen, `with`-lauseen
  unohtaminen (toimii CPythonissa, vuotaa PyPyssä), ja välimuisti, joka
  kasvaa rajatta.

## Itsearviointi

- Osaat selittää viitelaskennan ja syklisen roskienkeruun ja sen,
  miksi `__del__` ei sovi resurssien vapauttamiseen.
- Osaat kirjoittaa kontekstinhallitsijan `@contextmanager`-
  generaattorina niin, että siivous tehdään myös poikkeuksessa ja
  poikkeus välittyy kutsujalle.
- Osaat hallita vaihtelevan määrän resursseja `ExitStack`-oliolla.
- Osaat käsitellä tiedostoja `pathlib`-oliolla ja tallentaa tiedoston
  atomisesti.
- Osaat tunnistaa tyypilliset muistivuodot Python-ohjelmassa.
