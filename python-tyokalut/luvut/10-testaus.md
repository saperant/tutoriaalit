# Testaus

Työkalun tuloksiin nojataan päätöksissä: onko regressio puhdas,
täyttyykö ajoitus, onko rekisterikartta oikein. Siksi työkalu
testataan kuten muukin ohjelmisto. Tyyppivihjeet ja `mypy --strict`
ovat olleet käytössä jokaisessa esimerkissä ja löytävät virheet ennen
ajoa; pytest varmistaa toiminnan. pytestin perusteet (fixturet,
`tmp_path`, `monkeypatch`, parametrisointi) ja ulkoisen datan tyypit
(`TypedDict`, `Literal`, `cast`) esitellään taidossa *Python*. Tämä
luku soveltaa niitä työkaluun ja lisää kaksi työkaluille tyypillistä
tekniikkaa: kellon ja ympäristön eristämisen sekä tilannekuvatestin.

## Testattava työkalu

Regressioajon tulokset ovat JSON Lines -tiedostossa: yksi
JSON-objekti riviä kohden. `TypedDict` kuvaa objektin rakenteen ja
`Literal` sallitut arvot:

```{.python tiedosto="esimerkit/10-raportti/raportti.py" osa="tyypit"}
```

Logiikka on puhtaita funktioita. Kellonaika ja ympäristömuuttuja ovat
ainoat ulkoiset riippuvuudet, ja ne on eristetty niin, että testi voi
korvata ne:

```{.python tiedosto="esimerkit/10-raportti/raportti.py" osa="logiikka"}
```

`cast` ei tarkista mitään ajon aikana, joten se tulee vasta
varsinaisen tarkistuksen jälkeen.

## Kellon ja ympäristön eristäminen

Raportin otsikossa on kellonaika ja ympäristömuuttujasta luettu nimi,
joten tuloste muuttuisi ajosta toiseen. Fixture `tmp_path` antaa
testille oman tilapäishakemiston, ja `monkeypatch` korvaa attribuutteja
ja ympäristömuuttujia testin ajaksi:

```{.python tiedosto="esimerkit/10-raportti/test_raportti.py" osa="fixture"}
```

Kellonaika korvataan korvaamalla moduulin funktio `nyt`. Koodi kutsuu
`nyt()`-funktiota moduulin kautta, joten korvaus näkyy sille. Jos
koodi kutsuisi suoraan `datetime.now()`, aikaa ei voisi kiinnittää.

## Parametrisointi ja virhetilanteet

`parametrize` ajaa saman testin monella syötteellä, ja jokainen
tapaus näkyy raportissa omana testinään. Reunatapaukset (tyhjä ajo)
kuuluvat mukaan. `pytest.raises` testaa, että virheellinen syöte
hylätään oikealla viestillä:

```{.python tiedosto="esimerkit/10-raportti/test_raportti.py" osa="parametrit"}
```

Puhtaan funktion käyttöesimerkin voi kirjoittaa myös funktion
dokumentaatiomerkkijonoon. Esimerkin funktiossa `yhteenveto` on
tulkin istunnon muotoinen *doctest*, jonka `pytest --doctest-modules`
ajaa muiden testien mukana. Näin dokumentaation esimerkki ei voi
vanheta huomaamatta. Doctest sopii jäsennys- ja muunnosfunktioiden
(kuten luvun 2 taajuuden jäsennys) muutamaan havainnolliseen
tapaukseen; rajatapaukset kuuluvat parametrisoituihin testeihin.
Dokumentaation rakentaminen ja sen esimerkkien testaus laajemmin on
taidossa *Tekninen dokumentaatio*.

## Tilannekuvatesti

Raporttityökalun tuloste on pitkä teksti, jonka jokaisen rivin
vertaaminen käsin kirjoitettuun odotukseen on työlästä. *Tilannekuva*
(*snapshot*) on tallennettu tuloste, johon testi vertaa. Kun tuloste
muuttuu tarkoituksella, tilannekuva päivitetään
ympäristömuuttujalla, ja muutos tarkistetaan versionhallinnan
erosta:

```{.python tiedosto="esimerkit/10-raportti/test_raportti.py" osa="tilannekuva"}
```

```{.text tiedosto="esimerkit/10-raportti/odotetut/raportti.txt"}
```

Testit ajetaan hakemistossa:

```text
$ python3 -m pytest -q --doctest-modules
.......                                                          [100%]
7 passed in 0.02s
$ PAIVITA_ODOTETUT=1 python3 -m pytest -q   # tarkoituksellinen muutos
$ git diff odotetut/
```

Sama moduuli tuottaa raportin pääohjelmasta:

```{.python tiedosto="esimerkit/10-raportti/main.py"}
```

```{.tuloste tiedosto="esimerkit/10-raportti.odotettu"}
```

## Käytännössä

- **Testaa funktioita, ei prosesseja.** Kun `main(argv)` ja logiikka
  ovat funktioita, testit ovat nopeita eivätkä tarvitse aliprosesseja.
  Muutama päästä päähän -testi riittää varmistamaan kytkennät.
- **Eristä aika, satunnaisuus ja ympäristö.** Ne tekevät testeistä
  epädeterministisiä. Anna ne parametreina tai korvattavina
  funktioina.
- **Testiaineisto koodina tai pieninä tiedostoina testin vieressä.**
  Ei polkuja verkkolevylle tai kehittäjän kotihakemistoon.
- **Tilannekuvatesti tulosteille, tarkat väitteet logiikalle.**
  Tilannekuva näyttää muutoksen mutta ei kerro, onko se oikein.
  Katselmoija lukee eron.
- **`mypy --strict` ja ruff CI:ssä.** Tyyppivirheet ja tyypilliset
  bugit (muuttuva oletusarvo, käyttämätön muuttuja) löytyvät ilman
  testejä.
- **Sudenkuoppa:** testit, jotka riippuvat toistensa järjestyksestä tai
  jakavat tilaa. Jokainen testi luo aineistonsa itse (`tmp_path`).

## Itsearviointi

- Osaat rakentaa työkalun niin, että kellonaika ja ympäristö ovat
  korvattavissa, ja kiinnittää ne testissä `monkeypatch`-fixturella.
- Osaat kirjoittaa funktion dokumentaatiomerkkijonoon doctest-esimerkin
  ja ajaa sen pytestillä.
- Osaat parametrisoida testin ja testata virheellisen syötteen
  hylkäämisen.
- Osaat kirjoittaa tilannekuvatestin ja päivittää tilannekuvan
  hallitusti.
