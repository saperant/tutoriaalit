# Johdanto {.runko-johdanto}

Python on Guido van Rossumin 1989 aloittama ja 1991 julkaisema
yleiskäyttöinen ohjelmointikieli. Sen tavoitteena oli kieli, jota on
helppo lukea ja jolla saa nopeasti aikaan toimivan ohjelman. Python on
dynaamisesti tyypitetty: muuttujalla ei ole tyyppiä, vaan oliolla on.
Muistia hallitaan automaattisesti. Standardikirjasto on laaja, ja sen
periaatteeksi on sanottu "paristot mukana".

Python 3 julkaistiin 2008, ja se rikkoi yhteensopivuuden Python 2:n
kanssa: merkkijonot muuttuivat Unicodeksi ja `print` funktioksi.
Siirtymä kesti yli kymmenen vuotta, ja Python 2:n tuki päättyi 2020.
Vanhoissa ohjeissa näkyy yhä Python 2 -koodia, joten tämä mainitaan.

Tavoitteena on idiomaattinen ja ammattimainen Python: miten kieli toimii
pinnan alla, mitkä rakenteet ovat kalliita, ja miten tuotantokoodi
tyypitetään, testataan ja jäsennetään paketeiksi.

## Esitiedot ja rajaus

Esitietona on taito *Ohjelmoinnin perusteet (Python)*: tutoriaali ei
opeta ohjelmoinnin perusteita, vaan olettaa, että lukija osaa kirjoittaa
Pythonilla muuttujia, ehtoja, silmukoita, funktioita ja yksinkertaisia
luokkia.

Tutoriaali ei käsittele seuraavia aiheita:

- komentorivityökalut, tiedostomuotojen jäsentäminen ja ulkoisten
  ohjelmien ohjaus: taito *Python työkaluohjelmointiin*
- C- ja C++-laajennukset: taito *Python ja C/C++ yhteen*
- rinnakkaisuuden yleinen teoria: taito *Rinnakkaisohjelmointi*
- verkkopalvelut, tietokannat ja data-analyysin kirjastot: ne mainitaan
  viimeisen luvun kirjastotaulukossa.

## Mihin Python sopii ja mihin ei

Python on vahvimmillaan, kun kehittäjän aika on kalliimpaa kuin
koneen aika tai kun valmiit kirjastot tekevät raskaan työn:

- datan käsittely, analytiikka, koneoppiminen ja tieteellinen laskenta
  (NumPy, pandas, PyTorch: laskenta tehdään C-, C++- tai
  Fortran-kirjastoissa)
- verkkopalvelut ja rajapinnat (Django, FastAPI), joissa aika kuluu
  tietokannan ja verkon odottamiseen
- automaatio, ylläpitoskriptit, testaus ja liimakoodi järjestelmien
  välillä
- prototyypit ja sisäiset työkalut.

Python ei ole hyvä valinta, kun

- puhdas Python-laskenta on pullonkaula: tulkattu silmukka on
  tyypillisesti 10–100 kertaa hitaampi kuin vastaava C-, C++-, Rust-
  tai Java-koodi
- tarvitaan ennustettava viive tai pieni muisti, esimerkiksi
  sulautetuissa ja reaaliaikajärjestelmissä (MicroPython on oma
  rajattu toteutuksensa)
- ohjelma jaetaan yhtenä binäärinä ilman ajonaikaista ympäristöä, tai
  ajetaan selaimessa tai mobiililaitteessa
- monisäikeinen laskenta on välttämätöntä (globaali tulkkilukko,
  luku *Rinnakkaisuus*).

## Versiot ja toteutukset

Uusi versio julkaistaan vuosittain lokakuussa, ja kutakin tuetaan viisi
vuotta. Kieltä kehitetään *PEP*-dokumenttien (Python Enhancement
Proposal) kautta.

| Versio | Keskeisiä lisäyksiä |
|--------|---------------------|
| 3.8 | `:=`-sijoituslauseke, vain sijainnilla annettavat parametrit `/` |
| 3.9 | `list[int]` ilman `typing`-tuontia, sanakirjojen yhdisteoperaattori |
| 3.10 | `match`-lause, tyyppiyhdisteet ilman `Union`-tuontia |
| 3.11 | 10–60 % nopeampi tulkki, `ExceptionGroup`, `except*`, `tomllib` |
| 3.12 | tyyppiparametrisyntaksi `def f[T]`, `type`-lause, `itertools.batched` |
| 3.13 | kokeellinen GIL-vapaa versio ja JIT, uusi interaktiivinen tulkki |
| 3.14 | GIL-vapaa versio virallisesti tuettu, laiskasti arvioidut annotaatiot |

