# Rinnakkaiset algoritmit ja työnjako

Edellisten lukujen välineillä rakennetaan rinnakkaisia algoritmeja. Tämä
luku käy läpi standardikirjaston rinnakkaiset algoritmit, kaksi
perusalgoritmia (reduktio ja prefiksisumma), työn jakamisen säikeille,
OpenMP:n ja nopeutuksen teoreettiset rajat. Lopuksi mitataan väärää jakamista, joka
voi tehdä oikeasta rinnakkaisohjelmasta hitaamman kuin sarjallisesta.

## Suorituspolitiikat

C++17 lisäsi useimpiin standardialgoritmeihin ensimmäiseksi parametriksi
**suorituspolitiikan**:

| Politiikka | Lupa |
|---------------|-----------------------------------|
| `std::execution::seq` | Sarjallinen, kuten ilman politiikkaa (mutta poikkeus kutsuu `terminate`) |
| `std::execution::par` | Rinnakkain useassa säikeessä |
| `std::execution::par_unseq` | Rinnakkain ja vektoroituna samassa säikeessä lomitettuna |
| `std::execution::unseq` | Vektoroituna yhdessä säikeessä (C++20) |

Politiikka on *lupa* eikä käsky:

```{.cpp tiedosto="esimerkit/10-politiikat.cpp" osa="politiikat"}
```

```{.tuloste tiedosto="esimerkit/10-politiikat.odotettu"}
```

- `std::reduce` eroaa `std::accumulate`sta siinä, että se saa laskea
  summan missä järjestyksessä ja ryhmittelyssä tahansa. Operaation on
  siksi oltava liitännäinen ja vaihdannainen, tai tulos riippuu
  toteutuksesta.
- `par` sallii funktion kutsumisen eri säikeissä samaan aikaan, joten
  jaetun tilan muuttaminen funktiossa on datakilpailu.
- `par_unseq` sallii lisäksi saman säikeen kutsujen lomittamisen
  vektorikäskyiksi. Funktio ei silloin saa lukita mutexia eikä varata
  muistia, koska kaksi lomitettua kutsua samassa säikeessä voisi lukkiutua.

GCC:n libstdc++ toteuttaa rinnakkaiset politiikat Intelin TBB-kirjaston
avulla. Jos TBB:n otsakkeita ei löydy, ohjelma kääntyy ja toimii, mutta
algoritmit ajetaan sarjallisesti. Jos otsakkeet löytyvät, libstdc++
valitsee TBB:n automaattisesti, ja ohjelma on linkitettävä valitsimella
`-ltbb`; muuten linkitys epäonnistuu. Esimerkki valitsee siksi
sarjallisen taustan itse makrolla `_GLIBCXX_USE_TBB_PAR_BACKEND`, jolloin
se toimii samoin kaikilla koneilla ja osoittaa vain, että tulokset ovat
oikeat. Esimerkki ei siis aja mitään rinnakkain; rinnakkaisen ajon saa
asentamalla TBB:n, poistamalla makron ja linkittämällä valitsimella
`-ltbb`. NVIDIA:n `nvc++` ajaa samat algoritmit näytönohjaimella
(`-stdpar`).

## Reduktio

Reduktio yhdistää kokoelman yhdeksi arvoksi liitännäisellä operaatiolla.
Rinnakkaisena se jaetaan osiin, jokainen säie laskee osansa paikallisesti,
ja osatulokset yhdistetään:

```{.cpp tiedosto="esimerkit/10-reduktio.cpp" osa="reduktio"}
```

```{.cpp tiedosto="esimerkit/10-reduktio.cpp" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/10-reduktio.odotettu"}
```

Liukulukujen yhteenlasku ei ole liitännäinen, koska jokainen välitulos
pyöristetään. Tavallinen summa muuttuu siksi jaon mukana viimeisissä
numeroissa. Tulos on silti toistettava: sama jako antaa saman tuloksen joka
ajossa, koska jokainen osa lasketaan samassa järjestyksessä ja osat
yhdistetään indeksijärjestyksessä. Jos osatulokset yhdistettäisiin
valmistumisjärjestyksessä (esimerkiksi atomisella `fetch_add`illa), tulos
vaihtelisi ajosta toiseen. Kahanin kompensoitu summa pitää kirjaa
pyöristysvirheestä ja on lähes riippumaton jaosta; se maksaa noin neljä
operaatiota yhden sijaan.

