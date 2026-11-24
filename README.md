# Tutoriaalit

Avoin, suomenkielinen oppimateriaalikokonaisuus tekniikan osaajille:
opiskelijoille, alaa vaihtaville ja syventäville ammattilaisille sekä
tiiminvetäjille. Projektin tavoitteet, kohderyhmät ja periaatteet on
kuvattu dokumentissa **[VISIO.md](VISIO.md)**.

Kokonaisuus koostuu kolmesta osasta:

- **Taitopuu** kertoo, mikä taito mahdollistaa minkäkin ja mitä on
  hallittava ensin.
- **Roolit** ovat taitopuun osajoukkoja: kunkin roolin
  osaamisvaatimukset, esimerkiksi laitteistoarkkitehdille tai
  sulautettujen ohjelmistojen kehittäjälle.
- **Tutoriaalipaketit** opettavat taidot. Jokaisessa on PDF, testatut
  esimerkit ja valmis kehityskontti.

Taitopuu, roolipolut ja tutoriaalien tuotantojärjestys ovat hakemistossa
[`opintopolut/`](opintopolut/)
([opintopolut.pdf](https://saperant.github.io/tutoriaalit/materiaalit/opintopolut.pdf)).

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

Jokaisessa tutoriaalissa on lisäksi muutaman sivun pikaopas
(`<paketti>-pikaopas.pdf`) kokeneelle lukijalle. PDF:t eivät ole
versionhallinnassa: CI rakentaa ne jokaisesta muutoksesta ja julkaisee
ne taitopuukartan sivustolla. Paikallisesti PDF rakennetaan komennolla
`make -C <paketti> pdf`.

| Tutoriaali | Hakemisto | PDF |
|------------|-----------|-----|
| Ohjelmoinnin perusteet (Python) | [`ohjelmoinnin-perusteet/`](ohjelmoinnin-perusteet/) | [ohjelmoinnin-perusteet.pdf](https://saperant.github.io/tutoriaalit/materiaalit/ohjelmoinnin-perusteet.pdf) |
| Moderni C++ | [`moderni-cpp/`](moderni-cpp/) | [moderni-cpp.pdf](https://saperant.github.io/tutoriaalit/materiaalit/moderni-cpp.pdf) |
| C-kieli | [`c-kieli/`](c-kieli/) | [c-kieli.pdf](https://saperant.github.io/tutoriaalit/materiaalit/c-kieli.pdf) |
| Komentorivi ja Linux | [`komentorivi/`](komentorivi/) | [komentorivi.pdf](https://saperant.github.io/tutoriaalit/materiaalit/komentorivi.pdf) |
| Python | [`python/`](python/) | [python.pdf](https://saperant.github.io/tutoriaalit/materiaalit/python.pdf) |
| Bash-skriptaus | [`bash/`](bash/) | [bash.pdf](https://saperant.github.io/tutoriaalit/materiaalit/bash.pdf) |
| Rust | [`rust/`](rust/) | [rust.pdf](https://saperant.github.io/tutoriaalit/materiaalit/rust.pdf) |
| Java | [`java/`](java/) | [java.pdf](https://saperant.github.io/tutoriaalit/materiaalit/java.pdf) |
| Kotlin | [`kotlin/`](kotlin/) | [kotlin.pdf](https://saperant.github.io/tutoriaalit/materiaalit/kotlin.pdf) |
| JavaScript | [`javascript/`](javascript/) | [javascript.pdf](https://saperant.github.io/tutoriaalit/materiaalit/javascript.pdf) |
| TypeScript | [`typescript/`](typescript/) | [typescript.pdf](https://saperant.github.io/tutoriaalit/materiaalit/typescript.pdf) |
| Go | [`go/`](go/) | [go.pdf](https://saperant.github.io/tutoriaalit/materiaalit/go.pdf) |
| Tcl | [`tcl/`](tcl/) | [tcl.pdf](https://saperant.github.io/tutoriaalit/materiaalit/tcl.pdf) |
| HTML ja CSS | [`html-css/`](html-css/) | [html-css.pdf](https://saperant.github.io/tutoriaalit/materiaalit/html-css.pdf) |
| SQL ja relaatiotietokannat | [`sql/`](sql/) | [sql.pdf](https://saperant.github.io/tutoriaalit/materiaalit/sql.pdf) |
| Funktionaalinen ohjelmointi (Racket) | [`funktionaalinen-ohjelmointi/`](funktionaalinen-ohjelmointi/) | [funktionaalinen-ohjelmointi.pdf](https://saperant.github.io/tutoriaalit/materiaalit/funktionaalinen-ohjelmointi.pdf) |
| Web-sovellukset | [`web-sovellukset/`](web-sovellukset/) | [web-sovellukset.pdf](https://saperant.github.io/tutoriaalit/materiaalit/web-sovellukset.pdf) |
| Taustapalvelut | [`taustapalvelut/`](taustapalvelut/) | [taustapalvelut.pdf](https://saperant.github.io/tutoriaalit/materiaalit/taustapalvelut.pdf) |
| Android-sovellukset | [`android-sovellukset/`](android-sovellukset/) | [android-sovellukset.pdf](https://saperant.github.io/tutoriaalit/materiaalit/android-sovellukset.pdf) |
| Tietoturvan perusteet | [`tietoturvan-perusteet/`](tietoturvan-perusteet/) | [tietoturvan-perusteet.pdf](https://saperant.github.io/tutoriaalit/materiaalit/tietoturvan-perusteet.pdf) |
| Kryptografia | [`kryptografia/`](kryptografia/) | [kryptografia.pdf](https://saperant.github.io/tutoriaalit/materiaalit/kryptografia.pdf) |
| Miten tietokone laskee | [`tietokonearitmetiikka/`](tietokonearitmetiikka/) | [tietokonearitmetiikka.pdf](https://saperant.github.io/tutoriaalit/materiaalit/tietokonearitmetiikka.pdf) |
| Virtualisointi | [`virtualisointi/`](virtualisointi/) | [virtualisointi.pdf](https://saperant.github.io/tutoriaalit/materiaalit/virtualisointi.pdf) |
| Kontit ja pilvi | [`kontit-ja-pilvi/`](kontit-ja-pilvi/) | [kontit-ja-pilvi.pdf](https://saperant.github.io/tutoriaalit/materiaalit/kontit-ja-pilvi.pdf) |
| Palvelinympäristöt | [`palvelinymparistot/`](palvelinymparistot/) | [palvelinymparistot.pdf](https://saperant.github.io/tutoriaalit/materiaalit/palvelinymparistot.pdf) |
| Tietoverkot | [`tietoverkot/`](tietoverkot/) | [tietoverkot.pdf](https://saperant.github.io/tutoriaalit/materiaalit/tietoverkot.pdf) |
| Verkkoinfrastruktuuri | [`verkkoinfrastruktuuri/`](verkkoinfrastruktuuri/) | [verkkoinfrastruktuuri.pdf](https://saperant.github.io/tutoriaalit/materiaalit/verkkoinfrastruktuuri.pdf) |
| Tietoliikennetekniikka | [`tietoliikennetekniikka/`](tietoliikennetekniikka/) | [tietoliikennetekniikka.pdf](https://saperant.github.io/tutoriaalit/materiaalit/tietoliikennetekniikka.pdf) |
| Palveluarkkitehtuurit | [`palveluarkkitehtuurit/`](palveluarkkitehtuurit/) | [palveluarkkitehtuurit.pdf](https://saperant.github.io/tutoriaalit/materiaalit/palveluarkkitehtuurit.pdf) |
| Palveluarkkitehtuurin tietoturva | [`palvelutietoturva/`](palvelutietoturva/) | [palvelutietoturva.pdf](https://saperant.github.io/tutoriaalit/materiaalit/palvelutietoturva.pdf) |
| Sulautettujen järjestelmien tietoturva | [`sulautettujen-tietoturva/`](sulautettujen-tietoturva/) | [sulautettujen-tietoturva.pdf](https://saperant.github.io/tutoriaalit/materiaalit/sulautettujen-tietoturva.pdf) |
| Tietoturva kehitystyössä | [`turvallinen-kehitys/`](turvallinen-kehitys/) | [turvallinen-kehitys.pdf](https://saperant.github.io/tutoriaalit/materiaalit/turvallinen-kehitys.pdf) |
| Web-sovellusten tietoturva | [`web-tietoturva/`](web-tietoturva/) | [web-tietoturva.pdf](https://saperant.github.io/tutoriaalit/materiaalit/web-tietoturva.pdf) |
| Digitaalitekniikka | [`digitaalitekniikka/`](digitaalitekniikka/) | [digitaalitekniikka.pdf](https://saperant.github.io/tutoriaalit/materiaalit/digitaalitekniikka.pdf) |
| SoC-integraatio | [`soc-integraatio/`](soc-integraatio/) | [soc-integraatio.pdf](https://saperant.github.io/tutoriaalit/materiaalit/soc-integraatio.pdf) |
| ASIC-toteutus | [`asic-toteutus/`](asic-toteutus/) | [asic-toteutus.pdf](https://saperant.github.io/tutoriaalit/materiaalit/asic-toteutus.pdf) |
| GPU-ohjelmointi: OpenGL ja Vulkan | [`gpu-ohjelmointi/`](gpu-ohjelmointi/) | [gpu-ohjelmointi.pdf](https://saperant.github.io/tutoriaalit/materiaalit/gpu-ohjelmointi.pdf) |
| Peliohjelmointi | [`peliohjelmointi/`](peliohjelmointi/) | [peliohjelmointi.pdf](https://saperant.github.io/tutoriaalit/materiaalit/peliohjelmointi.pdf) |
| Reaaliaikaiset moninpelit | [`moninpelit/`](moninpelit/) | [moninpelit.pdf](https://saperant.github.io/tutoriaalit/materiaalit/moninpelit.pdf) |
| RTL-suunnittelu (SystemVerilog) | [`rtl-suunnittelu/`](rtl-suunnittelu/) | [rtl-suunnittelu.pdf](https://saperant.github.io/tutoriaalit/materiaalit/rtl-suunnittelu.pdf) |
| RTL-suunnittelu VHDL:llä | [`vhdl/`](vhdl/) | [vhdl.pdf](https://saperant.github.io/tutoriaalit/materiaalit/vhdl.pdf) |
| Versionhallinta (Git) | [`versionhallinta/`](versionhallinta/) | [versionhallinta.pdf](https://saperant.github.io/tutoriaalit/materiaalit/versionhallinta.pdf) |
| Lukujen esitys ja kiinteän pilkun aritmetiikka | [`kiintea-pilkku/`](kiintea-pilkku/) | [kiintea-pilkku.pdf](https://saperant.github.io/tutoriaalit/materiaalit/kiintea-pilkku.pdf) |
| Diskreetti matematiikka | [`diskreetti-matematiikka/`](diskreetti-matematiikka/) | [diskreetti-matematiikka.pdf](https://saperant.github.io/tutoriaalit/materiaalit/diskreetti-matematiikka.pdf) |
| Python työkaluohjelmointiin | [`python-tyokalut/`](python-tyokalut/) | [python-tyokalut.pdf](https://saperant.github.io/tutoriaalit/materiaalit/python-tyokalut.pdf) |
| Lineaarialgebra | [`lineaarialgebra/`](lineaarialgebra/) | [lineaarialgebra.pdf](https://saperant.github.io/tutoriaalit/materiaalit/lineaarialgebra.pdf) |
| Assembly | [`assembly/`](assembly/) | [assembly.pdf](https://saperant.github.io/tutoriaalit/materiaalit/assembly.pdf) |
| Todennäköisyys ja tilastot | [`todennakoisyys/`](todennakoisyys/) | [todennakoisyys.pdf](https://saperant.github.io/tutoriaalit/materiaalit/todennakoisyys.pdf) |
| FPGA-toteutus | [`fpga-toteutus/`](fpga-toteutus/) | [fpga-toteutus.pdf](https://saperant.github.io/tutoriaalit/materiaalit/fpga-toteutus.pdf) |
| Tietorakenteet | [`tietorakenteet/`](tietorakenteet/) | [tietorakenteet.pdf](https://saperant.github.io/tutoriaalit/materiaalit/tietorakenteet.pdf) |
| Käännösjärjestelmät, testaus ja CI | [`rakennus-ja-testaus/`](rakennus-ja-testaus/) | [rakennus-ja-testaus.pdf](https://saperant.github.io/tutoriaalit/materiaalit/rakennus-ja-testaus.pdf) |
| Python ja C/C++ yhteen | [`python-c-integraatio/`](python-c-integraatio/) | [python-c-integraatio.pdf](https://saperant.github.io/tutoriaalit/materiaalit/python-c-integraatio.pdf) |
| C ja assembly yhteen | [`c-asm-integraatio/`](c-asm-integraatio/) | [c-asm-integraatio.pdf](https://saperant.github.io/tutoriaalit/materiaalit/c-asm-integraatio.pdf) |
| Objektitiedostot, linkitys ja ABI | [`binaarit-ja-linkitys/`](binaarit-ja-linkitys/) | [binaarit-ja-linkitys.pdf](https://saperant.github.io/tutoriaalit/materiaalit/binaarit-ja-linkitys.pdf) |
| Tietokonearkkitehtuuri | [`tietokonearkkitehtuuri/`](tietokonearkkitehtuuri/) | [tietokonearkkitehtuuri.pdf](https://saperant.github.io/tutoriaalit/materiaalit/tietokonearkkitehtuuri.pdf) |
| Laitteiston verifiointi | [`verifiointi/`](verifiointi/) | [verifiointi.pdf](https://saperant.github.io/tutoriaalit/materiaalit/verifiointi.pdf) |
| Algoritmit ja tietorakenteet | [`algoritmit/`](algoritmit/) | [algoritmit.pdf](https://saperant.github.io/tutoriaalit/materiaalit/algoritmit.pdf) |
| Opintopolut (taitopuu) | [`opintopolut/`](opintopolut/) | [opintopolut.pdf](https://saperant.github.io/tutoriaalit/materiaalit/opintopolut.pdf) |

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
(devcontainer), jossa on tutoriaalin työkalut: esimerkiksi C:lle ja
C++:lle GCC 14, Clang 20, sanitoijat ja debuggeri, Pythonille ruff,
mypy ja pytest ja Rustille rustc, Cargo ja Clippy. Kontin voi avata
näin:

- **GitHub Codespaces:** *Code → Codespaces → New with options* ja
  valitse konfiguraatio, esimerkiksi *C-kieli: esimerkit*.
- **Visual Studio Code:** avaa repositorio ja valitse
  *Dev Containers: Reopen in Container*.
- **Ilman repositoriota:** taitopuukartalta saa kunkin tutoriaalin
  esimerkit zip-pakettina, jossa on mukana oma kehityskontti.

Kontissa `make -C <paketti> testaa` tarkistaa ja ajaa paketin kaikki
esimerkit samoin kuin CI. C- ja C++-esimerkit voi kääntää myös
esimerkkihakemiston Makefilellä: `make` kääntää kaikki, `make aja-01-hei` kääntää ja ajaa
yhden ja `make virhe-03-etumerkki` näyttää tarkoituksella virheellisen
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
  KIELIPAKETTI.md         kielipakettien yhteinen runko ja säännöt
  tarkista_paketti.py     kielipaketin rakenteen tarkistin
  pikaopas.yaml           pikaoppaiden (kaksipalstainen PDF) asetukset
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
  pikaopas.md             kielipaketin pikaopas kokeneelle
  <tutoriaali>.pdf        valmis PDF (ja <tutoriaali>-pikaopas.pdf)
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
