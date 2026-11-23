# Python kokeneelle {.runko-kokeneelle}

Tämä luku on tarkoitettu kehittäjälle, joka osaa C++:n, Javan tai
JavaScriptin ja haluaa kirjoittaa idiomaattista Pythonia nopeasti. Luku
kokoaa Pythonin ajattelutavan, vastaavuudet, hinnat ja sudenkuopat.
Lukuohje on luvun lopussa.

## Ajattelutapa

- **Kaikki on olio, ja nimet ovat viittauksia.** Kokonaisluku, funktio,
  luokka ja moduuli ovat olioita. Sijoitus `b = a` ei koskaan kopioi:
  se sitoo uuden nimen samaan olioon. Tämä vastaa Javan ja JavaScriptin
  oliomuuttujia, mutta koskee myös lukuja ja merkkijonoja.
- **Dynaaminen tyypitys, staattinen tarkistus erikseen.** Tulkki ei
  tarkista tyyppiannotaatioita. Ammattimaisessa koodissa mypy tai
  Pyright tekee sen, mitä C++:n tai Javan kääntäjä tekee. Ilman
  tarkistinta virheet löytyvät vasta ajon aikana.
- **Protokollat ennen perintää.** Python-koodi kysyy, mitä olio osaa,
  ei mikä se on (*duck typing*). Iteroitavuus, kontekstinhallinta,
  vertailu ja aritmetiikka ovat erikoismetodeja kuten `__iter__` ja
  `__eq__`, joita kieli kutsuu.
- **Luettavuus on tavoite.** Yksi ilmeinen tapa tehdä asia (*The Zen
  of Python*, `import this`). Sisennys on syntaksia. Tyylin määrää PEP 8,
  ja käytännössä sen valvoo muotoilija (`ruff format`, Black).
- **Paristot mukana.** Standardikirjastossa on CSV, JSON, SQLite,
  HTTP, säännölliset lausekkeet, päivämäärät, testaus ja paljon muuta.
  Ennen omaa toteutusta kannattaa katsoa sieltä.

## Vastaavuudet muihin kieliin

| Asia | C++ | Java | JavaScript | Python |
|----------------|----------------------|------------------|------------------|----------------------------|
| Dynaaminen taulukko | `std::vector` | `ArrayList` | `Array` | `list` |
| Hajautustaulu | `unordered_map` | `HashMap` | `Map` | `dict` (järjestys säilyy) |
| Joukko | `unordered_set` | `HashSet` | `Set` | `set`, `frozenset` |
| Tietue | `struct` | `record` | olioliteraali | `@dataclass` (luku 8) |
| Rajapinta | abstrakti luokka, konsepti | `interface` | ei | `Protocol`, `ABC` (luku 8) |
| Geneerisyys | mallit | generics | ei | tyyppiparametrit, vain tarkistimelle (luku 9) |
| Resurssien vapautus | RAII | try-with-resources | `try`/`finally` | `with` (luku 7) |
| Virheet | poikkeukset, `expected` | poikkeukset | poikkeukset | poikkeukset, halpoja (luku 10) |
| Puuttuva arvo | `nullptr`, `optional` | `null`, `Optional` | `null`, `undefined` | `None` |
| Laiska sarja | ranges | `Stream` | generaattori | generaattori (luku 6) |
| Lambda | `[&](int x){...}` | `x -> ...` | `x => ...` | `lambda x: ...` (yksi lauseke) |
| Näkyvyys | `private` | `private` | `#kenttä` | sopimus: `_nimi` |
| Asynkronisuus | korutiinit | virtuaalisäikeet | `async`/`await` | `async`/`await` (luku 12) |
| Paketinhallinta | vcpkg, Conan | Maven, Gradle | npm | pip, uv, `pyproject.toml` (luku 11) |

Muutama ero, joka yllättää:

- Kokonaisluvut ovat mielivaltaisen suuria: `2**100` ei vuoda yli.
  Jakolasku `/` palauttaa aina liukuluvun, ja `//` on lattiajako:
  `-7 // 2 == -4`, kun C++:ssa ja Javassa `-7 / 2 == -3`.
- `and`, `or` ja `not` ovat sanoja. `a or b` palauttaa jommankumman
  operandin, ei totuusarvoa, kuten JavaScriptin `||`.
- Totuusarvona tyhjä kokoelma, `0`, `""` ja `None` ovat epätosia.
  Idiomi on `if rivit:`, ei `if len(rivit) > 0:`.
- Vertailut ketjuuntuvat: `0 <= i < n`.
- `==` vertaa arvoa (`__eq__`) ja `is` identiteettiä. JavaScriptin
  `==`-tyyppimuunnoksia ei ole: `1 == "1"` on epätosi.
