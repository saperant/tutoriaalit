# Suorituskyky ja C++

Konenäkö käsittelee paljon dataa: yksi 1080p-kuva on kaksi miljoonaa
pikseliä, ja 30 kuvaa sekunnissa tarkoittaa yli 60 miljoonaa pikseliä
sekunnissa. Python on silti konenäön tavallisin kieli, koska raskas
laskenta tapahtuu OpenCV:n C++-koodissa. Tässä luvussa katsotaan, mikä
Pythonissa on kallista, miltä sama ohjelma näyttää C++:lla ja milloin
C++:aan kannattaa siirtyä. Yleiset mittaamisen periaatteet ovat taidossa
*Suorituskyvyn analyysi ja optimointi*.

## Mikä on kallista

Pythonin tulkki käsittelee jokaisen operaation erikseen: tyyppien
tarkistus, olioiden luonti ja viittauslaskenta maksavat kymmeniä
nanosekunteja operaatiota kohden. Kun silmukka käy läpi kuvan pikselit,
hinta maksetaan jokaisesta pikselistä. NumPy ja OpenCV tekevät saman
työn yhdellä kutsulla, ja silmukka pyörii käännetyssä koodissa.

Esimerkki laskee $3 \times 3$ -keskiarvon kolmella tavalla: Pythonin
silmukoilla, NumPyn siirretyillä näkymillä ja OpenCV:n `blur`-funktiolla.
Kaksi ensimmäistä tuottavat täsmälleen saman tuloksen. OpenCV pyöristää
jakolaskun eri tavalla, joten sitä ei verrata bitilleen.

```{.python tiedosto="esimerkit/10-reunat.py" osa="hinnat"}
```

Ajat mitataan vain, kun ohjelmalle annetaan argumentti `--mittaa`,
koska ne vaihtelevat koneittain eikä niitä voi verrata testissä.
Kirjoittajan koneella $160 \times 120$ -kuvalle (suuntaa-antavat luvut,
kuormitettu kone):

| Toteutus | Aika | Suhde OpenCV:hen |
|----------|------|------------------|
| Pythonin silmukka | 45 ms | noin 600-kertainen |
| NumPy | 0,17 ms | noin 2-kertainen |
| OpenCV `blur` | 0,07 ms | 1 |

Johtopäätös: **pikselisilmukka Pythonissa on lähes aina virhe**.
Vektoroitu NumPy on lähellä OpenCV:tä, ja OpenCV on vielä nopeampi,
koska se käyttää SIMD-käskyjä ja erottuvaa ydintä.

## Sama ketju C++:lla

Kun ketju koostuu OpenCV-kutsuista, Python ja C++ ajavat samaa
käännettyä koodia, ja ero jää pieneksi. Esimerkin reunaketju on
tasoitus, Canny ja yhtenäiset reunakäyrät, ja sama ohjelma on
kirjoitettu molemmilla kielillä.

```{.python tiedosto="esimerkit/10-reunat.py" osa="ketju"}
```

```{.tuloste tiedosto="esimerkit/10-reunat.odotettu"}
```

C++-versio käyttää samoja funktioita. Kuva on `cv::Mat`, joka on
viitelaskettu otsake datapuskuriin: kopiointi kopioi vain otsakkeen, ja
`clone()` kopioi datan. Funktioiden parametrit ovat tyyppiä
`cv::InputArray` ja `cv::OutputArray`, jotka hyväksyvät `Mat`:n,
`std::vector`:n ja muut taulukot.

```{.cpp tiedosto="esimerkit/cpp/reunat.cpp" osa="kuva"}
```

```{.cpp tiedosto="esimerkit/cpp/reunat.cpp" osa="ketju"}
```

```{.cpp tiedosto="esimerkit/cpp/reunat.cpp" osa="paa"}
```

```{.tuloste tiedosto="esimerkit/cpp/reunat.odotettu"}
```

Molemmat versiot löytävät 1 704 reunapikseliä ja 12 reunakäyrää, vaikka
Python-paketti on OpenCV 5.1 ja C++ käyttää Ubuntun OpenCV 4.6:ta.
Esimerkkien Makefile kääntää C++-ohjelman GCC:llä ja Clangilla
osoite- ja määrittelemättömän käytöksen sanitoijien kanssa ja vertaa
tulosteen tallennettuun. OpenCV:n otsakkeet otetaan mukaan
`-isystem`-polulla, koska vanhemman OpenCV:n otsakkeet tuottavat
C++20-kääntäjällä varoituksia, joita ei voi korjata omassa koodissa:

