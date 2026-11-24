# Mittaaminen

Mittaus vastaa kysymykseen ”kuinka kauan tämä kestää”, mutta vastaus
on luotettava vain, jos kello, toistot ja olosuhteet on valittu
oikein. Tässä luvussa rakennetaan pieni mittauskirjasto ja käydään
läpi tavallisimmat virheet: väärä kello, liian vähän toistoja,
keskiarvo mediaanin sijaan ja laskenta, jonka kääntäjä on poistanut.

## Kaksi kelloa

Seinäkello mittaa todellista kulunutta aikaa, prosessiaika suorittimella
kulunutta aikaa. POSIXin `clock_gettime` antaa molemmat nanosekunnin
tarkkuudella:

```{.c tiedosto="esimerkit/mittari.h" osa="kellot"}
```

`CLOCK_MONOTONIC` ei hyppää, kun kellonaikaa säädetään (NTP,
kesäaika), joten sitä käytetään aikavälien mittaamiseen.
`CLOCK_REALTIME` on kellonaika, eikä se sovi mittaamiseen.
`CLOCK_PROCESS_CPUTIME_ID` laskee vain ajan, jonka prosessin säikeet
ovat olleet suorittimella. Ero näkyy, kun ohjelma odottaa:

```{.c tiedosto="esimerkit/02-kellot.c" osa="testi"}
```

```{.tuloste tiedosto="esimerkit/02-kellot.odotettu"}
```

Nukkuessa seinäkello kulkee mutta prosessiaika ei. Laskiessa ne
kulkevat yhtä matkaa. Monisäikeisessä ohjelmassa prosessiaika voi
olla seinäkelloaikaa suurempi, koska se on kaikkien säikeiden summa.
Käyttäjälle merkitsee seinäkello; prosessiaika kertoo, paljonko
laskentakapasiteettia kului. Jos seinäkello on paljon prosessiaikaa
suurempi, ohjelma odottaa jotain: levyä, verkkoa, lukkoa tai muistia,
joka on sivutettu ulos.

Kellon tarkkuus ja hinta kannattaa tietää ennen kuin mittaa lyhyitä
asioita:

```{.tuloste tiedosto="esimerkit/tulokset/02-kellot.txt"}
```

Tarkkuus on nanosekunti, mutta kellon lukeminen maksaa itsessään
kymmeniä nanosekunteja tässä virtuaalikoneessa (fyysisellä koneella
tavallisesti 15–25 ns). Alle mikrosekunnin mittaiset asiat mitataan
siksi toistamalla niitä silmukassa ja jakamalla kokonaisaika
toistojen määrällä.

## Toistot ja tilastot

Yksittäinen mittaus on satunnaismuuttujan yksi arvo. Ajoon vaikuttavat
muut prosessit, keskeytykset, suorittimen kellotaajuuden säätö,
välimuistien ja TLB:n tila, muistin sivujen sijoittuminen ja jopa
ympäristömuuttujien pituus, joka siirtää pinon osoitetta. Mittaus
toistetaan siis monta kertaa ja tuloksista lasketaan tilasto.

```{.c tiedosto="esimerkit/mittari.h" osa="tilasto"}
```

Häiriöt tekevät ajasta aina pidemmän, eivät koskaan lyhyempää. Siksi
jakauma on vino: suurin osa mittauksista on lähellä pienintä arvoa, ja
muutama on paljon pidempi. Keskiarvo on herkkä näille poikkeamille,
mediaani ei:

```{.c tiedosto="esimerkit/02-toistot.c" osa="testi"}
```

```{.tuloste tiedosto="esimerkit/02-toistot.odotettu"}
```

Yksi keskeytyksen pidentämä mittaus siirtää keskiarvoa kaksi
millisekuntia, mutta mediaani ja MAD (mediaanin absoluuttinen
poikkeama) eivät juuri muutu. Pienin arvo on hyvä arvio siitä, mihin
ohjelma pystyy ihanteellisissa oloissa, ja mediaani siitä, mitä
tyypillinen ajo kestää. Raportissa kannattaa kertoa molemmat sekä
hajonta. Jos kahden version mediaanien ero on pienempi kuin hajonta,
eroa ei ole osoitettu.

## Lämmittely

Ensimmäinen ajo on erityinen. Koodi ja data eivät ole välimuisteissa,
muistisivut voivat olla vielä varaamatta, dynaaminen linkkeri
ratkaisee kirjastofunktioiden osoitteita ja suoritin voi olla
virransäästötilassa. Mittausfunktio ajaa siksi mitattavan kerran
ennen varsinaisia toistoja:

```{.c tiedosto="esimerkit/mittari.h" osa="mittaa"}
```

Mitattava annetaan funktio-osoittimena ja sen tila tietueena. Kutsu
funktio-osoittimen kautta maksaa muutaman nanosekunnin, mikä ei
haittaa millisekuntien mittauksia. Kylmän ja lämpimän ajon eron näkee,
kun välimuistit tyhjennetään ensin toisella suurella taulukolla:

```{.c tiedosto="esimerkit/02-toistot.c" osa="kylma"}
```

```{.tuloste tiedosto="esimerkit/tulokset/02-toistot.txt"}
```