Kun rinnakkaisen laskennan tuloksen on oltava bitilleen toistettava (esim.
tieteellinen laskenta tai testit), jako tehdään kiinteäksi eikä säikeiden
määrästä riippuvaksi, ja osat yhdistetään aina samassa järjestyksessä.

## Prefiksisumma

Prefiksisumma (*scan*) laskee jokaiseen kohtaan kaikkien edeltävien
alkioiden summan. Se näyttää luonnostaan sarjalliselta, mutta sen voi
rinnakkaistaa kolmessa vaiheessa:

```{.cpp tiedosto="esimerkit/10-prefiksi.cpp" osa="prefiksi"}
```

```{.cpp tiedosto="esimerkit/10-prefiksi.cpp" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/10-prefiksi.odotettu"}
```

1. Jokainen lohko lasketaan itsenäisesti, ja sen viimeinen arvo on lohkon
   summa.
2. Lohkosummista lasketaan eksklusiivinen prefiksi: lohkon $b$ siirtymä on
   kaikkien sitä edeltävien lohkojen summa. Lohkoja on vähän, joten tämä
   tehdään sarjallisesti esteen valmistumisfunktiossa.
3. Jokaisen lohkon alkioihin lisätään sen siirtymä.

Algoritmi käy datan läpi kahdesti, joten työtä on kaksinkertaisesti
sarjalliseen verrattuna. Nopeutusta on odotettavissa vasta usealla
ytimellä, ja muistikaistan rajoittamalla datalla ei aina silloinkaan.
Prefiksisumma on silti tärkeä rakennuspala: sillä lasketaan rinnakkain
suodatuksen kohdepaikat, kantalukulajittelun paikat ja harvojen
matriisien rivien alut. Standardissa se on `std::inclusive_scan` ja
`std::exclusive_scan` suorituspolitiikan kanssa.

## Työnjako

Kun tehtävät ovat erikokoisia, työnjako ratkaisee, kuinka kauan
viimeinen säie laskee. Esimerkissä tehtävän $i$ hinta kasvaa lineaarisesti
$i$:n mukana:

```{.cpp tiedosto="esimerkit/10-tyonjako.cpp" osa="jaot"}
```

```{.tuloste tiedosto="esimerkit/10-tyonjako.odotettu"}
```

![Säiekohtainen kuorma suhteessa keskiarvoon (laskettu esimerkin
hintafunktiosta). Staattisessa jaossa viimeinen säie saa kalleimmat
tehtävät ja määrää koko laskennan keston.](kuvat/tyonjako.png){width=85%}

- **Staattinen yhtenäinen jako** antaa viimeiselle säikeelle 1,75
  kertaa keskimääräisen kuorman: koko laskenta kestää 1,75 kertaa
  ihanteellisen ajan. Tulos on deterministinen, koska jako ei riipu
  ajoituksesta.
- **Syklinen jako** tasaa tämän kuorman lähes täydellisesti, koska
  jokainen säie saa joka neljännen tehtävän. Se toimii, kun hinta muuttuu
  säännöllisesti, mutta huonontaa paikallisuutta: vierekkäiset tehtävät
  menevät eri ytimille.
- **Dynaaminen jako** jakaa työn ajoituksen mukaan: vapaa säie ottaa
  seuraavan erän atomisesta laskurista. Se tasaa myös kuorman, jota ei
  tunneta etukäteen, ja sopeutuu siihen, että osa säikeistä saa vähemmän
  suoritinaikaa. Kuormitetulla testikoneella säikeiden osuudet
  vaihtelivat siksi ajosta toiseen (virhetulosteessa), vaikka kokonaisaika
  oli lyhin. Erän koko on kompromissi: pieni erä tasaa paremmin, iso
  vähentää kilpailua laskurista.

