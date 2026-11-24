# Lopuksi {.runko-lahteet}

## Menetelmä

Optimointi on mittaamista, ja jokainen tämän tutoriaalin esimerkki
noudatti samaa kaavaa:

1. **Oikea perusversio ja testi.** Ilman toistettavaa testiä
   optimointi on arvailua, ja nopea väärä tulos on arvoton.
2. **Mittaus.** Mediaani, pienin arvo ja hajonta toistoista; tieto
   siitä, mitataanko kylmää vai lämmintä tilaa.
3. **Profiili.** Missä aika kuluu, ja mikä osuus siitä on
   nopeutettavissa (Amdahl)?
4. **Hypoteesi.** Liikaa työtä (algoritmi), muistin odottamista
   (välimuistit, asettelu), vääriä ennusteita (haarat), käyttämätöntä
   rinnakkaisuutta (vektorit) vai kiinteitä kustannuksia (varaukset,
   järjestelmäkutsut)?
5. **Muutos, testi ja uusi mittaus.** Yksi muutos kerrallaan; peru,
   jos se ei auttanut.

## Nyrkkisäännöt

Seuraavat suuruusluokat pätevät useimpiin nykyisiin
palvelin- ja työpöytäsuorittimiin. Ne on tarkoitettu arvioihin, eivät
mittausten korvikkeeksi.

| Toimenpide | Aika | Jaksoina (3 GHz) |
|----------------------------------|----------------|----------------|
| Yhteenlasku, looginen operaatio | 0,3 ns | 1 |
| Väärin ennustettu haara | 5 ns | 15–20 |
| L1-osuma | 1 ns | 4–5 |
| L2-osuma | 4 ns | 12–15 |
| L3-osuma | 10–20 ns | 40–60 |
| Keskusmuisti | 80–150 ns | 250–450 |
| Järjestelmäkutsu | 0,1–1 µs | 300–3000 |
| Pieni `malloc` ja `free` | 20–100 ns | 60–300 |
| SSD-lukeminen | 20–100 µs | $10^5$ |
| Verkon edestakainen matka konesalissa | 100–500 µs | $10^6$ |

- **Algoritmi ensin.** Neliöllisen silmukan löytäminen voittaa kaikki
  mikro-optimoinnit.
- **Data ratkaisee.** Pienempi, peräkkäinen ja yhdessä käytetty data on
  nopeaa; hajanainen data on hidasta.
- **Kääntäjä on liittolainen.** Anna sille tietoa (`restrict`,
  `static inline`, LTO, PGO) ja tarkista, mitä se teki.
- **Kiinteät kustannukset kertautuvat.** Varaukset, kutsut ja
  järjestelmäkutsut silmukassa maksavat joka kierroksella.
- **Lopeta ajoissa.** Kun profiili on tasainen, lisävoitot ovat kalliita.

## Testaaminen

Paketin esimerkit testataan kahdella tavalla. Toiminnalliset testit
kääntävät jokaisen esimerkin GCC 14:llä ja Clang 20:llä
sanitoijien kanssa ja vertaavat tulosteet odotettuihin, joten jokainen
optimoitu versio on testattu perusversiota vastaan. Valgrindin
simuloidut luvut ovat deterministisiä, ja Makefile tarkistaa niistä
väitteet, joihin teksti nojaa: sarakkeittainen läpikäynti tekee
vähintään neljä kertaa enemmän hutia, lohkominen vähentää
muistiliikennettä vähintään neljäsosaan, lajittelematon data tuottaa
vähintään kymmenen kertaa enemmän vääriä ennusteita, LTO poistaa
kutsun ja PGO-käännös antaa saman tuloksen. Ajoitukset tulostetaan,
mutta niitä ei verrata, koska ne riippuvat koneesta.

## Rinnakkaisuus

Tämä tutoriaali käsitteli yhden ytimen suorituskykyä. Moniytimisessä
ohjelmassa samat periaatteet pätevät, ja niiden lisäksi tulevat
työnjako, synkronoinnin hinta, väärä jakaminen ja muistikaistan
jakaminen ytimien kesken. Amdahlin laki rajoittaa rinnakkaistamista
samalla tavalla kuin optimointia: sarjallinen osa määrää ylärajan.
Ennen kuin ohjelman jakaa säikeisiin, sen yhden säikeen version
kannattaa optimoida, koska jokainen ydin hyötyy siitä.

## Jatkotaidot