Kylmä ajo kesti moninkertaisesti mediaanin verran. Kumpi luku on
oikea, riippuu käytöstä. Palvelimen kuuma polku ajetaan miljoonia
kertoja, ja sitä kuvaa lämmin luku. Komentorivityökalu käynnistyy
kerran ja käsittelee tiedoston kerran, ja sitä kuvaa kylmä luku. Mittaa
se, mitä käyttäjä kokee.

## Kääntäjä poistaa mitattavan

Optimoiva kääntäjä saa poistaa laskennan, jonka tulosta ei käytetä,
koska ohjelman havaittava käytös ei muutu. Tavallinen mittausvirhe
näyttää tältä:

```{.c tiedosto="esimerkit/02-poistettu.c" osa="vaarin"}
```

Kääntäjä näkee, että `summa` ei kirjoita muistiin eikä kutsu mitään, ja
koska tulos hylätään, koko silmukka katoaa. Korjaus on käyttää tulos
tavalla, jota kääntäjä ei voi todistaa tarpeettomaksi:

```{.c tiedosto="esimerkit/02-poistettu.c" osa="oikein"}
```

```{.c tiedosto="esimerkit/mittari.h" osa="kayta"}
```

```{.tuloste tiedosto="esimerkit/tulokset/02-poistettu.txt"}
```

Nolla millisekuntia on aina epäilyttävä tulos. Sama ilmiö on
hienovaraisempi, kun kääntäjä laskee osan työstä käännösaikana
(vakiosyöte), siirtää laskennan pois silmukasta tai yhdistää kaksi
mitattavaa kierrosta. Mikrovertailun syötteen kannattaa siksi tulla
ohjelman ulkopuolelta tai satunnaisgeneraattorista. `kayta` vastaa
C++-vertailukirjastojen (Google Benchmark, nanobench)
`DoNotOptimize`-funktiota.

## Mikro- ja makrovertailut

*Mikrovertailu* mittaa yhtä funktiota tai silmukkaa eristettynä.
*Makrovertailu* mittaa koko ohjelmaa todellisella kuormalla. Ne
vastaavat eri kysymyksiin, ja kumpikin voi johtaa harhaan:

| Vertailu | Hyvä | Sudenkuoppa |
|------------|--------------------------------|--------------------------------------|
| Mikro | Nopea iteroida, pieni kohina, kertoo yhden asian | Data on aina välimuistissa ja haarat opittuja; todellisuudessa ei |
| Makro | Mittaa sen, mikä merkitsee | Kohinainen; ei kerro, mikä osa muuttui |

Mikrovertailu, jossa sama 4 KiB taulukko käsitellään miljoona kertaa,
mittaa L1-välimuistin nopeutta. Jos todellinen ohjelma koskee
funktioon kerran sekunnissa, data tulee muistista ja tulos on
täysin toinen. Tee mikrovertailuja hypoteesin testaamiseen, mutta
tarkista lopputulos makrovertailulla.

## Mittausympäristö

Kohinaa voi vähentää, mutta ei poistaa:

- Sulje muut kuormittavat ohjelmat. Kannettavassa kytke laturi, koska
  akkukäytöllä suoritin hidastaa.
- Linuxissa suorittimen taajuuden säätäjän voi asettaa tilaan
  `performance` (`cpupower frequency-set -g performance`) ja
  turbotilan pois, jotta taajuus ei vaihtele lämpötilan mukaan.
- Sido mittaus yhteen ytimeen (`taskset -c 2 ./ohjelma`), jotta
  käyttöjärjestelmä ei siirrä sitä ytimeltä toiselle.
- Toista koko vertailu useaan kertaan eri järjestyksessä. Jos A
  mitataan aina ennen B:tä, B saa lämpimät välimuistit ja A
  lämmittelyn haitat.

Virtuaalikoneessa ja pilvessä ympäristöä ei hallitse: muut asiakkaat
jakavat saman fyysisen koneen. Silloin tarvitaan enemmän toistoja,
mediaaneja ja deterministisiä mittareita, kuten Valgrindin
käskymääriä (luku 4).

## Käytännössä

- **Mittaa seinäkelloa `CLOCK_MONOTONIC`-kellolla**, ja vertaa
  prosessiaikaan, kun epäilet odottamista.
- **Toista ja raportoi mediaani, pienin arvo ja hajonta.** Yksittäinen
  mittaus ei ole tulos.
- **Lämmitä tai mittaa kylmänä tietoisesti.** Kerro, kumpi luku on.
- **Varmista, että mitattava tapahtuu.** Nollan lähellä oleva aika
  tarkoittaa yleensä, että kääntäjä poisti työn.
- **Mittaa sama asia aina samalla tavalla** ennen muutosta ja sen
  jälkeen: sama syöte, sama kone, samat liput.
- **Säilytä mittausohjelma.** Kun koodi muuttuu vuoden päästä, sama
  mittaus kertoo, palasiko hitaus.

## Itsearviointi

- Osaat valita seinäkellon ja prosessiajan välillä ja selittää, mitä
  niiden ero kertoo.
- Osaat perustella, miksi mediaani on keskiarvoa parempi aikojen
  tunnusluku, ja laskea MAD-arvon.
- Osaat kirjoittaa mittauksen, josta kääntäjä ei poista mitattavaa
  laskentaa.
- Osaat selittää, miksi ensimmäinen ajo on muita hitaampi ja milloin
  juuri se on oikea mittaus.
- Osaat luetella mittausten kohinan lähteitä ja keinoja vähentää niitä.
