# Vektorointi ja SIMD

SIMD-käsky (engl. *single instruction, multiple data*) tekee saman
operaation usealle luvulle kerralla. x86-64:n SSE2-rekisteri on 128
bittiä eli neljä `float`-lukua, AVX2:n 256 bittiä ja AVX-512:n 512
bittiä; ARMin vastaavat ovat NEON (128 bittiä) ja SVE. Kahdeksan luvun
vektorikäsky maksaa saman verran kuin skalaarikäsky, joten
vektoroitu silmukka voi olla moninkertaisesti nopeampi. Useimmiten
vektoroinnin tekee kääntäjä, ja ohjelmoijan tehtävä on kirjoittaa
silmukat niin, että kääntäjä pystyy siihen.

## Automaattinen vektorointi

GCC vektoroi silmukoita tasolla `-O3` ja rajoitetusti myös tasolla
`-O2` (versiosta 12 alkaen), Clang tasolta `-O2` alkaen. Lippu
`-fopt-info-vec-optimized` (GCC) tai `-Rpass=loop-vectorize`
(Clang) kertoo, mitkä silmukat vektoroitiin, ja
`-fopt-info-vec-missed` miksi muut jäivät vektoroimatta.

```{.makefile tiedosto="esimerkit/Makefile" osa="vektorointi"}
```

Esimerkkitiedostossa on neljä silmukkaa. Ensimmäiset kaksi laskevat
BLAS-kirjaston *saxpy*-operaation $y = ax + y$:

```{.c tiedosto="esimerkit/08-vektorointi.c" osa="saxpy"}
```

```{.tuloste tiedosto="esimerkit/tulokset/tarkista-vektorointi.txt"}
```

Rivin 14 silmukka (ilman `restrict`-sanaa) vektoroitiin, mutta
*versioituna*: kääntäjä tuotti kaksi versiota ja tarkistuksen, joka
valitsee vektoroidun vain, jos taulukot eivät ole päällekkäin. Syy on
aliasing: C sallii, että `y` ja `x` osoittavat samaan muistiin, jolloin
silmukan kierros voi lukea edellisen kierroksen tuloksen. Esimerkki
näyttää, että ero on todellinen:

```{.c tiedosto="esimerkit/08-vektorointi.c" osa="paallekkain"}
```

```{.tuloste tiedosto="esimerkit/08-vektorointi.odotettu"}
```

Kun `y` alkaa yhden alkion `x`:n jälkeen, jokainen kierros käyttää
edellisen kierroksen kirjoittamaa arvoa, ja tulos on 1, 2, 3, ...
Vektoroitu versio lukisi neljä vanhaa arvoa kerralla ja antaisi eri
tuloksen. `restrict` on ohjelmoijan lupaus, että osoittimien kautta
käsitellyt alueet eivät ole päällekkäin. Silloin tarkistusta ei
tarvita. Lupauksen rikkominen on määrittelemätöntä käyttäytymistä,
jota sanitoijat eivät havaitse.

Tässä mittauksessa tarkistus oli halpa, ja molemmat versiot olivat
yhtä nopeita tasolla `-O3`:

```{.tuloste tiedosto="esimerkit/tulokset/08-vektorointi-O3.txt"}
```

`restrict` on tärkeämpi, kun osoittimia on monta (tarkistuksia
kasvaa neliöllisesti), kun silmukka on lyhyt (tarkistus maksaa
suhteessa enemmän) tai kun kääntäjä luopuu versioinnista
kokonaan. Optimointitaso ratkaisee myös paljon: tasolla `-O2` GCC 14
käyttää kevyttä kustannusmallia eikä vektoroinut kumpaakaan
saxpy-silmukkaa, vain kokonaislukusumman, ja `-O2`-käännöksen
saxpy-kutsut kestivät kirjoittajan koneella noin kuusi kertaa
kauemmin kuin yllä.

## Liukulukujen järjestys

Kokonaislukujen summa vektoroituu ongelmitta: neljä osasummaa
lasketaan rinnakkain ja yhdistetään lopuksi. Liukulukujen summa ei
ole liitännäinen, eli $(a + b) + c$ voi poiketa luvusta $a + (b + c)$
pyöristyksen vuoksi:

```{.c tiedosto="esimerkit/08-vektorointi.c" osa="summat"}
```

```{.c tiedosto="esimerkit/08-vektorointi.c" osa="jarjestys"}
```

Harmonisen sarjan tuhannen termin summa eroaa viimeisissä numeroissa,
kun se lasketaan kahdeksana osasummana. Kääntäjä ei saa muuttaa
tulosta, joten se ei saa jakaa summaa osasummiin. Raportin mukaan
rivin 47 silmukka silti ”vektoroitiin”, mutta konekoodista näkyy, mitä
se tarkoittaa:

```{.tuloste tiedosto="esimerkit/tulokset/tarkista-konekoodi.txt"}
```

Luvut ladataan neljän ryhmissä, mutta ne lisätään yksi kerrallaan
skalaarikäskyllä `addss` samaan rekisteriin. Jokainen yhteenlasku
odottaa edellistä, joten silmukan nopeuden määrää yhteenlaskun viive
(neljä jaksoa) eikä sen läpäisy. Kahdeksan osasumman versio tekee
kahdeksan riippumatonta ketjua, ja se oli edellisen mittauksen
alaosassa kahdeksan kertaa nopeampi. Ero tulee samoista käskyistä
eri riippuvuuksin.
Kääntäjän saa jakamaan summan itse lipulla `-fassociative-math` tai
laajemmalla `-ffast-math`. Jälkimmäinen sallii myös oletuksen, ettei
`NaN`- ja äärettömiä arvoja esiinny, ja muuttaa siten esimerkiksi
`isnan`-tarkistusten tuloksia. Turvallisempi tapa on kirjoittaa
osasummat itse, kuten yllä, tai käyttää OpenMP:n
`#pragma omp simd reduction(+:s)` -direktiiviä, joka antaa luvan vain
yhdelle silmukalle.

