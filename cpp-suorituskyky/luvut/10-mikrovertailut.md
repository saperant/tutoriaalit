# Mikrovertailut ja perf

*Mikrovertailu* (engl. microbenchmark) mittaa pientä koodinpätkää,
kuten yhtä funktiota tai yhtä säiliön operaatiota, irrallaan
ohjelmasta. Se on oikea työkalu kahden toteutuksen vertailuun, mutta
myös helpoin tapa mitata väärin. Tässä luvussa rakennetaan
mikrovertailu Google Benchmarkin periaatteilla, verrataan kuutta tapaa
muuntaa kokonaisluku merkkijonoksi ja esitellään `perf`, joka mittaa
koko ohjelmaa prosessorin omilla laskureilla.

## Sudenkuopat

| Sudenkuoppa | Seuraus | Torjunta |
|--------------------------------|--------------------------------|------------------------------|
| Tulosta ei käytetä | Kääntäjä poistaa laskennan | `pida`, `DoNotOptimize` (luku 2) |
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

## Toistomäärän kalibrointi

Google Benchmark ja vastaavat kirjastot kasvattavat toistomäärää,
kunnes yksi mittaus kestää tarpeeksi kauan, ja ilmoittavat ajan
operaatiota kohden. Sama periaate omana funktiona:

```{.cpp tiedosto="esimerkit/10-muotoilu.cpp" osa="vertailu"}
```

Mitattava kierros käsittelee tuhat eri lukua, jotta ennustin ei opi yhtä
syötettä, ja `piilota` estää kääntäjää laskemasta tuloksia etukäteen:

```{.cpp tiedosto="esimerkit/10-muotoilu.cpp" osa="kierros"}
```

## Kokonaisluku merkkijonoksi

C++:ssa on ainakin kuusi tapaa muuntaa luku tekstiksi:

```{.cpp tiedosto="esimerkit/10-muotoilu.cpp" osa="tavat"}
```

```{.cpp tiedosto="esimerkit/10-muotoilu.cpp" osa="testi"}
```

```{.tuloste tiedosto="esimerkit/10-muotoilu.odotettu"}
```

Yksikään tapa ei varaa muistia: tulokset ovat lyhyitä, joten ne
mahtuvat merkkijonon sisäiseen puskuriin. Erot ovat silti suuria:

```{.makefile tiedosto="esimerkit/Makefile" osa="muotoilu"}
```

```{.tuloste tiedosto="esimerkit/tulokset/tarkista-muotoilu.txt"}
```

```{.tuloste tiedosto="esimerkit/tulokset/10-muotoilu.txt"}
```

`std::to_chars` (C++17) on nopein, koska se tekee vain muunnoksen: ei
lokaalia, ei muotoilumerkkijonon jäsennystä eikä virheiden
tarkistusta puskurin koon lisäksi. `snprintf` jäsentää
muotoilumerkkijonon ajon aikana ja kulkee C-kirjaston yleisen
tulostuskoneiston läpi. `std::format` tarkistaa muotoilun
käännösaikana mutta tekee silti tyypin mukaisen ajonaikaisen
valinnan. `std::ostringstream` on hitain: virran rakentaminen alustaa
lokaalin ja puskurin, ja jokainen `<<` kulkee virtuaalikutsujen ja
vartijaolion (engl. sentry) läpi.

Käytännön valinta riippuu tarpeesta. Lokirivien ja virheilmoitusten
tekemiseen `std::format` ja `std::print` ovat sopivia ja turvallisia.
Sarjallistamiseen, kuten JSONin, CSV:n tai protokollien tuottamiseen,
`std::to_chars` ja `std::from_chars` ovat oikeat työkalut: ne ovat
lokaalista riippumattomia, eli ne tuottavat saman tuloksen joka
koneella, ja ne ovat moninkertaisesti nopeampia. `std::ostringstream`
kuuluu vanhaan koodiin.

## Google Benchmark

Google Benchmark (Apache 2.0) on yleisin C++:n mikrovertailukirjasto.
Mitattava funktio saa parametrina tilaolion `benchmark::State&`, ja sen
silmukka `for (auto _ : tila)` toistaa mitattavaa koodia niin monta
kertaa kuin kirjasto kalibroi. Silmukan sisällä
`benchmark::DoNotOptimize` ja `benchmark::ClobberMemory` vastaavat
luvun 2 funktioita `pida` ja `sotke_muisti`, ja makro `BENCHMARK`
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

- **Mikrovertailu vertaa, ohjelma ratkaisee.** Käytä mikrovertailua
  valintaan kahden toteutuksen välillä ja vahvista tulos koko ohjelman
  mittauksella.
- **Käytä kirjastoa**: Google Benchmark tai nanobench hoitavat
  kalibroinnin ja tilastot oikein.
- **Todenmukainen syöte**: koko, jakauma ja vaihtelu kuten
  tuotannossa. Sama syöte joka kierroksella opettaa ennustimelle
  vastauksen.
- **Muotoile lukuja `std::to_chars`illa** sarjallistamisessa ja
  `std::format`illa ihmisille luettavassa tulosteessa.
- **perf ensin, jos se on käytettävissä**: IPC ja ohiarvaukset
  kertovat, kannattaako katsoa muistia, haaroja vai laskentaa.

## Itsearviointi

- Osaat luetella mikrovertailun sudenkuopat ja torjua ne.
- Osaat kalibroida toistomäärän ja ilmoittaa ajan operaatiota kohden.
- Osaat perustella, miksi `std::to_chars` on nopeampi kuin
  `snprintf`, `std::format` ja `std::ostringstream`.
- Osaat mitata ohjelman `perf stat`illa ja tulkita IPC:n ja
  haarautumisen ohiarvaukset.
