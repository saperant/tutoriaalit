# Mittaaminen C++:ssa

Mittauksen tilastot, eli toistot, mediaani, hajonta ja lämmittely,
käsitellään taidossa *Suorituskyvyn analyysi ja optimointi*. Tässä
luvussa ne toteutetaan C++:lla, ja lisäksi rakennetaan kaksi
determinististä mittaria: muistinvarausten laskuri ja Cachegrindin
käskymäärät operaatiota kohden. Luvun lopussa ovat mikrovertailun
sudenkuopat, toistomäärän kalibrointi ja `perf`, joka mittaa koko
ohjelmaa prosessorin omilla laskureilla. Ensin kuitenkin ongelma, joka
on C++:ssa tavallista pahempi: kääntäjä poistaa mitattavan koodin.

## Kääntäjä poistaa mittauksen

C++-kääntäjä näkee mallien ja `inline`-funktioiden rungot, joten se
sisällyttää ne kutsukohtaan ja poistaa laskennan, jonka tulosta ei
käytetä. Mittaus näyttää silloin nollaa. Esimerkkinä keskiarvo:

```{.cpp tiedosto="esimerkit/02-poistettu.cpp" osa="keskiarvo"}
```

Ratkaisu on kertoa kääntäjälle, että arvoa käytetään, tuottamatta
silti yhtään käskyä. GCC:n ja Clangin laajennettu `asm`-lause sopii
tähän: tyhjä assembly-lohko, joka "lukee" arvon tai "muuttaa" sitä.

```{.cpp tiedosto="esimerkit/mittari.hpp" osa="pida"}
```

`pida` vastaa Google Benchmarkin funktiota `DoNotOptimize` ja
`sotke_muisti` funktiota `ClobberMemory`. `piilota` tekee syötteestä
tuntemattoman, jotta kääntäjä ei voi laskea tulosta etukäteen.
`volatile` estää poistamasta itse `asm`-lausetta, ja `"memory"`
kertoo, että lause voi lukea tai kirjoittaa mitä tahansa muistia.

Esimerkki mittaa keskiarvon neljällä tavalla. Kukin tapa on lambda,
jonka mittauskehys toistaa:

```{.cpp tiedosto="esimerkit/02-poistettu.cpp" osa="tavat"}
```

Cachegrind laskee suoritetut käskyt kierrosta kohden:

```{.tuloste tiedosto="esimerkit/tulokset/tarkista-poistettu.txt"}
```

Hylätty tulos maksaa nolla käskyä: koko kierros on poistettu, ja
jäljelle jää vain silmukan laskuri. Vakiosyötteellä kääntäjä laski
keskiarvon käännöksessä ja tallentaa vain valmiin luvun. Vasta kun
syöte on piilotettu, keskiarvo todella lasketaan. Ajoituksessa
hylätty mittaus näyttää yhtä nollalta:

```{.tuloste tiedosto="esimerkit/tulokset/02-poistettu.txt"}
```

Nollan lähellä oleva tulos on aina syytä epäillä: nykyprosessori ei
käsittele miljoonaa alkiota alle mikrosekunnissa.

## Mittauskehys

Mittauskehys ajaa funktion kerran lämmittelyksi ja sitten halutun
määrän kertoja. Se palauttaa mediaanin ja mediaanin absoluuttisen
poikkeaman, jotka kestävät yksittäisiä häiriöitä paremmin kuin
keskiarvo ja keskihajonta.

```{.cpp tiedosto="esimerkit/mittari.hpp" osa="mittaa"}
```

`std::chrono::steady_clock` on monotoninen kello: se ei hyppää, vaikka
järjestelmän kellonaikaa säädettäisiin. `system_clock` ei sovi
mittaamiseen, ja `high_resolution_clock` on libstdc++:ssa vain
`system_clock`in toinen nimi. Malliparametri `F` sallii minkä tahansa
kutsuttavan ilman `std::function`in kustannusta (luku 4).

## Muistinvarausten laskuri