- Lohkolla ei ole omaa näkyvyysaluetta. Silmukan sisällä sidottu nimi
  näkyy silmukan jälkeen; näkyvyysalueet ovat moduuli, funktio ja
  luokka.
- Merkkijonot ovat muuttumattomia Unicode-merkkijonoja (`str`), ja
  tavut ovat eri tyyppi (`bytes`). Niitä ei voi sekoittaa.

## Hinnat

CPython tulkitsee tavukoodia. Hinta tulee siitä, että jokainen
operaatio on dynaaminen: `a + b` selvittää ajon aikana operandien
tyypit ja kutsuu oikeaa metodia. Nyrkkisääntöjä:

- **Python-tason operaatiot ovat kalliita, C-tason halpoja.**
  Silmukka, joka laskee summan alkio kerrallaan, on moninkertaisesti
  hitaampi kuin `sum()`, joka tekee saman C:ssä. Suorituskykyinen
  Python siirtää kuumat silmukat sisäänrakennettuihin funktioihin,
  kokoelmiin, koostelausekkeisiin ja kirjastoihin kuten NumPy.
- **Funktiokutsu ja attribuuttihaku maksavat.** Kutsu luo kehyksen
  ja attribuuttihaku `olio.x` käy läpi sanakirjoja. Ero näkyy vain
  kuumissa silmukoissa; luettavuus ensin, profilointi sitten.
- **Oikea kokoelma ratkaisee eniten.** `x in lista` on O(n) ja
  `x in joukko` O(1). `lista.pop(0)` siirtää kaikki alkiot, ja
  `deque.popleft()` on O(1). Luvussa *Työkalut* mitataan ero.
- **Poikkeukset ovat halpoja.** `try` ei maksa mitään, kun poikkeusta
  ei tapahdu, ja poikkeuksen nostaminenkin on Pythonin mittakaavassa
  halpaa. Siksi Python suosii EAFP-tyyliä (luku 10), toisin kuin C++.
- **Olio vie tilaa.** Pieni kokonaisluku on 28 tavua ja tavallinen
  olio sanakirjoineen satoja tavuja. Miljoonien olioiden kanssa
  `__slots__` tai `array`/NumPy säästää muistia.
- **Globaali tulkkilukko (GIL).** Vain yksi säie suorittaa
  Python-koodia kerrallaan. Säikeet sopivat odottamiseen (I/O),
  laskentaan tarvitaan prosesseja tai C-kirjastoja (luku 12).

## Tärkeimmät sudenkuopat

1. **Muuttuva oletusarvo** `def f(x=[])` luodaan kerran, kun funktio
   määritellään, ja se jaetaan kaikkien kutsujen kesken (luku 3).
2. **Viittausten jakaminen.** `[[0] * 3] * 3` luo kolme viittausta
   samaan sisälistaan. Sisäkkäinen rakenne kopioidaan `deepcopy`llä.
3. **Iteraattori kuluu.** Generaattorin tai `map`-olion voi käydä läpi
   vain kerran; toinen läpikäynti on hiljaa tyhjä (luku 6).
4. **Sulkeuma sitoo nimen, ei arvoa.** Silmukassa luodut lambdat
   näkevät kaikki silmukkamuuttujan viimeisen arvon.
5. **Leveä `except`.** `except Exception: pass` piilottaa ohjelmointi-
   virheet. Siepataan vain odotetut poikkeukset (luku 10).
6. **Tyyppiannotaatio ei ole tarkistus.** `def f(n: int)` hyväksyy
   ajon aikana minkä tahansa olion. Ulkoinen syöte validoidaan rajalla.
7. **Liukuluvut rahalle.** Käytä `Decimal`-tyyppiä tai kokonaislukuja
   senteissä.
8. **Kiertävät tuonnit ja moduulitason sivuvaikutukset.** Moduulin
   koodi ajetaan tuonnin yhteydessä. Pääohjelma kuuluu
   `if __name__ == "__main__":` -lohkoon (luku 11).

## Lukuohje kokeneelle

Lue ensin kunkin luvun *Itsearviointi*. Jos hallitset väitteet, siirry
eteenpäin. Kokeneelle tärkeimmät luvut ovat:

- **Tietomalli** (luku 3): viittaukset, muuttuvuus ja oletusarvot,
  joista suurin osa Python-bugeista syntyy.
- **Iteraattorit ja generaattorit** (luku 6) sekä **resurssit**
  (luku 7): Pythonin vastineet C++:n rangeille ja RAII:lle.
- **Tyypitys** (luku 9): mitä mypy osaa ja miten geneerinen koodi
  kirjoitetaan.
- **Rinnakkaisuus** (luku 12): GIL ja oikean mallin valinta.

Luvun 14 *Käytännöt* kokoaa idiomit ja nyrkkisäännöt, ja erillinen
pikaopas tiivistää syntaksin muutamalle sivulle.
