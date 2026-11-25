# Lajittelu

CPU:n parhaat lajittelualgoritmit, kuten pikalajittelu ja
introsort, ovat vertailupohjaisia ja datasta riippuvia: jako riippuu
pivotista, ja haarautuminen riippuu vertailun tuloksesta. GPU:lle
sopivat paremmin algoritmit, joissa jokainen säie tekee saman työn
datasta riippumatta. Tässä luvussa toteutetaan kaksi: **bitoninen
lajittelu**, joka on lajitteluverkko, ja **kantalukulajittelu**, joka
rakentuu histogrammista ja prefiksisummasta. Jälkimmäinen on GPU:n
nopein yleinen lajittelu kokonaisluku- ja liukulukuavaimille.

## Bitoninen lajittelu

**Lajitteluverkko** on kiinteä jono vertaa ja vaihda -askeleita. Mitkä
parit verrataan, ei riipu datasta, joten jokainen askel on täysin
rinnakkainen: $n/2$ riippumatonta vertailua. Bitoninen verkko
rakentuu bitonisista jonoista, jotka ensin nousevat ja sitten
laskevat. Vaiheessa $k = 2, 4, 8, \dots, n$ jokainen $k$ alkion lohko
lajitellaan vuorotellen nousevaksi ja laskevaksi, jolloin kahdesta
vierekkäisestä lohkosta tulee yksi bitoninen jono. Vaiheen askeleet
$j = k/2, k/4, \dots, 1$ yhdistävät sen lajitelluksi.

![Bitoninen lajitteluverkko kahdeksalle alkiolle. Jokainen
pystynuoli on yksi vertaa ja vaihda -pari, ja saman sarakkeen parit
tehdään rinnakkain. Vaiheet $k = 2$ ja $k = 4$ tekevät lohkoista
vuorotellen nousevia ja laskevia, ja viimeinen vaihe yhdistää
bitonisen jonon lajitelluksi.](kuvat/07-bitoninen.png){width=100%}

Askeleessa $(k, j)$ alkio $i$ verrataan alkioon $i \oplus j$, ja
suunta riippuu bitistä $i \mathbin{\&} k$. Yksi askel on yksi ajo:

```{.glsl tiedosto="esimerkit/varjostimet/bitoninen.comp" osa="askel"}
```

```{.cpp tiedosto="esimerkit/07-bitoninen.cpp" osa="globaali"}
```

Verkko vaatii, että $n$ on kahden potenssi. Muun kokoinen data
täydennetään suurimmalla arvolla, jolloin täytteet lajittuvat loppuun:

```{.cpp tiedosto="esimerkit/07-bitoninen.cpp" osa="taydennys"}
```

Askelia on $\log_2 n (\log_2 n + 1) / 2$, eli 262 144 alkiolle 171.
Jokaisessa on $n/2$ vertailua, joten työtä on $O(n \log^2 n)$. Se on
enemmän kuin vertailulajittelun $O(n \log n)$, mutta jokainen askel on
säännöllinen ja hajaantumaton, ja verkko lajittelee pieniä taulukoita
GPU:lla nopeasti. Pieniä verkkoja käytetään myös osana muita
algoritmeja, esimerkiksi lajittelemaan työryhmän sisäinen lohko
jaetussa muistissa.

### Lyhyet askeleet jaetussa muistissa

Askeleet, joiden etäisyys $j$ on alle 512, pysyvät 512 alkion lohkon
sisällä. Ne voidaan tehdä yhdessä ajossa: työryhmä lataa lohkon
jaettuun muistiin, tekee kaikki lohkon sisäiset askeleet esteiden
välein ja kirjoittaa lohkon takaisin.

```{.glsl tiedosto="esimerkit/varjostimet/bitoninen_jaettu.comp" osa="lohko"}
```

```{.cpp tiedosto="esimerkit/07-bitoninen.cpp" osa="yhdistelma"}
```

```{.tuloste tiedosto="esimerkit/07-bitoninen.odotettu"}
```

Ajojen määrä putoaa 171:stä 55:een, ja globaalin muistin läpikäyntejä
on saman verran vähemmän. Vertailuja on sama määrä, koska verkko on
sama. Oikealla GPU:lla yhdistelmä on selvästi nopeampi, koska jokainen
globaali askel lukee ja kirjoittaa koko taulukon. Lavapipellä se oli
mittaustilassa noin kaksi kertaa *hitaampi*. Taulukko mahtuu CPU:n
välimuistiin, joten globaali askel on halpa, mutta jokainen
jaetun muistin askel maksaa esteen (luku 3). Tämä on taas muistutus
siitä, että optimointi tehdään kohdelaitteelle ja mitataan siellä.

