# Modulit ja standardikirjasto

Kun ohjelma kasvaa yli muutaman sadan rivin, se jaetaan useaan
tiedostoon. Jokainen `.py`-tiedosto on *moduli*, jonka funktioita ja
luokkia muut modulit voivat käyttää. Moduleihin jakaminen pitää
tiedostot ymmärrettävän kokoisina ja tekee koodista uudelleenkäytettävää.

## Oma moduli

Luvuissa *Funktiot* ja *Virheet ja poikkeukset* kirjoitettiin rahan
jäsennys ja muotoilu. Kun ne siirretään omaan moduliinsa, niitä voi
käyttää mistä tahansa ohjelmasta kopioimatta:

```{.python tiedosto="esimerkit/09-kuitti/rahat.py"}
```

```{.python tiedosto="esimerkit/09-kuitti/main.py"}
```

Syöte ja tuloste:

```{.tuloste tiedosto="esimerkit/09-kuitti.syote"}
```

```{.tuloste tiedosto="esimerkit/09-kuitti.odotettu"}
```

- `from rahat import euroina, jasenna_summa` tuo modulista `rahat`
  (tiedosto `rahat.py` samassa hakemistossa) kaksi funktiota. Vaihtoehto
  `import rahat` tuo modulin, jolloin funktiot kutsutaan muodossa
  `rahat.euroina(...)`.
- Kun moduli tuodaan, sen koodi suoritetaan kerran. Siksi modulissa on
  vain määrittelyjä.
- Ehto `if __name__ == "__main__":` on tosi vain, kun tiedosto ajetaan
  ohjelmana (`python3 rahat.py`). Tuotaessa ehdon lohkoa ei suoriteta.
  Sama rakenne pääohjelmassa kutsuu `main`-funktiota, jonka paluuarvo
  välitetään käyttöjärjestelmälle `sys.exit`-kutsulla.
- Pääohjelma on funktio `main` eikä modulin päätason koodia. Näin
  pääohjelman nimet ovat paikallisia, ja muutkin modulit (esimerkiksi
  testit) voivat tuoda pääohjelman tiedoston ajamatta sitä.

Pääohjelma `main.py` olettaa, että jokaisella rivillä on kolme kenttää.
Väärämuotoinen rivi kaataa ohjelman; luvun *Ohjelman suunnittelu*
budjettiohjelma käsittelee tämän.

## Standardikirjasto

Pythonin mukana tulee laaja *standardikirjasto*, jonka modulit ovat
käytettävissä ilman asennusta. Ennen kuin kirjoitat jotain itse,
tarkista, löytyykö se valmiina:

| Moduli | Käyttö |
|--------|--------|
| `math` | matemaattiset funktiot: `sqrt`, `ceil`, `floor`, `pi` |
| `statistics` | keskiarvo, mediaani, keskihajonta |
| `random` | satunnaisluvut (ei salaukseen: `secrets`) |
| `datetime` | päivämäärät, kellonajat ja aikavälit |
| `pathlib` | tiedostopolut ja tiedostojärjestelmä |
| `csv`, `json` | yleiset tiedostomuodot |
| `sys` | komentoriviargumentit, syöte, ohjelman lopetus |
| `collections` | lisäkokoelmat, kuten `Counter` ja `deque` |
| `re` | säännölliset lausekkeet |

Projektin aikataulu lasketaan `datetime`-modulilla:

```{.python tiedosto="esimerkit/09-aikataulu.py"}
```

```{.tuloste tiedosto="esimerkit/09-aikataulu.odotettu"}
```

`date` on päivämäärä ja `timedelta` aikaväli. Päivämääriä voi
vertailla ja vähentää toisistaan, ja `weekday()` kertoo viikonpäivän.
Esimerkki ei käytä tämänhetkistä päivää (`date.today()`), jotta sen
tuloste on aina sama ja sen voi testata. Ohjelmassa, jonka tulos
riippuu kellosta, aika kannattaa antaa funktiolle parametrina samasta
syystä.

## Ulkoiset kirjastot

Standardikirjaston ulkopuolisia kirjastoja on Python Package Indexissä
(PyPI) satoja tuhansia. Ne asennetaan `pip`-työkalulla projektikohtaiseen
*virtuaaliympäristöön*, jotta eri projektien kirjastoversiot eivät
sekoitu:

```text
$ python3 -m venv .venv
$ source .venv/bin/activate
(.venv) $ pip install requests
```

Projektin riippuvuudet ja työkalujen asetukset kirjataan tiedostoon
`pyproject.toml`; tämän tutoriaalin esimerkkien asetukset ovat
hakemiston juuressa. Taito *Python työkaluohjelmointiin* käsittelee
riippuvuuksien hallinnan ja paketoinnin.

## Käytännössä

- **Yksi moduli, yksi aihe.** `rahat.py` käsittelee rahasummia,
  `raportti.py` raportteja. Modulin nimi on lyhyt ja kirjoitetaan
  pienillä kirjaimilla.
- **Tuonnit tiedoston alkuun**, ensin standardikirjasto, sitten
  ulkoiset kirjastot ja viimeisenä omat modulit (ruff järjestää ne).
  Ei `from moduli import *`, koska silloin lukija ei näe, mistä nimet
  tulevat.
- **Pääohjelma funktioon `main` ja `if __name__ == "__main__":`.**
  Moduli, jonka tuominen tekee jotain, yllättää käyttäjänsä.
- **Standardikirjasto ensin.** Valmis, testattu `datetime` on parempi
  kuin oma päivämäärälaskenta, joka unohtaa karkausvuodet.
- **Ulkoinen kirjasto on riippuvuus**, jota pitää päivittää ja
  arvioida. Pieneen tehtävään standardikirjasto riittää yleensä.
- **Ajasta ja satunnaisuudesta riippuva koodi parametrisoidaan**, jotta
  sen voi testata.

## Itsearviointi

- Osaat jakaa ohjelman useaan moduliin ja tuoda modulin funktiot
  `import`-lauseella.
- Osaat selittää, mitä `if __name__ == "__main__":` tekee ja miksi
  sitä käytetään.
- Osaat etsiä tehtävään sopivan standardikirjaston modulin ja laskea
  päivämäärillä `datetime`-modulilla.
- Osaat luoda virtuaaliympäristön ja asentaa siihen kirjaston.
