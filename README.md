# Tutoriaalit

Suomenkielisiä tutoriaaleja eri aiheista. Tutoriaalit kirjoitetaan
Markdownilla, ja lopullinen versio on PDF-dokumentti.

| Tutoriaali | Hakemisto | PDF |
|------------|-----------|-----|
| Moderni C++ | [`moderni-cpp/`](moderni-cpp/) | [moderni-cpp.pdf](moderni-cpp/moderni-cpp.pdf) |

## Periaatteet

- **Kieli:** suomi, asiallinen ja tiivis. Vakiintuneet englanninkieliset
  termit mainitaan suluissa, kun termi esitellään ensimmäisen kerran.
- **Testattu koodi:** ohjelmointiaiheisissa tutoriaaleissa kaikki koodi
  on erillisissä tiedostoissa, jotka käännetään ja ajetaan
  automaattisesti. Tekstiin koodi ja sen tuloste sisällytetään
  tiedostoista, joten tekstissä näkyy aina sama koodi, joka on testattu.
- **Lähteet:** lähdemateriaalina käytetään vain lisenssiltään
  yhteensopivia lähteitä, ja lähteet mainitaan.
- **Lisenssi:** kaikki materiaali on lisensoitu
  [CC BY-SA 4.0](LICENSE) -lisenssillä.

## Rakenne

```text
yhteiset/                 kaikille tutoriaaleille yhteiset työkalut
  pdf.yaml                pandocin PDF-asetukset
  tyyli.tex               PDF:n LaTeX-tyylit
  sisallyta.lua           pandoc-suodatin koodin sisällyttämiseen
  testaa_esimerkit.py     esimerkkikoodin testaaja
<tutoriaali>/
  Makefile                make testaa / make pdf / make
  metadata.yaml           otsikko, päiväys yms.
  luvut/NN-nimi.md        luvut järjestyksessä
  esimerkit/              koodiesimerkit ja niiden odotetut tulosteet
  <tutoriaali>.pdf        valmis PDF
```

## Rakentaminen

Tarvittavat ohjelmat (Ubuntu 24.04):

```text
sudo apt install make python3 pandoc g++-14 clang-20 libclang-rt-20-dev \
    texlive-xetex texlive-latex-recommended texlive-latex-extra \
    texlive-fonts-recommended texlive-lang-european lmodern fonts-dejavu
```

Juurihakemistossa `make` testaa ja rakentaa kaikki tutoriaalit.
Tutoriaalin omassa hakemistossa:

```text
make testaa   # kääntää, ajaa ja tarkistaa esimerkit
make pdf      # rakentaa PDF:n
make          # molemmat
```

GitHub Actions ajaa testit ja rakentaa PDF:t jokaisen muutoksen
yhteydessä (`.github/workflows/tutoriaalit.yml`).

## Koodiesimerkkien kirjoittaminen

Koodi sisällytetään Markdowniin tyhjällä koodilohkolla, jonka
attribuutti `tiedosto` kertoo lähdetiedoston:

````markdown
```{.cpp tiedosto="esimerkit/01-hei.cpp"}
```
````

Tiedostosta voi näyttää vain osan. Osa rajataan lähdekoodissa
kommenteilla `// @alku nimi` ja `// @loppu nimi`, ja se valitaan
attribuutilla `osa="nimi"`. Merkintäkommentit eivät näy PDF:ssä.

Ohjelman tuloste sisällytetään tiedostosta `<nimi>.odotettu`:

````markdown
```{.tuloste tiedosto="esimerkit/01-hei.odotettu"}
```
````

Testaaja (`yhteiset/testaa_esimerkit.py`) tarkistaa, että

- jokainen `cpp`-koodilohko viittaa tiedostoon (käsin kirjoitettua koodia
  ei sallita),
- jokainen esimerkki kääntyy GCC:llä ja Clangilla varoitukset virheinä
  (`-Wall -Wextra -Wpedantic -Werror`),
- ohjelma toimii AddressSanitizerin ja UndefinedBehaviorSanitizerin
  kanssa, ja rivin `// TSAN` sisältävät myös ThreadSanitizerin kanssa,
- ohjelman tuloste vastaa tiedostoa `<nimi>.odotettu`,
- tiedostot `<nimi>.ei-kaanny.cpp` eivät käänny sellaisinaan mutta
  kääntyvät makrolla `-DKORJATTU`, jolla virheellinen kohta poistetaan,
- rivit ovat enintään 78 merkkiä pitkiä,
- jokaista esimerkkiä käytetään tekstissä.