**Työnvarastaminen** (*work stealing*) on dynaamisen jaon hajautettu
muoto. Jokaisella työntekijällä on oma kaksipäinen jono, johon se lisää ja
josta se ottaa tehtäviä toisesta päästä. Tyhjä työntekijä varastaa
satunnaisen toisen jonon toisesta päästä. Kilpailua on vain
varastettaessa, ja varastettava tehtävä on tyypillisesti iso (rekursion
ylätaso). Cilk, Intel TBB, Rayon, Javan ForkJoinPool ja Go:n vuorontaja
toimivat näin.

Työnvarastaminen sopii erityisesti *haarautuvaan* rinnakkaisuuteen
(*fork–join*), jossa tehtävä jakaa itsensä rekursiivisesti osiin,
kuten lomituslajittelu. Tällaisen laskennan rinnakkaisuutta kuvataan
kahdella luvulla: *työ* $T_1$ on kaikkien operaatioiden määrä ja *jänne*
$T_\infty$ pisin toisistaan riippuvien operaatioiden ketju. Nopeutus ei
voi ylittää suhdetta $T_1 / T_\infty$, ja Blumofen ja Leisersonin tulos
(1999) takaa, että työnvarastaminen saavuttaa $p$ suorittimella ajan
$T_1/p + O(T_\infty)$. Rekursio katkaistaan käytännössä sarjalliseksi,
kun osa on niin pieni, ettei tehtävän luominen enää kannata.

## OpenMP lyhyesti

Edellä reduktio ja työnjako kirjoitettiin käsin, jotta niiden rakenne
näkyy. Laskentakoodissa sama tehdään useimmiten **OpenMP**:llä, joka on
C:n, C++:n ja Fortranin vakiintunut laajennus jaetun muistin
rinnakkaisuuteen. Silmukka merkitään kääntäjän direktiivillä, ja
kääntäjä tuottaa säikeet, jaon ja yhdistämisen. GCC ja Clang tukevat
sitä valitsimella `-fopenmp`; ilman valitsinta direktiivit ohitetaan ja
ohjelma on sarjallinen.

```{.cpp tiedosto="esimerkit/openmp/tyonjako.cc" osa="reduktio"}
```

Lause `reduction(+ : summa)` tekee saman kuin osion *Reduktio* käsin
kirjoitettu versio: jokainen säie laskee paikalliseen kopioon, ja kopiot
yhdistetään lopuksi. Ilman sitä `summa += i` olisi datakilpailu.
Työnjako valitaan lauseella `schedule`:

```{.cpp tiedosto="esimerkit/openmp/tyonjako.cc" osa="jako"}
```

```{.tuloste tiedosto="esimerkit/openmp/tyonjako.odotettu"}
```

Luvut ovat samat kuin omassa toteutuksessa: `schedule(static)` on
yhtenäinen jako, `schedule(static, 1)` syklinen ja
`schedule(dynamic, 32)` erälaskuri. OpenMP ei poista
rinnakkaisohjelmoinnin sääntöjä: silmukan rungossa jaettuun dataan
kirjoittaminen on edelleen datakilpailu, ja liukulukujen reduktion
tulos riippuu jaosta. ThreadSanitizer ei tunne GCC:n OpenMP-kirjaston
sisäistä synkronointia ja raportoi siitä vääriä hälytyksiä, joten tätä
esimerkkiä ei ajeta sillä.

## Nopeutuksen rajat

Taito *Tietokonearkkitehtuuri* esitteli Amdahlin lain yleisessä
muodossa: nopeutus on rajattu sen osan mukaan, jota parannus ei koske.
Rinnakkaisohjelmassa tuo osa on sarjallinen osuus. Jos ohjelmasta
osuus $s$ on sarjallista, Amdahlin laki (1967) rajaa nopeutuksen $p$
suorittimella:

$$S_A(p) = \frac{1}{s + (1 - s)/p} \le \frac{1}{s}.$$

Gustafsonin laki (1988) katsoo asiaa toisin: kun suorittimia on enemmän,
myös ongelma kasvaa, ja sarjallinen osuus pysyy vakiona ajasta:

$$S_G(p) = s + (1 - s)\,p.$$

```{.cpp tiedosto="esimerkit/10-amdahl.cpp" osa="taulukko"}
```

```{.tuloste tiedosto="esimerkit/10-amdahl.odotettu"}
```

![Nopeutus suorittimien määrän funktiona taulukon sarjallisilla
osuuksilla (molemmat asteikot logaritmisia, pisteviiva on ihanteellinen
nopeutus). Amdahlin käyrät taittuvat rajaansa $1/s$; Gustafsonin
skaalatussa ongelmassa nopeutus kasvaa lähes
suoraan.](kuvat/nopeutus.png){width=100%}

Jo 5 %:n sarjallinen osuus rajaa nopeutuksen 20-kertaiseksi, vaikka
suorittimia olisi tuhat. Sarjallista osuutta ovat paitsi sarjallinen koodi
myös lukon alla vietetty aika, säikeiden käynnistys ja tulosten
yhdistäminen. Gustafsonin näkökulma selittää, miksi suuret koneet ovat
silti hyödyllisiä: ne eivät ratkaise samaa ongelmaa nopeammin vaan
isomman ongelman samassa ajassa.

Mitattu nopeutus näyttää saman käytännössä. Luvun alun reduktio ajettiin
40 miljoonalle luvulle eri säiemäärillä neliytimisessä virtuaalikoneessa
(Intel Xeon 2,1 GHz, GCC 14, `-O2`, ei muuta kuormaa). Mittausohjelma
`esimerkit/mittaus/nopeutus.cc` sisällyttää esimerkin funktion
sellaisenaan ja ilmoittaa yhdeksän ajon mediaanin:

```{.tuloste tiedosto="esimerkit/tulokset/10-nopeutus.txt"}
```

![Mitattu nopeutus säiemäärän funktiona (samat luvut kuin
tulosteessa). Neljään säikeeseen asti nopeutus seuraa ihannetta;
kahdeksan säiettä neljällä ytimellä on hitaampi kuin
neljä.](kuvat/mitattu.png){width=70%}

Neljällä säikeellä nopeutus on noin 3,6 eli 90 % ihanteesta. Amdahlin
kaavasta ratkaistuna se vastaa 3–4 %:n sarjallista osuutta: säikeiden
käynnistystä, osasummien yhdistämistä ja ytimien yhteistä muistikaistaa.
Kahdeksan säiettä neljällä ytimellä ei nopeuta vaan hidastaa, koska
säikeet vuorottelevat ytimillä ja vuoronvaihdot maksavat. Laskentatyössä
säikeitä kannattaa siksi olla enintään ytimien verran
(`std::thread::hardware_concurrency`). Luvut vaihtelevat ajosta toiseen
muutaman prosentin.

## Väärä jakaminen

Välimuisti käsittelee muistia riveittäin, x86-64:llä 64 tavun paloina.
Jos kaksi säiettä kirjoittaa eri muuttujiin samalla rivillä, rivi kulkee
ytimeltä toiselle jokaisella kirjoituksella, vaikka säikeet eivät jaa
yhtään dataa. Tämä on **väärä jakaminen** (*false sharing*).
`std::hardware_destructive_interference_size` kertoo etäisyyden, jolla
kaksi oliota eivät häiritse toisiaan:

```{.cpp tiedosto="esimerkit/10-vaara-jakaminen.cpp" osa="rakenteet"}
```

```{.cpp tiedosto="esimerkit/10-vaara-jakaminen.cpp" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/10-vaara-jakaminen.odotettu"}
```

Tiiviit laskurit ovat kaikki samalla rivillä, erilliset kukin omallaan.
Esimerkin silmukka on lyhyt ja sen ajat (virhetulosteessa) riippuvat
koneesta, joten ero mitattiin erikseen. Mittausohjelma
`esimerkit/mittaus/vaara-jakaminen.cc` käyttää samoja rakenteita,
kasvattaa jokaista laskuria 20 miljoonaa kertaa ja ilmoittaa seitsemän
ajon mediaanin samalla koneella kuin edellä:

