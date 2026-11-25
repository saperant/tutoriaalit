# Johdanto {.runko-johdanto}

Python on hyvä kieli työkalujen, analyysien ja sovellusten
liimaamiseen yhteen, mutta yksittäinen Python-silmukka on kymmeniä
kertoja hitaampi kuin sama silmukka C:llä tai C++:lla. Toisaalta
suurin osa maailman numeriikasta, kuvankäsittelystä, laiteajureista ja
tiedostomuotojen kirjastoista on kirjoitettu C:llä tai C++:lla. Kielten
raja on siksi arkipäivää: NumPy, SciPy, PyTorch, OpenCV ja
`cryptography` ovat kaikki Python-rajapintoja natiivikoodin päällä.

Tämä tutoriaali opettaa tekemään saman itse ja tekemään sen oikein.
Kielten rajalla virheet ovat erilaisia kuin kummassakaan kielessä
erikseen: väärä tyyppi kaataa koko tulkin, unohtunut viite vuotaa
muistia, väärä omistaja vapauttaa muistin kahdesti, ja huomaamaton
kopio syö koko nopeushyödyn. Siksi jokaisen luvun keskiössä on
kysymys siitä, kuka omistaa minkäkin datan ja kuinka kauan.

## Esitiedot ja rajaus

Esitietona ovat taidot *Python työkaluohjelmointiin* (NumPy,
paketointi, pytest) ja *Moderni C++* (luokat, RAII, `std::vector`,
`std::span`) sekä C-kielen perusteet: osoittimet, `malloc`/`free` ja
`errno`.

Tutoriaali käsittelee Pythonin laajentamista natiivikoodilla. Toinen
suunta, Python-tulkin upottaminen C++-ohjelmaan
(`py::scoped_interpreter`), on rajattu pois. Jaetut kirjastot,
symbolien näkyvyys ja ABI on käsitelty tarkemmin taidossa
*Objektitiedostot, linkitys ja ABI*, C++-koodin oma nopeus taidossa
*C++:n suorituskyky* ja profiloinnin menetelmät taidossa
*Suorituskyvyn analyysi ja optimointi*.

## Milloin kielten rajaa tarvitaan

Natiivikoodia tarvitaan kolmesta syystä:

- **Olemassa oleva kirjasto.** C- tai C++-kirjasto tekee jo sen, mitä
  tarvitaan: tiedostomuodon purku, laiteohjain, numeerinen ratkaisija.
  Sitä ei kirjoiteta uudelleen Pythonilla, vaan sille tehdään
  Python-rajapinta.
- **Laskenta, jota ei voi vektoroida.** NumPy on nopea, kun lasku
  ilmaistaan kokonaisille taulukoille. Kun jokainen askel riippuu
  edellisestä (suodattimet, tilakoneet, simulaatiot), silmukka on
  kirjoitettava jollakin kääntyvällä kielellä.
- **Rinnakkaisuus ja laitteisto.** C++-säikeet voivat laskea
  rinnakkain ilman Pythonin tulkkilukkoa, ja natiivikoodi pääsee
  käsiksi laitteisiin ja käyttöjärjestelmän rajapintoihin suoraan.

Rajalla on hintansa: käännösvaihe, alustakohtaiset binäärit,
vaikeampi virheenjäljitys ja uusi virhetyyppien joukko. Siksi luku 2
aloittaa mittaamisesta. Usein ongelma ratkeaa NumPylla, ja vasta kun
se ei riitä, tarvitaan tämän tutoriaalin välineitä.

## Välineet

