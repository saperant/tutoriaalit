# Työkalut: testaus, laatu ja profilointi {.runko-tyokalut}

Python-projektin työkaluketju on vakiintunut: pytest testaukseen, ruff
tyyliin ja virhemalleihin, mypy tyyppeihin, `logging` lokitukseen ja
cProfile profilointiin. Testauksen ja jatkuvan integraation yleiset
periaatteet ovat taidossa *Käännösjärjestelmät, testaus ja CI* ja
optimoinnin menetelmät taidossa *Suorituskyvyn analyysi ja
optimointi*; tämä luku näyttää Pythonin välineet.

## pytest

pytestin perusteet (testifunktio, `assert`, parametrisointi ja
`pytest.raises`) esitellään taidossa *Ohjelmoinnin perusteet
(Python)*. Tässä ne kerrataan yhdellä esimerkillä ja lisätään
kiintopisteet ja doctest.

pytest on Pythonin tosiasiallinen testikehys. Testit ovat tavallisia
funktioita, joiden nimi alkaa `test_`, ja tarkistukset tavallisia
`assert`-lauseita. pytest kirjoittaa `assert`-lauseet uudelleen niin,
että epäonnistuessa se näyttää molempien puolten arvot. Testattava
funktio jäsentää rahasumman:

```{.python tiedosto="esimerkit/13-testit.py" osa="koodi"}
```

Testit:

```{.python tiedosto="esimerkit/13-testit.py" osa="testit"}
```

- `@pytest.mark.parametrize` ajaa saman testin usealla syötteellä.
  Jokainen tapaus raportoidaan erikseen `ids`-argumentin nimellä.
- `pytest.raises` tarkistaa, että lohko nostaa poikkeuksen, ja `match`
  tarkistaa viestin säännöllisellä lausekkeella.
- *Kiintopiste* (*fixture*) on funktio, joka valmistelee testin
  tarvitseman ympäristön. Testi pyytää sitä parametrin nimellä.
  Sisäänrakennettu `tmp_path` antaa jokaiselle testille oman
  väliaikaisen hakemiston; `monkeypatch` vaihtaa ympäristömuuttujia ja
  attribuutteja testin ajaksi; `capsys` sieppaa tulosteen. Yhteiset
  kiintopisteet kirjoitetaan tiedostoon `conftest.py`.

Tavallisesti testit ajetaan komennolla `pytest` projektin juuressa, ja
pytest löytää `tests/test_*.py`-tiedostot itse. Tämä esimerkki ajaa
itsensä `pytest.main`-kutsulla ja tulostaa tulokset omalla
liitännäisellä, jotta tuloste on toistettava:

```{.tuloste tiedosto="esimerkit/13-testit.odotettu"}
```

Hyödyllisiä valitsimia: `-x` pysähtyy ensimmäiseen virheeseen, `-k nimi`
valitsee testit nimen perusteella, `--lf` ajaa vain viimeksi
epäonnistuneet, `-q` tiivistää tulosteen ja `--pdb` avaa debuggerin
virheen kohdalla. Kattavuus mitataan `pytest-cov`-liitännäisellä
(`--cov=varasto`). Standardikirjaston `unittest` on xUnit-tyylinen
vaihtoehto, jonka testit pytest osaa myös ajaa; `unittest.mock`
tarjoaa valeoliot molempiin.

Tulosteen ensimmäinen rivi `13-testit.jasenna_summa` on *doctest*:
funktion `jasenna_summa` dokumentaatiomerkkijonossa on tulkin istunnon
muotoinen esimerkki (`>>>`-rivi ja sen tulos), ja valitsin
`--doctest-modules` ajaa sen testinä. Ilman pytestiä saman tekee
`python -m doctest tiedosto.py`. Doctest varmistaa, että
dokumentaation esimerkit pitävät paikkansa. Se sopii puhtaiden
funktioiden muutamaan havainnolliseen esimerkkiin, mutta ei korvaa
yksikkötestejä: rajatapaukset ja virhepolut tekisivät
dokumentaatiosta lukukelvotonta. Rajapintaviitteen tuottaminen
dokumentaatiomerkkijonoista (Sphinx ja autodoc) on taidossa
*Tekninen dokumentaatio*.

## Koodin laatu

| Työkalu | Tehtävä | Komento |
|---------|---------|---------|
| ruff | virhemallit, tyyli, tuontien järjestys | `ruff check --fix .` |
| ruff format | muotoilu (Black-yhteensopiva) | `ruff format .` |
| mypy | tyyppitarkistus | `mypy --strict src` |
| pytest | testit | `pytest -q` |
| pre-commit | edellisten ajo ennen jokaista committia | `pre-commit install` |