```text
g++ -std=c++20 -Wall -Wextra -Werror reunat.cpp \
    $(pkg-config --cflags opencv4 | sed 's/-I/-isystem /') \
    $(pkg-config --libs opencv4)
```

Kirjoittajan koneella ($640 \times 480$, yksi säie, suuntaa-antava)
ketju kesti C++:lla noin 0,8 ms ja Pythonilla noin 1,0 ms. Ero on
kutsujen ja tyyppimuunnosten hinta, ei laskennan. **C++ kannattaa, kun
ketjussa on omaa pikselitason logiikkaa**, kun viive on kriittinen
(yksittäiset millisekunnit robotin ohjauksessa), tai kun ohjelma ajetaan
sulautetussa laitteessa ilman Python-tulkkia.

## Säikeet, SIMD ja kiihdytys

OpenCV rinnakkaistaa monet funktiot itse ja valitsee ajonaikaisesti
suorittimen parhaat SIMD-käskyt. Kaksi seurausta on tärkeää tietää.
Ensinnäkin mittaus on toistettavampi yhdellä säikeellä
(`cv2.setNumThreads(1)`), ja moniajossa (esimerkiksi monta kameraa omissa
prosesseissaan) OpenCV:n omat säikeet kilpailevat prosessien kanssa.
Toiseksi liukulukutulokset voivat erota viimeisissä biteissä eri
suorittimilla, koska käskyt ja summausjärjestys vaihtelevat. Siksi
tämän tutoriaalin testit vertaavat liukulukuja toleranssilla.

Grafiikkasuorittimella kiihdyttämiseen OpenCV tarjoaa `UMat`-tyypin, joka
ajaa funktiot OpenCL:llä läpinäkyvästi, sekä CUDA-modulit lisämoduleissa.
Siirto suorittimen ja grafiikkasuorittimen välillä maksaa, joten kiihdytys
kannattaa vain, kun koko ketju pysyy grafiikkasuorittimella. Taito
*GPU-laskenta* käsittelee aihetta yleisesti.

## Käytännössä

- **Ei pikselisilmukoita Pythonissa.** Vektoroi NumPylla tai käytä
  OpenCV:n funktiota. Jos omaa pikselilogiikkaa on pakko olla,
  kirjoita se C++:lla (taito *Python ja C/C++ yhteen*) tai Numballa.
- **Mittaa ennen siirtoa C++:aan.** Kun ketju on OpenCV-kutsuja, Python
  ei yleensä ole pullonkaula. Profiloi, mikä kutsu vie ajan.
- **Vältä turhia kopioita ja tyyppimuunnoksia.** Työskentele näkymillä,
  anna `dst`-parametri uudelleenkäyttöön silmukoissa, ja pysy samassa
  tyypissä koko ketjun ajan.
- **Pienennä ensin.** Monet analyysit toimivat puolikkaalla tai
  neljäsosakuvalla, ja työ pienenee neliössä. Pyramidi antaa karkean
  tuloksen nopeasti ja tarkennuksen vain tarvittaessa.
- **Kiinnitä säikeet ja käännä varoitukset virheiksi.** C++:ssa
  sanitoijat löytävät `Mat`-indeksoinnin ja elinaikojen virheet, jotka
  muuten kaatavat ohjelman vasta tuotannossa.

## Itsearviointi

- Osaat selittää, miksi Pythonin pikselisilmukka on satoja kertoja
  hitaampi kuin vektoroitu koodi, ja kirjoittaa saman vektoroituna.
- Osaat kirjoittaa saman OpenCV-ketjun C++:lla ja kääntää sen
  pkg-configilla, varoitukset virheinä ja sanitoijien kanssa.
- Osaat selittää `cv::Mat`-tyypin viitelasketun datan ja `clone()`-kutsun
  eron.
- Osaat arvioida, milloin C++ tai grafiikkasuoritin kannattaa, ja miksi
  liukulukutulokset voivat erota koneittain.