C++ sallii ohjelman korvata globaalit `operator new`- ja `operator
delete`-funktiot. Korvaava määrittely voi laskea varaukset ennen kuin
se pyytää muistin `malloc`illa:

```{.cpp tiedosto="esimerkit/laskuri.hpp" osa="laskuri"}
```

Korvaavia funktioita saa olla ohjelmassa vain yksi kappale, joten
otsake otetaan mukaan yhteen käännösyksikköön. Kaikki
standardikirjaston säiliöt varaavat oletusallokaattorin kautta
`operator new`illa, joten laskuri näkee jokaisen vektorin,
merkkijonon, solmun ja `std::function`in varauksen. `malloc`ia
suoraan kutsuvat C-kirjastot jäävät laskematta.

Laskuri on deterministinen: sama ohjelma tekee aina yhtä monta
varausta, kun standardikirjaston toteutus on sama. Toteutusten välillä
luvut voivat erota, koska esimerkiksi lyhyen merkkijonon puskurin koko
ja vektorin kasvukerroin eivät ole standardin määräämiä. Tämän
tutoriaalin luvut ovat libstdc++:n (GCC 14), jota myös Ubuntun Clang
käyttää. Tuotannossa sama tieto saadaan ilman koodimuutoksia
työkaluilla, kuten `heaptrack` ja Valgrindin `massif` tai `dhat`.

## Käskyt operaatiota kohden

Valgrind ajaa ohjelman omassa virtuaalikoneessaan ja laskee jokaisen
suoritetun käskyn. Cachegrind lisäksi simuloi välimuistit. Tulokset
ovat täsmälleen samat joka ajossa, mutta Cachegrind laskee myös
ohjelman käynnistyksen ja syötteen rakentamisen. Ne supistuvat pois,
kun ohjelma ajetaan kahdesti, toistoilla 0 ja K, ja erotus jaetaan:

```{.makefile tiedosto="esimerkit/Makefile" osa="kaskyt"}
```

Siksi esimerkit tukevat argumenttia `--kerran TAPA K`. Ohjelma
rakentaa joka kerta saman syötteen, valitsee tavan yhden kerran ja
toistaa sitä K kertaa:

```{.makefile tiedosto="esimerkit/Makefile" osa="poistettu"}
```

`--suhde A B MIN` tarkistaa, että tavan A tulos on vähintään MIN
kertaa tavan B tulos. Näin tekstin väitteet, kuten "piilotettu syöte
tekee enemmän työtä kuin vakiosyöte", testataan joka käännöksellä.

Käskymäärä ei ole aika. Välimuistihutia, väärin ennustettuja haaroja ja
riippuvuusketjuja se ei näe, joten sama käskymäärä voi kestää
kymmenkertaisesti eri ajan. Siksi Cachegrindilla lasketaan tarvittaessa
myös välimuistihudit (luku 8), ja lopullinen tulos mitataan aina
kellolla.

## Mikrovertailut

*Mikrovertailu* (engl. microbenchmark) mittaa pientä koodinpätkää,
kuten yhtä funktiota tai yhtä säiliön operaatiota, irrallaan
ohjelmasta. Luvut 3–10 ovat mikrovertailuja. Se on oikea työkalu kahden
toteutuksen vertailuun, mutta myös helpoin tapa mitata väärin.

### Sudenkuopat

| Sudenkuoppa | Seuraus | Torjunta |
|--------------------------------|--------------------------------|------------------------------|
| Tulosta ei käytetä | Kääntäjä poistaa laskennan | `pida`, `DoNotOptimize` |
| Syöte on vakio | Tulos lasketaan käännöksessä | `piilota`, syöte ajon aikana |
| Sama syöte joka kierros | Ennustin ja välimuisti oppivat sen | Vaihteleva, todenmukainen syöte |
| Liian lyhyt mittaus | Kellon tarkkuus ja kutsun hinta hallitsevat | Toistoja, kunnes mittaus kestää millisekunteja |
| Kylmä aloitus | Sivuvirheet, kylmä välimuisti, kellotaajuuden nousu | Lämmittely ennen mittausta |
| Yksi mittaus | Kohina näyttää erolta | Toistot, mediaani ja hajonta |
| Väärä kokonaisuus | Nopeampi funktio, hitaampi ohjelma | Mittaa myös koko ohjelma |