## Kantalukulajittelu

**Kantalukulajittelu** (radix sort) ei vertaa avaimia, vaan lajittelee
ne numero kerrallaan vähiten merkitsevästä alkaen (LSD). Jokainen
kierros on *vakaa* lajittelu yhden numeron mukaan: samannumeroiset
avaimet säilyttävät keskinäisen järjestyksensä. Silloin kierroksen
jälkeen avaimet ovat järjestyksessä kaikkien tähän asti käsiteltyjen
numeroiden mukaan. 32-bittiset avaimet ja 4-bittiset numerot vaativat
8 kierrosta, ja työ on $O(n)$ kierrosta kohden.

GPU:lla jokainen kierros on kolme vaihetta, jotka on jo opittu:

1. **Laskenta**: jokainen työryhmä laskee 256 avaimensa numeroiden
   histogrammin (16 lokeroa).
2. **Skannaus**: histogrammit tallennetaan numero kerrallaan
   (`laskut[numero * ryhmia + ryhma]`), ja niiden poissulkeva summa
   antaa jokaiselle (numero, ryhmä)-parille aloituspaikan
   kohdetaulukossa. Kaikki numeron 0 avaimet tulevat ennen numeron 1
   avaimia, ja saman numeron sisällä ryhmän 0 avaimet ennen ryhmän 1
   avaimia.
3. **Hajautus**: jokainen avain kirjoitetaan paikkaan, joka on parin
   aloituspaikka plus samaa numeroa olevien aiempien avainten määrä
   työryhmässä.

![Yksi kierros kahdeksalle avaimelle, numerona avaimen kaksi alinta
bittiä. Saman numeron avaimet säilyttävät keskinäisen järjestyksensä
(13, 9 ja 5 lokerossa 1), mikä tekee kierroksesta
vakaan.](kuvat/07-kantaluku.png){width=95%}

```{.glsl tiedosto="esimerkit/varjostimet/radix_laske.comp" osa="laske"}
```

Vaihe 2 on luvun 5 monitasoinen skannaus sellaisenaan. Vaihe 3 vaatii
jokaiselle avaimelle sen *sijan* työryhmän samannumeroisten avainten
joukossa, ja vakaus edellyttää, että sija noudattaa avainten
järjestystä. Sija lasketaan aliryhmän äänestyksellä: `subgroupBallot`
antaa bittimaskin kaistoista, joilla on sama numero, ja
`subgroupBallotExclusiveBitCount` laskee omaa kaistaa edeltävät bitit.
Aiempien aliryhmien määrät haetaan jaetusta muistista:

```{.glsl tiedosto="esimerkit/varjostimet/radix_hajota.comp" osa="sija"}
```

Tämä olettaa, että aliryhmät ovat työryhmän peräkkäisiä säikeitä.
Luvun 3 esimerkki tarkisti sen lavapipelle. Silmukka 16 numeron yli
on tasainen, eli kaikki kaistat kulkevat sen yhtä aikaa, kuten
aliryhmäoperaatiot vaativat.

Isännällä kierrokset ajavat dataa vuorotellen puskurista A puskuriin B
ja takaisin. Kuvaajajoukot molempiin suuntiin luodaan kerran:

```{.cpp tiedosto="esimerkit/07-kantaluku.cpp" osa="lajittelija"}
```

Vakaus testataan erikseen. Avaimen yläbitit ovat lajitteluavain ja
alabitit alkuperäinen järjestys. Kun lajitellaan vain yläbittien
mukaan, tuloksen on oltava sama kuin `std::stable_sort`-funktiolla:

```{.cpp tiedosto="esimerkit/07-kantaluku.cpp" osa="vakaus"}
```

```{.tuloste tiedosto="esimerkit/07-kantaluku.odotettu"}
```

Jokainen kierros on viisi ajoa: laskenta, kolme skannausajoa ja
hajautus. Jokainen kierros lukee datan kahdesti ja kirjoittaa sen
kerran. Liukuluvut lajitellaan samalla tavalla, kun niiden bitit
muunnetaan ensin niin, että kokonaislukujärjestys vastaa
liukulukujärjestystä: positiivisilta käännetään merkkibitti ja
negatiivisilta kaikki bitit. Avain–arvo-parien lajittelussa arvot
kulkevat avainten mukana omassa puskurissaan.