Ruffin sääntöryhmät valitaan `pyproject.toml`-tiedostossa. Tämän
tutoriaalin esimerkit käyttävät ryhmiä E ja F (pycodestyle, pyflakes),
B (bugbear: yleiset bugit kuten muuttuva oletusarvo), UP (pyupgrade:
vanhentunut syntaksi) ja SIM (yksinkertaistukset). Kun sääntö
halutaan ohittaa yksittäisellä rivillä, käytetään
`# noqa: SÄÄNTÖ` -kommenttia, kuten luvun 3 esimerkissä.

## Debuggaus

`breakpoint()` pysäyttää ohjelman ja avaa `pdb`-debuggerin. Tärkeimmät
komennot ovat `n` (seuraava rivi), `s` (astu funktioon), `c` (jatka),
`p lauseke` (tulosta), `w` (pino) ja `q` (lopeta). `python -m pdb
ohjelma.py` käynnistää ohjelman debuggerissa ja pysähtyy kaatuessa.
Editorien debuggerit (VS Code, PyCharm) käyttävät samaa mekanismia
graafisesti. `python -X dev` kytkee päälle lisätarkistuksia ja
varoituksia, ja `faulthandler` tulostaa pinojäljen, kun ohjelma jumittuu
tai kaatuu C-tasolla.

## Lokitus

`print` on käyttäjälle tarkoitettua tulostetta; diagnostiikka kuuluu
`logging`-moduulille. Lokittajat muodostavat pisteillä erotetun
hierarkian, jonka tasoja voi säätää osittain. Lokitus määritellään
kerran sovelluksen käynnistyksessä:

```{.python tiedosto="esimerkit/13-loki.py" osa="asetus"}
```

Moduulit pyytävät oman lokittajansa nimellä ja lokittavat sen kautta:

```{.python tiedosto="esimerkit/13-loki.py" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/13-loki.odotettu"}
```

- `logging.getLogger(__name__)` antaa jokaiselle moduulille lokittajan,
  jonka nimi vastaa pakettirakennetta. Taso voidaan säätää koko
  paketille (`kauppa`) tai osalle (`kauppa.tilaus`).
- Viestin argumentit annetaan erikseen (`"tilaus %d", tilaus_id`), ei
  f-merkkijonona. Muotoilu tehdään vain, jos viesti todella kirjataan,
  ja lokipalvelut voivat ryhmitellä viestit muotoilemattoman pohjan
  mukaan.
- `loki.exception` kirjaa viestin `ERROR`-tasolla ja liittää mukaan
  käsiteltävän poikkeuksen. Esimerkin muotoilija tiivistää poikkeuksen
  yhdelle riville; oletusmuotoilija tulostaa koko pinojäljen.
- Kirjasto ei koskaan kutsu `basicConfig`-funktiota: lokituksen
  määrittely kuuluu sovellukselle. Tuotannossa muoto sisältää ajan, ja
  lokit kirjoitetaan usein JSON-muodossa keskitettyyn palveluun.

## Profilointi

Optimointi alkaa mittaamisesta. `cProfile` laskee jokaisen funktion
kutsumäärät ja ajat. Komentoriviltä koko ohjelma profiloidaan
komennolla `python -m cProfile -s cumtime ohjelma.py`; koodissa
profiloija on kontekstinhallitsija:

```{.python tiedosto="esimerkit/13-profilointi.py" osa="profiloi"}
```

```{.tuloste tiedosto="esimerkit/13-profilointi.odotettu"}
```

Esimerkki tulostaa vain kutsumäärät, koska ajat vaihtelevat ajosta
toiseen. Ne kertovat jo olennaisen: naiivi rekursio kutsuu funktiota
21 891 kertaa, välimuistillinen 21 kertaa. Tavallisesti tulokset
tulostetaan `pstats.Stats(profiili).sort_stats("cumtime").print_stats(10)`
-kutsulla. `Stats.stats`-attribuutti ei kuulu dokumentoituun
rajapintaan, joten tyyppimäärittely puuttuu ja esimerkki ohittaa mypyn
varoituksen.

cProfile mittaa funktiotasolla ja hidastaa ohjelmaa. Muita välineitä:

- `timeit` mittaa pienen koodinpätkän toistamalla sitä
  (`python -m timeit "sum(range(1000))"`).
- *py-spy* on otantaprofiloija, joka liitetään käynnissä olevaan
  prosessiin ilman koodimuutoksia ja tuottaa liekkikaavion.
- *line_profiler* mittaa rivi riviltä, *tracemalloc* ja *memray*
  muistinkäytön.