```{.tuloste tiedosto="esimerkit/tulokset/10-vaara-jakaminen.txt"}
```

![Väärän jakamisen hinta (samat luvut kuin tulosteessa, logaritminen
asteikko). Erillisten laskurien aika ei riipu säikeiden määrästä;
tiiviiden laskurien aika kasvaa jokaisen säikeen
myötä.](kuvat/jakaminen.png){width=70%}

Yhdellä säikeellä asettelulla ei ole väliä. Kahdella säikeellä tiivis
versio on noin kymmenen ja neljällä yli kaksikymmentä kertaa hitaampi,
vaikka säikeet eivät jaa yhtään muuttujaa: atominen kasvatus tarvitsee
rivin yksinomistuksen, ja rivi kulkee ytimeltä toiselle jokaisella
kirjoituksella. Säikeiden lisääminen siis hidastaa ohjelmaa. Ilmiö on
voimakkain atomisilla ja lukituilla operaatioilla. Tavallinen kirjoitus
kärsii vähemmän, koska suoritin voi kerätä kirjoituksia puskuriinsa ja
purkaa ne kerralla, kun rivi on sen hallussa; taidon *Suorituskyvyn
analyysi ja optimointi* vastaava koe tavallisilla muuttujilla näytti
samalla koneella vain pienen eron. Mittaa omalla koneellasi optimoidulla
käännöksellä (`-O2`) ilman sanitoijia ja muuta kuormaa; sama taito
käsittelee mittaamisen tarkemmin.

GCC varoittaa (`-Winterference-size`), jos vakiota käytetään
otsikkotiedostossa, koska sen arvo voi muuttua kääntäjäversion tai
`-mtune`-valinnan mukana ja muuttaa siten tyypin kokoa ja ABI:a.
Julkisissa rajapinnoissa käytetään siksi kiinteää arvoa, esimerkiksi
`alignas(64)` tai `alignas(128)` (Intelin vierekkäisten rivien
esinouto käsittelee rivejä pareittain).

## Käytännössä

- **Rinnakkaista ensin algoritmi, sitten koodi.** Suuri sarjallinen
  osuus tai lukon alla vietetty aika rajaa nopeutuksen ennen kuin
  yksikään mikro-optimointi auttaa.
- **Standardialgoritmi politiikalla, kun se riittää.** Tarkista, että
  toteutus oikeasti rinnakkaistaa (libstdc++ tarvitsee TBB:n).
- **Kiinteä jako toistettaviin tuloksiin.** Liukulukujen reduktiossa
  tulos riippuu jaosta; älä yhdistä osia valmistumisjärjestyksessä.
- **OpenMP silmukoille.** Kun rinnakkaistettava asia on silmukka
  taulukon yli, direktiivi on lyhyempi ja vähemmän virhealtis kuin omat
  säikeet.
- **Dynaaminen jako tuntemattomalle kuormalle.** Atominen
  erälaskuri on yksinkertainen ja tehokas; työnvarastaminen skaalautuu
  pidemmälle.
- **Säiekohtainen data omille riveilleen.** Kuumat laskurit ja
  osatulokset joko paikallisiin muuttujiin tai `alignas`illa erilleen.

## Itsearviointi

- Osaat käyttää standardialgoritmeja suorituspolitiikoilla ja kertoa,
  mitä `par` ja `par_unseq` vaativat funktiolta.
- Osaat toteuttaa rinnakkaisen reduktion ja prefiksisumman ja selittää,
  miksi liukulukujen reduktion tulos riippuu jaosta.
- Osaat valita staattisen, syklisen ja dynaamisen työnjaon välillä ja
  kuvata työnvarastamisen periaatteen.
- Osaat rinnakkaistaa silmukan OpenMP:n `parallel for` -direktiivillä
  ja valita `reduction`- ja `schedule`-lauseet.
- Osaat laskea Amdahlin ja Gustafsonin lakien nopeutukset ja tunnistaa
  väärän jakamisen.