Viimeinen rivi on tärkein. Mikrovertailussa funktion data ja koodi ovat
välimuistissa, ja haarautumisen ennustin on oppinut sen haarat.
Oikeassa ohjelmassa funktiota kutsutaan muun työn lomassa, jolloin
välimuisti on täynnä muuta. Silmukoiden avaaminen ja suuret
hakutaulukot voittavat mikrovertailun mutta voivat hidastaa ohjelmaa,
koska ne vievät välimuistia muulta koodilta.

### Toistomäärän kalibrointi

Kun mitattava operaatio kestää nanosekunteja, yksi kutsu ei riitä:
kellon tarkkuus ja kellon lukemisen hinta hallitsevat tulosta. Google
Benchmark ja vastaavat kirjastot kasvattavat toistomäärää, kunnes yksi
mittaus kestää tarpeeksi kauan, ja ilmoittavat ajan operaatiota kohden.
Sama periaate omana funktiona:

```{.cpp tiedosto="esimerkit/mittari.hpp" osa="kalibroi"}
```

Luvun 10 muotoiluvertailu käyttää tätä funktiota.

### Google Benchmark

Google Benchmark (Apache 2.0) on yleisin C++:n mikrovertailukirjasto.
Mitattava funktio saa parametrina tilaolion `benchmark::State&`, ja sen
silmukka `for (auto _ : tila)` toistaa mitattavaa koodia niin monta
kertaa kuin kirjasto kalibroi. Silmukan sisällä
`benchmark::DoNotOptimize` ja `benchmark::ClobberMemory` vastaavat
tämän luvun funktioita `pida` ja `sotke_muisti`, ja makro `BENCHMARK`
rekisteröi funktion.

Kirjasto hoitaa kalibroinnin, toistot (`--benchmark_repetitions`),
tilastot ja tulokset JSONina, ja se osaa parametroida syötteen koon.
Ubuntussa se on paketissa `libbenchmark-dev`. Tämä tutoriaali käyttää
omaa pientä kehystä, jotta esimerkit eivät tarvitse ylimääräisiä
riippuvuuksia, mutta oikeassa projektissa kannattaa käyttää kirjastoa.
Vaihtoehtoja ovat nanobench (yksi otsake, MIT) ja Catch2:n
`BENCHMARK`-makro.

## perf ja laitteistolaskurit

Linuxin `perf` lukee prosessorin *suorituskykylaskureita* (engl.
performance monitoring counters): jaksot, käskyt, välimuistihudit ja
väärin ennustetut haarat lasketaan laitteistossa ilman, että ohjelma
hidastuu. Tämän tutoriaalin mittausympäristössä (kontti virtuaalikoneessa)
laskurit eivät ole käytettävissä, joten tässä on vain komennot ja niiden
tulkinta:

```text
perf stat -e cycles,instructions,branch-misses,cache-misses ./ohjelma
perf record -g ./ohjelma          # näytteet kutsupinoineen
perf report                       # kuumat funktiot
perf annotate funktio             # kuumat käskyt lähdekoodin rinnalla
```

| Mittari | Laskenta | Tulkinta |
|-----------------------------|---------------------------|--------------------------------------|
| IPC | käskyt / jaksot | alle 1: odottaa muistia tai ennusteita; yli 2: laskennan rajoittama |
| Haarautumisen ohiarvaukset | branch-misses / branches | yli muutama prosentti: haarat ovat ennustamattomia |
| Välimuistihudit | cache-misses / käskyt | verrataan versioiden kesken, ei absoluuttisesti |