| Väline | Mitä se on | Milloin |
|--------|-----------|---------|
| `ctypes` | vakiokirjaston C-kutsurajapinta, ei käännöstä | valmis C-kirjasto, muutama funktio |
| cffi | C-otsakkeista sidonnat, erillinen paketti | laaja C-kirjasto, PyPy |
| pybind11 | C++-otsakekirjasto laajennusmoduuleille | C++-koodi, luokat, poikkeukset |
| nanobind | pybind11:n kevyempi seuraaja | uusi projekti, pienet ja nopeat sidonnat |
| Pythonin C-API | tulkin oma rajapinta | kirjastojen sisäosat, ymmärrys |
| Cython, Numba | Pythonin näköinen kieli tai JIT | numeriikka ilman C++:aa |

Tutoriaali käyttää kahta ensimmäistä ja kahta seuraavaa käytännössä ja
näyttää C-API:n, jotta muiden välineiden tekemä työ ymmärretään.
Cython ja Numba mainitaan vaihtoehtoina luvussa 2.

## Esimerkit ja työkalut

Esimerkit on testattu Python 3.12:lla ja 3.13:lla, GCC 14:llä,
pybind11 3.1:llä ja nanobind 3.1:llä. Jokainen esimerkki on hakemisto,
jossa on C- tai C++-lähde, Python-ohjelma `main.py`, tyyppitiedosto
`.pyi` ja odotettu tuloste. Esimerkkien `Makefile` kääntää kaikki
moduulit hakemistoon `build/`, tarkistaa Python-koodin `ruff`illa ja
`mypy --strict`illä ja vertaa tulosteet odotettuihin:

```text
cd esimerkit
make                    # käännä, tarkista ja aja kaikki
cd 05-pybind11 && PYTHONPATH=../build python3 main.py
```

C++ käännetään varoitukset virheinä (`-Wall -Wextra -Werror`).
Laajennusmoduulin tiedostonimessä on tulkin versio ja alusta, ja sen
pääte saadaan tulkilta itseltään. Makefilen alku näyttää liput, joita
kaikki luvut käyttävät:

```{.makefile tiedosto="esimerkit/Makefile" osa="liput"}
```

- **`-fPIC`** tuottaa sijainnista riippumatonta koodia, jota jaettu
  kirjasto vaatii.
- **`-fvisibility=hidden`** piilottaa moduulin sisäiset symbolit.
  Pythonille riittää yksi näkyvä alustusfunktio, ja piilottaminen
  estää kahden moduulin samannimisiä symboleita sekoittumasta.
- **`-isystem`** merkitsee Pythonin, pybind11:n ja nanobindin otsakkeet
  järjestelmäotsakkeiksi, jolloin niiden varoitukset eivät kaada
  `-Werror`-käännöstä.

Kehityskontissa (`.devcontainer/python-c-integraatio`) on kaikki
valmiina. Ilman konttia tarvitaan Pythonin kehitysotsakkeet
(`python3-dev`) ja virtuaaliympäristö:

```text
python3 -m venv .venv && . .venv/bin/activate
pip install pybind11==3.1.0 nanobind==3.1.0 numpy setuptools wheel \
    ruff mypy pytest
```

## Tutoriaalin rakenne

Luku 2 mittaa, missä aika kuluu, ja kertoo, milloin NumPy riittää.
Luvut 3–4 käyttävät C-kirjastoa `ctypes`illä ja suunnittelevat C++:lle
C-rajapinnan, joka kestää kielten rajan. Luvut 5–7 kirjoittavat
laajennusmoduuleja pybind11:llä ja nanobindilla: funktiot, luokat,
poikkeukset, tyyppimuunnokset ja elinajat. Luku 8 käsittelee
NumPy-taulukoita ilman kopioita, ja luku 9 mittaa kutsun hinnan ja
perustelee paketin tärkeimmän suunnittelusäännön. Luku 10 käsittelee
tulkkilukkoa ja säikeitä, luku 11 kurkistaa Pythonin C-API:in ja
viitelaskentaan ja luku 12 paketoi laajennuksen jaettavaksi
pyöräksi. Jokainen luku päättyy osioihin *Käytännössä* ja
*Itsearviointi*. Jos osaat itsearvioinnin asiat, voit siirtyä
seuraavaan lukuun.