## Mitä Pythonissa kannattaa optimoida

Suurin hyöty tulee lähes aina algoritmista ja tietorakenteesta, ei
mikro-optimoinnista. Esimerkki mittaa kaksi luvussa 5 mainittua eroa;
tuloste kertoo vain, onko ero suuruusluokan verran:

```{.python tiedosto="esimerkit/13-hinnat.py" osa="hinnat"}
```

```{.tuloste tiedosto="esimerkit/13-hinnat.odotettu"}
```

![Haun `x in kokoelma` kesto, kun alkiota ei löydy (CPython 3.13,
pienin viidestä mittauksesta, molemmat akselit logaritmisia). Listan
haku hidastuu samassa suhteessa kuin lista kasvaa; joukon haku ei
riipu koosta.](kuvat/jasenyys.png){width=70%}

Kuvaajan tuottaa `kuvat/piirra.py` (`make kuvat`). Mitatut ajat
vaihtelevat koneen ja ajon mukaan, minkä vuoksi testattu esimerkki
tarkistaa vain suuruusluokan.

Kun algoritmi on kunnossa ja profiloija osoittaa kuuman kohdan,
CPythonissa auttavat seuraavat keinot, suunnilleen hyödyn mukaan:

1. Työn siirtäminen C-tasolle: sisäänrakennetut funktiot (`sum`, `max`,
   `sorted`, `str.join`), koostelausekkeet, `itertools`, `collections`.
2. Vektorointi NumPyllä: silmukka koko taulukon operaatioksi.
3. Turhan työn poisto silmukasta: vakiolausekkeet, säännöllisten
   lausekkeiden käännös ja tuonnit silmukan ulkopuolelle,
   `functools.cache` toistuville laskuille.
4. Attribuuttihakujen ja kutsujen vähentäminen kuumimmassa silmukassa,
   esimerkiksi metodin sitominen paikalliseen nimeen
   (`lisaa = tulos.append`). Hyöty on kymmeniä prosentteja, joten keino
   kuuluu vain mitattuihin kohtiin.
5. Raskaampi työkalu: PyPy, Cython, Numba tai C-, C++- tai
   Rust-laajennus (taito *Python ja C/C++ yhteen*).

## Käytännössä

- **pytest ja kiintopisteet.** Testit ovat pieniä funktioita;
  parametrisointi korvaa kopioidut testit ja kiintopisteet
  valmistelukoodin. `tmp_path` ja `monkeypatch` pitävät testit
  eristettyinä ja rinnakkain ajettavina.
- **Automaattiset portit.** `ruff check`, `ruff format --check`,
  `mypy --strict` ja `pytest` ajetaan CI:ssä jokaisessa muutoksessa ja
  paikallisesti pre-commit-koukulla. Tyyli ei ole katselmoinnin aihe.
- **`logging`, ei `print`, diagnostiikkaan.** Lokittaja moduulia
  kohden, määrittely kerran pääohjelmassa, laiska muotoilu ja
  `exception` poikkeuksille.
- **Mittaa ennen optimointia.** cProfile tai py-spy kertoo kuuman
  kohdan; arvaus osuu harvoin. `timeit` vertailee vaihtoehtoja.
- **Hinta:** cProfile hidastaa kutsuintensiivistä koodia jopa
  kaksinkertaisesti ja vääristää pienten funktioiden osuutta;
  otantaprofiloija ei. Lokikutsu, jonka taso on suodatettu pois,
  maksaa silti funktiokutsun; kalliit argumentit suojataan
  `loki.isEnabledFor(logging.DEBUG)`-tarkistuksella.
- **Sudenkuopat:** testit, jotka riippuvat toistensa järjestyksestä tai
  jaetusta tilasta, `assert` tuotantokoodin tarkistuksena, `basicConfig`
  kirjastossa ja mikro-optimointi ilman mittausta.

## Itsearviointi

- Osaat kirjoittaa pytest-testejä parametrisoinnilla,
  `pytest.raises`-tarkistuksella ja kiintopisteillä.
- Osaat kirjoittaa dokumentaatiomerkkijonoon doctest-esimerkin, ajaa
  sen ja perustella, milloin doctest riittää ja milloin ei.
- Osaat ottaa käyttöön ruffin ja mypyn ja ajaa ne automaattisesti.
- Osaat debugata ohjelmaa `breakpoint()`-kutsulla ja pdb:n komennoilla.
- Osaat määritellä lokituksen sovellukseen ja lokittaa moduuleista
  laiskalla muotoilulla.
- Osaat profiloida ohjelman cProfilella ja valita optimointikeinon
  mittauksen perusteella.