- **C++:n suorituskyky**: siirtosemantiikka, kopiot, allokaattorit,
  mallien ja `constexpr`-laskennan hinnat sekä standardikirjaston
  säiliöiden valinta.
- **GPU-laskenta**: tuhansien säikeiden laskenta, muistihierarkia
  näytönohjaimessa ja roofline-malli GPU:lle.
- **Arkkitehtuurin tutkiminen**: suorittimen mikroarkkitehtuurin
  mittaaminen ja mallintaminen, laitteistolaskurit ja simulaattorit.
- **Rinnakkaisohjelmointi**: säikeet, synkronointi ja rinnakkaiset
  algoritmit.

## Lähteet

- Denis Bakhvalov: *Performance Analysis and Tuning on Modern CPUs*,
  2. painos, 2024, <https://github.com/dendibakh/perf-book>. Nykyaikainen
  ja käytännönläheinen kokonaisesitys: perf, top-down-menetelmä,
  välimuistit, haarat ja vektorointi.
- Ulrich Drepper: *What Every Programmer Should Know About Memory*,
  Red Hat 2007, <https://people.freebsd.org/~lstewart/articles/cpumemory.pdf>.
  Muistihierarkian perusteos; askelpituus- ja osoitinjahtikokeet.
- Agner Fog: *Optimization manuals*, <https://www.agner.org/optimize/>.
  C++-koodin optimointi, mikroarkkitehtuurien kuvaukset ja käskyjen
  viive- ja läpäisytaulukot.
- Brendan Gregg: *Systems Performance*, 2. painos, Addison-Wesley 2020,
  sekä <https://www.brendangregg.com/flamegraphs.html>. Mittausmenetelmät
  ja liekkikuvaajat.
- John L. Hennessy ja David A. Patterson: *Computer Architecture: A
  Quantitative Approach*, 6. painos, Morgan Kaufmann 2017. Välimuistit,
  ennustus ja vektoriarkkitehtuurit.
- Samuel Williams, Andrew Waterman ja David Patterson: *Roofline: An
  Insightful Visual Performance Model for Multicore Architectures*,
  Communications of the ACM 52(4), 2009.
- Gene M. Amdahl: *Validity of the Single Processor Approach to
  Achieving Large Scale Computing Capabilities*, AFIPS 1967.
- Kazushige Goto ja Robert A. van de Geijn: *Anatomy of
  High-Performance Matrix Multiplication*, ACM Transactions on
  Mathematical Software 34(3), 2008. BLAS-kirjastojen lohkominen ja
  mikroytimet.
- Todd Mytkowicz, Amer Diwan, Matthias Hauswirth ja Peter F. Sweeney:
  *Producing Wrong Data Without Doing Anything Obviously Wrong!*,
  ASPLOS 2009. Ympäristömuuttujien ja linkitysjärjestyksen vaikutus
  mittauksiin.
- Ahmad Yasin: *A Top-Down Method for Performance Analysis and Counters
  Architecture*, ISPASS 2014.
- Donald E. Knuth: *Structured Programming with go to Statements*,
  Computing Surveys 6(4), 1974. Lainaus ennenaikaisesta optimoinnista.
- t0st: *How I cut GTA Online loading times by 70%*, 2021,
  <https://nee.lv/2021/02/28/How-I-cut-GTA-Online-loading-times-by-70/>.
  `sscanf` ja `strlen` neliöllisenä silmukkana.
- Valgrind-käyttöohje: Cachegrind ja Callgrind,
  <https://valgrind.org/docs/manual/>.
- GCC-käyttöohje: *Options That Control Optimization* ja
  `-fopt-info`, <https://gcc.gnu.org/onlinedocs/gcc/Optimize-Options.html>.
- Intel Intrinsics Guide,
  <https://www.intel.com/content/www/us/en/docs/intrinsics-guide/>.
- Linuxin perf-työkalun wiki, <https://perfwiki.github.io/>.

## Lisenssi

Tämä tutoriaali ja sen esimerkkikoodit on lisensoitu Creative Commons
Nimeä–JaaSamoin 4.0 Kansainvälinen -lisenssillä (CC BY-SA 4.0,
<https://creativecommons.org/licenses/by-sa/4.0/deed.fi>). Teosta saa
kopioida, levittää ja muokata, kunhan alkuperäinen lähde mainitaan ja
muokatut versiot jaetaan samalla lisenssillä.
