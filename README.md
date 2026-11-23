# Tutoriaalit

Suomenkielisiä tutoriaaleja eri aiheista. Tutoriaalit kirjoitetaan
Markdownilla, ja lopullinen versio on PDF-dokumentti.

Tutoriaalit muodostavat **taitopuun**: jokainen tutoriaali on yksi
taito, joka rakentuu esitietojensa päälle. Roolit, kuten
laitteistoarkkitehti tai sulautettujen ohjelmistojen kehittäjä, ovat
polkuja puun läpi. Taitopuu, roolipolut ja tutoriaalien
tuotantojärjestys ovat hakemistossa [`opintopolut/`](opintopolut/)
([opintopolut.pdf](opintopolut/opintopolut.pdf)).

**Taitopuukartta** ([`sivusto/`](sivusto/)) on interaktiivinen
verkkosivu, jolla taitopuuta voi tutkia: roolipolun voi valita
yläpalkista, taidon voi lisätä polulle kaikkine esitietoineen, ja
valmiiden taitojen kohdalta avautuvat tutoriaalin PDF, esimerkit
kehityskontteineen ja Codespaces. Polun voi jakaa linkkinä. Sivusto
julkaistaan GitHub Pagesiin `main`-haarasta.

Kartalla kunkin alueen taidot muodostavat *nipun*: ne ovat kiertoradalla
nipun keskipisteen ympärillä, ja toisiaan edellyttävät taidot ovat
radalla vierekkäin. Nippujen paikat lasketaan selaimessa
voimasimulaatiolla (`sivusto/asettelu.js`), ja nippuja voi raahata.
Nippujen väliset yhteydet kulkevat yhteisinä johdinnippuina, jotka
kiertävät muut niput. Taidolle voi antaa taitopuussa kentän `nippu`,
jos alue halutaan jakaa useampaan nippuun.

| Tutoriaali | Hakemisto | PDF |
|------------|-----------|-----|
| Moderni C++ | [`moderni-cpp/`](moderni-cpp/) | [moderni-cpp.pdf](moderni-cpp/moderni-cpp.pdf) |
| C-kieli | [`c-kieli/`](c-kieli/) | [c-kieli.pdf](c-kieli/c-kieli.pdf) |
| Opintopolut (taitopuu) | [`opintopolut/`](opintopolut/) | [opintopolut.pdf](opintopolut/opintopolut.pdf) |

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

## Esimerkit kehityskontissa

Jokaisen tutoriaalin esimerkeille on valmis kehityskontti
(devcontainer), jossa on kääntäjät (GCC 14, Clang 20), sanitoijat ja
debuggeri:

- **GitHub Codespaces:** *Code → Codespaces → New with options* ja
  valitse konfiguraatio, esimerkiksi *C-kieli: esimerkit*.
- **Visual Studio Code:** avaa repositorio ja valitse
  *Dev Containers: Reopen in Container*.
- **Ilman repositoriota:** taitopuukartalta saa kunkin tutoriaalin
  esimerkit zip-pakettina, jossa on mukana oma kehityskontti.

Kontin sisällä tai ilman konttia esimerkit käännetään esimerkkihakemiston
Makefilellä: `make` kääntää kaikki, `make aja-01-hei` kääntää ja ajaa
yhden ja `make virhe-02-etumerkki` näyttää tarkoituksella virheellisen
esimerkin käännösvirheen.

Konfiguraatiot ovat hakemistossa `.devcontainer/`: yhteinen `Dockerfile`
sekä tutoriaalikohtaiset `devcontainer.json`-tiedostot. Konfiguraatio
*Tutoriaalien kirjoittaminen* sisältää lisäksi pandocin, XeLaTeXin ja
Graphvizin PDF:ien rakentamiseen.

## Rakenne