C++-ohjelmissa `perf report` näyttää mallien ja lambdojen nimet pitkinä,
ja sisällytetyt funktiot näkyvät kutsujan osana. `perf report
--no-children` näyttää funktioiden oman ajan, ja `-g --call-graph
dwarf` tuottaa luotettavammat kutsupinot optimoidusta koodista, jossa
kehysosoitinta ei käytetä. Liekkikuvaaja (Brendan Greggin
FlameGraph-skriptit tai `perf script` ja Speedscope) näyttää kutsupinot
yhtenä kuvana.

Kun laskureita ei ole, kuten useimmissa konteissa ja CI-palvelimilla,
Valgrindin Cachegrind ja Callgrind antavat käskyt, simuloidut hudit ja
kutsugraafin. Ne ovat hitaita (20–100 kertaa) mutta deterministisiä.
Intelin VTune ja AMD:n uProf antavat laskureista vielä tarkemman
kuvan, esimerkiksi *top-down*-analyysin, joka jakaa jaksot
käyttöön, odotukseen ja hukkaan.

## Käytännössä

- **Mittaa optimoitu käännös**, `-O2` tai `-O3` kuten tuotannossa.
  Optimoimattomassa C++:ssa jokainen `std::vector`in `operator[]` ja
  iteraattorin askel on funktiokutsu, joten `-O0`-mittaus kertoo
  abstraktioista väärää.
- **Estä poisto `pida`- ja `piilota`-tyyppisillä funktioilla** tai
  kirjaston vastineilla. Älä käytä `volatile`-muuttujia: ne estävät
  myös optimoinnit, jotka tuotantokoodissa tapahtuvat.
- **Nolla tai epäuskottavan pieni aika** tarkoittaa lähes aina, että
  kääntäjä poisti tai laski laskennan valmiiksi.
- **Varauslaskuri on halvin profiloija.** Varausten määrä kertoo
  kopioista, kasvusta ja solmusäiliöistä suoraan, ja se toimii myös
  sanitoijien kanssa ja testeissä.
- **Käskymäärät sopivat regressiotesteihin.** Ajoitus ei sovi
  CI-palvelimelle, jonka kuormaa ei tunneta; käskymäärä samalla
  kääntäjällä sopii.
- **Mikrovertailu vertaa, ohjelma ratkaisee.** Käytä mikrovertailua
  valintaan kahden toteutuksen välillä ja vahvista tulos koko ohjelman
  mittauksella.
- **Käytä kirjastoa**: Google Benchmark tai nanobench hoitavat
  kalibroinnin ja tilastot oikein.
- **Todenmukainen syöte**: koko, jakauma ja vaihtelu kuten
  tuotannossa. Sama syöte joka kierroksella opettaa ennustimelle
  vastauksen.
- **perf ensin, jos se on käytettävissä**: IPC ja ohiarvaukset
  kertovat, kannattaako katsoa muistia, haaroja vai laskentaa.
- **Mittaa myös tarkistusten hinta.** Kovennettu standardikirjasto
  (libstdc++:n `-D_GLIBCXX_ASSERTIONS`, libc++:n *hardening mode*)
  lisää rajatarkistukset esimerkiksi `operator[]`-kutsuihin. Sen
  hinnan saa omalle koodille samalla menetelmällä: käskyt operaatiota
  kohden kummallakin käännöksellä.

## Itsearviointi

- Osaat selittää, miksi kääntäjä voi poistaa mitattavan koodin, ja
  estää sen `asm`-lauseella tuottamatta ylimääräisiä käskyjä.
- Osaat korvata globaalin `operator new`in ja laskea ohjelman osan
  muistinvaraukset.
- Osaat laskea Cachegrindilla käskyt operaatiota kohden niin, että
  käynnistys ja syötteen rakentaminen supistuvat pois.
- Osaat valita mittauksen kellon ja perustella, miksi mediaani on
  keskiarvoa parempi.
- Osaat luetella mikrovertailun sudenkuopat ja torjua ne.
- Osaat kalibroida toistomäärän ja ilmoittaa ajan operaatiota kohden.
- Osaat mitata ohjelman `perf stat`illa ja tulkita IPC:n ja
  haarautumisen ohiarvaukset.
