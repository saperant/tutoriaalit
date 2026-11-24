# Tyyppivihjeet ja testaus

Työkalun tuloksiin nojataan päätöksissä: onko regressio puhdas,
täyttyykö ajoitus, onko rekisterikartta oikein. Siksi työkalu
testataan kuten muukin ohjelmisto. Tyyppivihjeet ja `mypy --strict`
löytävät virheet ennen ajoa, ja pytest varmistaa toiminnan.

## Tyypit rajapinnoissa

Regressioajon tulokset ovat JSON Lines -tiedostossa: yksi
JSON-objekti riviä kohden. `TypedDict` kuvaa objektin rakenteen ja
`Literal` sallitut arvot, joten mypy huomaa kirjoitusvirheen
avaimessa tai tilassa:

```{.python tiedosto="esimerkit/10-raportti/raportti.py" osa="tyypit"}
```

Logiikka on puhtaita funktioita. Kellonaika ja ympäristömuuttuja ovat
ainoat ulkoiset riippuvuudet, ja ne on eristetty niin, että testi voi
korvata ne:

```{.python tiedosto="esimerkit/10-raportti/raportti.py" osa="logiikka"}
```

`cast(AjoTulos, data)` kertoo mypylle, että tarkistettu sanakirja on
oikeaa tyyppiä. `cast` ei tarkista mitään ajon aikana, joten se tulee
vasta varsinaisen tarkistuksen jälkeen.

## pytest: fixturet ja monkeypatch

*Fixture* on funktio, joka valmistelee testin tarvitseman asian.
pytest antaa sen testille parametrin nimen perusteella. `tmp_path` on
pytestin oma fixture, joka antaa tyhjän tilapäishakemiston jokaiselle
testille. `monkeypatch` korvaa attribuutteja ja ympäristömuuttujia ja
palauttaa ne testin jälkeen:

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
$ python3 -m pytest -q
......                                                           [100%]
6 passed in 0.02s
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

- Osaat kuvata JSON-rakenteen `TypedDict`illä ja sallitut arvot
  `Literal`illa.
- Osaat kirjoittaa fixtureja ja käyttää `tmp_path`- ja
  `monkeypatch`-fixtureja kellon ja ympäristön kiinnittämiseen.
- Osaat parametrisoida testin ja testata virheellisen syötteen
  hylkäämisen.
- Osaat kirjoittaa tilannekuvatestin ja päivittää tilannekuvan
  hallitusti.