```text
yhteiset/                 kaikille tutoriaaleille yhteiset työkalut
  pdf.yaml                pandocin PDF-asetukset
  tyyli.tex               PDF:n LaTeX-tyylit
  sisallyta.lua           pandoc-suodatin koodin sisällyttämiseen
  testaa_esimerkit.py     esimerkkikoodin testaaja
  taitopuu.py             taitopuun tarkistin ja generaattori
  sivusto.py              taitopuukartan rakentaja
opintopolut/
  taitopuu.toml           taitopuu: alueet, taidot ja roolit
sivusto/                  taitopuukartta (HTML, CSS, JS, asettelu ja selaintesti)
.devcontainer/            kehityskontit esimerkeille ja kirjoittamiselle
<tutoriaali>/
  Makefile                make testaa / make pdf / make
  metadata.yaml           otsikko, päiväys yms.
  luvut/NN-nimi.md        luvut järjestyksessä
  esimerkit/              koodiesimerkit, odotetut tulosteet ja syötteet
                          sekä Makefile niiden kääntämiseen
  <tutoriaali>.pdf        valmis PDF
```

## Rakentaminen

Tarvittavat ohjelmat (Ubuntu 24.04):

```text
sudo apt install make python3 pandoc g++-14 clang-20 libclang-rt-20-dev \
    texlive-xetex texlive-latex-recommended texlive-latex-extra \
    texlive-fonts-recommended texlive-lang-european lmodern fonts-dejavu \
    graphviz
```

Juurihakemistossa `make` testaa ja rakentaa kaikki tutoriaalit.
Tutoriaalin omassa hakemistossa:

```text
make testaa   # kääntää, ajaa ja tarkistaa esimerkit
make pdf      # rakentaa PDF:n
make          # molemmat
```

Taitopuukartan selaintestit tarvitsevat Playwrightin
(`npm install playwright`); ilman sitä ne ohitetaan. `make -C sivusto
palvele` käynnistää kartan paikallisesti osoitteeseen
<http://localhost:8000>.

GitHub Actions ajaa testit, rakentaa PDF:t ja sivuston, testaa
esimerkit kehityskontissa ja julkaisee sivuston GitHub Pagesiin
(`.github/workflows/tutoriaalit.yml`). Julkaisua varten repositorion
asetuksista on valittava *Pages → Source: GitHub Actions*.

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

Ohjelman syöte voidaan antaa tiedostossa `<nimi>.syote` ja
komentoriviargumentit tiedostossa `<nimi>.argumentit` (yksi per rivi).
Ohjelma ajetaan tyhjässä väliaikaisessa hakemistossa, joten se saa
luoda tiedostoja. Monen tiedoston esimerkki on hakemisto
`esimerkit/<nimi>/`, jonka lähdetiedostot käännetään yhdeksi ohjelmaksi.

Testaaja (`yhteiset/testaa_esimerkit.py --kieli c|cpp`) tarkistaa, että

- jokainen C- ja C++-koodilohko viittaa tiedostoon (käsin kirjoitettua
  koodia ei sallita),
- jokainen esimerkki kääntyy GCC:llä ja Clangilla varoitukset virheinä
  (`-Wall -Wextra -Wpedantic -Werror`, C++23 tai C23),
- ohjelma toimii AddressSanitizerin ja UndefinedBehaviorSanitizerin
  kanssa, ja rivin `// TSAN` sisältävät myös ThreadSanitizerin kanssa,
- ohjelman tuloste vastaa tiedostoa `<nimi>.odotettu`,
- tiedostot `<nimi>.ei-kaanny.cpp` (`.c`) eivät käänny sellaisinaan
  mutta kääntyvät makrolla `-DKORJATTU`, jolla virheellinen kohta
  poistetaan,
- tiedostot `<nimi>.kaatuu.cpp` (`.c`) kaatuvat sanitoijan havaitsemaan
  virheeseen, ja virheilmoitus sisältää tiedoston `<nimi>.virhe` rivit,
- rivit ovat enintään 78 merkkiä pitkiä,
- jokaista esimerkkiä käytetään tekstissä.