Tämän tutoriaalin esimerkit vaativat Python 3.12:n. Uudempien versioiden
ominaisuudet mainitaan erikseen.

Viitetoteutus *CPython* on kirjoitettu C:llä, ja sitä tarkoitetaan,
kun puhutaan Pythonista. Muita toteutuksia ovat PyPy (JIT-kääntäjä,
usein moninkertaisesti nopeampi puhtaassa Python-koodissa) ja
MicroPython (mikro-ohjaimet). Tämän tutoriaalin hintatiedot koskevat
CPythonia.

## Työkalut

Esimerkit on testattu Linuxissa CPython 3.12:lla. Jokainen esimerkki
tarkistetaan ennen ajoa kahdella työkalulla:

```text
ruff check esimerkki.py        # tyyli- ja virhetarkistus (linter)
mypy --strict esimerkki.py     # staattinen tyyppitarkistus
python3 esimerkki.py
```

*Ruff* löytää käyttämättömät tuonnit, varjostetut nimet ja yleiset
virhemallit, ja se myös muotoilee koodin (`ruff format`). *Mypy*
tarkistaa tyyppiannotaatiot. Python itse ei tarkista annotaatioita
ajon aikana, joten ilman mypyä ne ovat pelkkää dokumentaatiota.
Asetukset ovat paketin tiedostossa `pyproject.toml` (luku *Modulit,
paketit ja projektin rakenne*). Luvussa *Työkalut* esitellään lisäksi
pytest, debuggeri ja profiloija.

Interaktiivinen tulkki (`python3` ilman argumentteja) sopii kokeiluihin.
`help(olio)` näyttää dokumentaation ja `dir(olio)` attribuutit.

## Ensimmäinen ohjelma

Ohjelma lukee kulut CSV-muodossa vakiosyötteestä ja laskee summat
luokittain:

```{.python tiedosto="esimerkit/01-kulut.py"}
```

Syöte:

```{.tuloste tiedosto="esimerkit/01-kulut.syote"}
```

Tuloste:

```{.tuloste tiedosto="esimerkit/01-kulut.odotettu"}
```

Lyhyessä ohjelmassa on jo monta tuotantokoodin tapaa:

- Rahasummat ovat `Decimal`-olioita, eivät liukulukuja: `0.1 + 0.2` ei
  ole liukulukuna tasan `0.3`.
- `csv.DictReader` jäsentää CSV:n oikein myös lainausmerkkien ja
  pilkkujen kanssa. Merkkijonon pilkkominen `split(",")`-kutsulla
  rikkoutuu ensimmäisestä lainatusta kentästä.
- `defaultdict(Decimal)` luo puuttuvalle avaimelle alkuarvon
  `Decimal()` eli nollan.
- Tyyppiannotaatiot (`-> int`, `dict[str, Decimal]`) dokumentoivat
  rajapinnan ja antavat mypyn tarkistaa sen.
- `if __name__ == "__main__":` ajaa `main`-funktion vain, kun tiedosto
  käynnistetään ohjelmana, ei kun se tuodaan moduulina. `sys.exit`
  välittää paluuarvon käyttöjärjestelmälle.

Ohjelma ajetaan komennolla `python3 01-kulut.py < kulut.csv`.

## Esimerkkien testaus

Kaikki tämän tutoriaalin koodi on peräisin hakemiston `esimerkit`
tiedostoista. Jokainen tiedosto tarkistetaan ruffilla ja
`mypy --strict` -tilassa, ajetaan tyhjässä väliaikaisessa hakemistossa
ja sen tulostetta verrataan tiedostoon, josta myös tekstissä näkyvät
tulosteet on poimittu.

Osa esimerkeistä näyttää koodia, jonka mypy hylkää. Ne testataan
kahdesti: ensin varmistetaan, että tarkistus epäonnistuu, ja sitten,
että se onnistuu, kun virheellinen rivi on poistettu. Muutama esimerkki
näyttää ajonaikaisen virheen, ja sen testi varmistaa, että ohjelma
todella kaatuu odotetulla tavalla.