## Mikä estää vektoroinnin

| Este | Esimerkki | Korjaus |
|------------------------|------------------------|----------------------------|
| Mahdollinen aliasing | Kaksi osoitinparametria | `restrict`, paikalliset kopiot |
| Silmukan kierrosten riippuvuus | `a[i] = a[i-1] + x` | Algoritmin muutos (esim. etuliitesumma lohkoittain) |
| Liukulukujen järjestys | Summa, tulo, minimi | Omat osasummat, `-fassociative-math` |
| Funktiokutsu silmukassa | Toisen käännösyksikön funktio | `static inline`, LTO (luku 9) |
| Ehto silmukan sisällä | `if (a[i] > 0) ...` | Usein kääntäjä tekee maskin itse |
| Hajanaiset osoitteet | `a[indeksi[i]]`, AoS-kenttä | SoA (luku 6); AVX2:ssa gather-käsky |
| Tuntematon kierrosmäärä tai poistuminen | `while`-silmukka, `break` | Laske pituus ensin |

## SIMD-intrinsicsit

Kun kääntäjä ei vektoroi, käskyjä voi käyttää suoraan
*intrinsics*-funktioilla, jotka vastaavat yksittäisiä konekäskyjä.
Pistetulo viitetoteutuksena ja SSE2:lla, joka kuuluu jokaiseen
x86-64-suorittimeen:

```{.c tiedosto="esimerkit/08-simd.c" osa="skalaari"}
```

```{.c tiedosto="esimerkit/08-simd.c" osa="sse2"}
```

`_mm_loadu_ps` lataa neljä lukua tasaamattomasta osoitteesta.
Nykysuorittimilla se on yhtä nopea kuin tasattu lataus, kun osoite
sattuu olemaan tasattu. Silmukan lopussa käsitellään jäljelle jäävät
alle neljä alkiota skalaarina. AVX2-versio on samanlainen kahdeksalla
luvulla, mutta AVX2 ei ole kaikissa x86-64-suorittimissa. Funktio
käännetään AVX2-käskyillä `target`-attribuutilla, ja ohjelma valitsee
toteutuksen ajon aikana:

```{.c tiedosto="esimerkit/08-simd.c" osa="avx2"}
```

```{.c tiedosto="esimerkit/08-simd.c" osa="valinta"}
```

Näin sama ohjelmatiedosto toimii vanhassa suorittimessa SSE2:lla ja
käyttää uudemman koneen AVX2:ta. Tätä *ajonaikaista valintaa* (engl.
dispatch) käyttävät glibcin `memcpy` ja `strlen`, joista Callgrind näytti
luvussa 4 nimen `__strlen_avx2`. Testi käyttää pieniä kokonaislukuja,
jotta kaikki osasummat ovat tarkkoja ja toteutukset antavat täsmälleen
saman tuloksen:

```{.tuloste tiedosto="esimerkit/08-simd.odotettu"}
```

```{.tuloste tiedosto="esimerkit/tulokset/08-simd.txt"}
```

Intrinsicsit sitovat koodin yhteen arkkitehtuuriin, ja ne ovat
vaikeita lukea. Siksi ne kuuluvat vain profiilin osoittamiin kuumiin
silmukoihin, ja niiden rinnalla pidetään aina skalaariversio sekä
testi, joka vertaa tuloksia. Siirrettävämpiä vaihtoehtoja ovat GCC:n ja
Clangin vektorityypit (`__attribute__((vector_size(32)))`), C++26:n
`std::simd` sekä kirjastot kuten Highway ja SIMDe.

## Käytännössä

- **Anna kääntäjän vektoroida ensin.** Tarkista raportista
  (`-fopt-info-vec`, `-Rpass=loop-vectorize`), mitkä silmukat
  vektoroituivat, ja konekoodista, miten.
- **Kirjoita vektoroitavia silmukoita**: tunnettu kierrosmäärä,
  peräkkäiset osoitteet, ei kierrosten välisiä riippuvuuksia, ei kutsuja.
- **Käytä `restrict`-sanaa, kun lupaus pitää.** Dokumentoi se
  rajapinnassa, koska kutsujan on noudatettava sitä.
- **Hallitse liukulukujen järjestystä itse.** Omat osasummat ovat
  toistettavia; `-ffast-math` muuttaa koko käännösyksikön semantiikkaa.
- **Valitse käskykanta ajon aikana**, jos ohjelma jaetaan valmiina
  binäärinä. `-march=native` sopii vain koneelle, jolla käännetään.
- **Pidä intrinsics-koodin rinnalla skalaariversio** ja testi, joka
  vertaa niitä.

## Itsearviointi

- Osaat lukea kääntäjän vektorointiraportin ja tarkistaa konekoodista,
  vektoroituiko silmukka todella.
- Osaat selittää, miksi aliasing estää vektoroinnin ja mitä
  `restrict` lupaa.
- Osaat selittää, miksi liukulukusumma ei vektoroidu, ja kirjoittaa
  sen osasummina.
- Osaat kirjoittaa SSE2- ja AVX2-intrinsicsfunktion sekä valita
  toteutuksen ajon aikana suorittimen ominaisuuksien mukaan.