Tuotantotason toteutukset (CUB, Onesweep, FidelityFX Parallel Sort)
käyttävät 8 bitin numeroita ja käsittelevät useita avaimia säiettä
kohden, jolloin kierroksia on neljä ja muistiliikennettä vähemmän.
Hajautus kirjoittaa avaimet ensin jaettuun muistiin numeron mukaan
järjestettyinä, jotta globaalin muistin kirjoitukset osuvat
peräkkäisiin osoitteisiin (luku 8).

## Primitiivit yhdessä: naapurihaku ruudukolla

Kokonaiset GPU-algoritmit kootaan tähän asti opituista osista.
Tavallinen esimerkki on hiukkassimulaation naapurihaku: jokaisen
hiukkasen on löydettävä ne hiukkaset, jotka ovat enintään etäisyyden
$h$ päässä. Kaikkien parien vertailu on $O(n^2)$, mutta tasainen
ruudukko, jonka ruudun sivu on $h$, rajaa haun hiukkasen omaan ja
viereisiin ruutuihin. Ruudukko rakennetaan neljällä ajolla:

1. **Kartta**: jokainen säie laskee hiukkasensa ruudun numeron
   (kuten SAXPY, luku 2).
2. **Lajittelu**: hiukkaset lajitellaan ruudun numeron mukaan
   kantalukulajittelulla, jolloin saman ruudun hiukkaset ovat
   taulukossa peräkkäin.
3. **Histogrammi ja skannaus**: ruutujen hiukkasmäärien poissulkeva
   skannaus antaa jokaisen ruudun aloituspaikan lajitellussa
   taulukossa (luvut 5 ja 6).
4. **Haku**: jokainen säie käy läpi oman ruutunsa ja kahdeksan
   (kolmessa ulottuvuudessa 26) naapuriruutua aloituspaikkojen avulla.

Vaiheiden välillä on riippuvuus työryhmien yli, joten jokainen on oma
ajonsa (luku 9). Sama rakenne, avaimen laskenta, lajittelu ja
aloituspaikkojen skannaus, toistuu törmäystunnistuksessa, valojen
jakamisessa ruutuihin ja kiihdytysrakenteiden rakentamisessa.

## Käytännössä

- **Kantalukulajittelu suurille taulukoille, verkot pienille.**
  Kantalukulajittelu skaalautuu lineaarisesti, mutta sen kiinteä hinta
  (kierrokset ja skannaukset) on suuri. Muutaman tuhannen alkion
  lajittelu tehdään yhdessä työryhmässä verkolla jaetussa muistissa.
- **Lajittele avaimia, ei rakenteita.** Lajittele avaimet ja indeksit
  ja järjestä data indeksien mukaan vasta lopuksi tai ei ollenkaan.
  Suurten rakenteiden siirtely joka kierroksella kuluttaa kaistaa.
- **Testaa vakaus erikseen.** Kantalukulajittelu on oikein vain, jos
  jokainen kierros on vakaa. Virhe näkyy vasta, kun samaa numeroa
  olevia avaimia on paljon.
- **Käytä kirjastoa, kun voit.** Lajittelu on GPU:n viritetyimpiä
  algoritmeja. Oma toteutus kannattaa, kun lajittelu on osa suurempaa
  putkea, kuten läpinäkyvien pintojen järjestys tai hiukkasten
  ryhmittely ruuduittain.

## Itsearviointi

- Osaat kuvata, miten ruudukkopohjainen naapurihaku kootaan kartasta,
  lajittelusta, histogrammista ja skannauksesta.
- Osaat toteuttaa bitonisen lajitteluverkon ajoina ja jaetussa
  muistissa sekä laskea sen askeleet ja työn.
- Osaat selittää, miksi lajitteluverkot sopivat GPU:lle, vaikka ne
  tekevät enemmän työtä kuin vertailulajittelu.
- Osaat rakentaa kantalukulajittelun kierroksen laskennasta,
  skannauksesta ja hajautuksesta ja selittää, miksi kierroksen on
  oltava vakaa.
- Osaat laskea vakaan sijan aliryhmäoperaatioilla ja testata
  lajittelun vakauden.
