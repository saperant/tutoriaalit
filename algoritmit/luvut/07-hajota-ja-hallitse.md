# Hajota ja hallitse

*Hajota ja hallitse* (engl. divide and conquer) ratkaisee tehtävän
kolmessa vaiheessa:

1. **Hajota:** jaa tehtävä pienempiin samanlaisiin osatehtäviin.
2. **Hallitse:** ratkaise osatehtävät rekursiivisesti. Riittävän pienet
   ratkaistaan suoraan (*perustapaus*).
3. **Yhdistä:** muodosta osien ratkaisuista koko tehtävän ratkaisu.

Lomituslajittelu on menetelmän perusesimerkki: hajotus on tyhjä,
osatehtäviä on kaksi, ja yhdistäminen on lomitus. Pikalajittelussa työ
on hajotuksessa ja yhdistäminen tyhjä. Binäärihaussa osatehtäviä on
vain yksi.

Algoritmin aikavaativuus on rekursioyhtälö $T(n) = a\,T(n/b) + f(n)$,
jossa $a$ on osatehtävien määrä, $n/b$ niiden koko ja $f(n)$ hajotuksen
ja yhdistämisen työ. Diskreetin matematiikan luvun 7 master-lause
ratkaisee sen vertaamalla $f(n)$:ää lehtien määrään $n^{\log_b a}$.
Rekursiopuu kertoo saman havainnollisesti: kun jokaisen tason työ
on sama, kokonaistyö on tasojen määrä kertaa tason työ. Kun lehtiä on
paljon, työ on lehdissä.

Menetelmä kannattaa, kun yhdistäminen on halvempaa kuin tehtävän
ratkaiseminen suoraan. Tämän luvun kaksi esimerkkiä ovat juuri
tällaisia: kummassakin suora ratkaisu on neliöllinen, ja nokkela
yhdistäminen tekee siitä nopeamman.

## Inversioiden laskeminen

Kaksi käyttäjää on järjestänyt samat kahdeksan elokuvaa
mieltymystensä mukaan. Kuinka erilaiset listat ovat? Luonteva mitta
on niiden elokuvaparien määrä, jotka käyttäjät ovat järjestäneet eri
tavoin. Kun elokuvat numeroidaan ensimmäisen käyttäjän järjestyksen
mukaan, toisen käyttäjän listassa jokainen tällainen pari on
*inversio*: pari $i < j$, jossa $a_i > a_j$. Mitta on Kendallin
etäisyys, ja sitä käytetään suosittelujärjestelmissä ja hakutulosten
vertailussa.

Suora laskenta käy läpi kaikki parit, $\Theta(n^2)$. Hajota ja hallitse
-ratkaisu laskee inversiot lomituslajittelun yhteydessä. Inversio on
joko kokonaan vasemmassa puoliskossa, kokonaan oikeassa tai puoliskojen
välillä. Kaksi ensimmäistä lasketaan rekursiivisesti. Puoliskojen
väliset ovat helppoja laskea lomituksessa: kun oikean puoliskon
alkio siirretään tulokseen, se on pienempi kuin kaikki vasemman
puoliskon jäljellä olevat alkiot, ja jokainen niistä muodostaa sen
kanssa inversion.

```{.c tiedosto="esimerkit/07-inversiot.c" osa="inversiot"}
```

```{.tuloste tiedosto="esimerkit/07-inversiot.odotettu"}
```

Lisäys yhdistämisvaiheeseen on vakioaikainen, joten koko algoritmi on
lomituslajittelun tavoin $\Theta(n \log n)$. Funktio lajittelee
taulukon sivuvaikutuksena; jos alkuperäinen järjestys tarvitaan,
lasketaan kopiosta. Raaka vertailu laskee inversiot suoraan kaikista
pareista 20 satunnaisesta taulukosta, joiden pituus on enintään 3000.
Pieni arvoalue (0–999) varmistaa, että mukana on paljon yhtä suuria
alkioita. Yhtä suuret eivät ole inversioita, ja siksi lomituksen
ehto on `<=`: jos se olisi `<`, yhtä suuret laskettaisiin väärin.

Inversioiden määrä on myös lisäyslajittelun työ (luku 3) ja
kuplalajittelun vaihtojen määrä. Lähes järjestetyn datan
"järjestyksessä olemisen" voi siis mitata ennen kuin lajittelija
valitaan.

## Karatsuban kertolasku

Kahden $n$-numeroisen luvun kertominen koulumenetelmällä vaatii $n^2$
numeroparin kertolaskua. Pitkään oletettiin, että parempi ei ole
mahdollista, kunnes Anatoli Karatsuba keksi vuonna 1960 menetelmän,
joka tarvitsee kolme puolikkaan kokoista kertolaskua neljän sijaan.

Jaetaan luvut puolikkaisiin: $a = a_1 \cdot 10^m + a_0$ ja
$b = b_1 \cdot 10^m + b_0$. Silloin

$$a b = a_1 b_1 \cdot 10^{2m} + (a_1 b_0 + a_0 b_1) \cdot 10^m + a_0 b_0.$$

Suoraan laskettuna tarvitaan neljä tuloa. Karatsuban oivallus on, että
keskimmäinen termi saadaan kahdesta muusta ja yhdestä uudesta
tulosta: $a_1 b_0 + a_0 b_1 = (a_0 + a_1)(b_0 + b_1) - a_0 b_0 -
a_1 b_1$. Yhteen- ja vähennyslaskut ovat lineaarisia, joten

$$T(n) = 3\,T(n/2) + \Theta(n) = \Theta(n^{\log_2 3}) \approx
\Theta(n^{1{,}585}).$$

```{.c tiedosto="esimerkit/07-karatsuba.c" osa="karatsuba"}
```

Luvut ovat numerotaulukoita vähiten merkitsevä numero ensin, ja
välivaiheiden "numerot" saavat kasvaa yli yhdeksän tai olla
negatiivisia. Siirtonumerot käsitellään vasta lopuksi kerran koko
tulolle. Tämä pitää rekursion yksinkertaisena: tulo on tavallinen
polynomien tulo, ja vasta lopuksi kerroin muutetaan numeroiksi.
Tulos kirjoitetaan suoraan kutsujan taulukkoon niin, että $z_0$ on
alku- ja $z_2$ loppupuoliskossa, ja $z_1$ lisätään niiden päälle
keskelle.

```{.tuloste tiedosto="esimerkit/07-karatsuba.odotettu"}
```

Karatsuban kertolaskujen määrä on tarkalleen $16 \cdot 3^{\log_2 n -
2}$, koska perustapaus kertoo neljän numeron luvut koulumenetelmällä
16 kertolaskulla. Suhde kasvaa koko ajan: 4096 numerolla Karatsuba
tekee 18 kertaa vähemmän kertolaskuja. Jokainen tulo tarkistetaan
koulumenetelmää vastaan.

Perustapauksen koko on tärkeä vakiokerroin. Rekursio, yhteenlaskut ja
muistinvaraukset maksavat, joten pienillä luvuilla koulumenetelmä on
nopeampi. Todelliset kirjastot, kuten GMP, käyttävät koulumenetelmää
muutamaan kymmeneen konesanaan asti, Karatsubaa sen yli ja vielä
suuremmille luvuille Toom–Cookia ja FFT:hen perustuvia menetelmiä.
Sama kuvio toistuu Strassenin matriisikertolaskussa: seitsemän
puolikkaan kokoista matriisituloa kahdeksan sijaan antaa
$\Theta(n^{\log_2 7}) \approx \Theta(n^{2{,}81})$.

Karatsuban kaltaiset algoritmit ovat tärkeitä kryptografiassa, jossa
RSA:n ja elliptisten käyrien laskenta on tuhansien bittien lukujen
kertolaskua.

## Rekursio käytännössä

Rekursiivinen ratkaisu on usein selkein tapa kirjoittaa hajota ja
hallitse -algoritmi, mutta sillä on kolme hintaa:

- **Pino.** Tasapainoisen jaon syvyys on $\log_2 n$, mikä ei ole
  ongelma. Epätasainen jako, kuten pikalajittelun pahin tapaus, voi
  olla $n$ syvä ja kaataa ohjelman.
- **Kutsujen hinta.** Funktiokutsu, paluu ja parametrit maksavat
  enemmän kuin muutama vertailu, joten perustapaus kannattaa tehdä
  suuremmaksi kuin yksi alkio.
- **Muisti.** Jokaisessa kutsussa tehtävä varaus kertautuu
  rekursiopuun solmujen määrällä. Lomituslajittelun aputaulukko
  varattiin siksi kerran (luku 3); Karatsuba varaa väliaikaiset
  taulukot jokaisessa kutsussa, mikä on yksinkertaistus.

Rekursion voi aina muuttaa silmukaksi omalla pinolla, ja
lomituslajittelun voi kirjoittaa alhaalta ylös: ensin lomitetaan
yhden alkion jaksot pareiksi, sitten parit neljän jaksoiksi ja niin
edelleen. Alhaalta ylös -versiossa ei ole rekursiota lainkaan.

## Käytännössä

- **Kirjoita rekursioyhtälö ennen koodia.** Osatehtävien määrä, niiden
  koko ja yhdistämisen hinta kertovat master-lauseella heti, kannattaako
  jako.
- **Yhdistämisen on oltava halpaa.** Inversioiden laskeminen ja
  Karatsuba ovat nopeita, koska yhdistäminen on lineaarista. Jos
  yhdistäminen on yhtä kallista kuin suora ratkaisu, jako ei auta.
- **Tee perustapauksesta riittävän suuri.** Pienille osatehtäville suora
  menetelmä on nopeampi; raja kannattaa mitata.
- **Laske ensin, varaa kerran.** Väliaikainen muisti varataan
  mieluiten kerran koko rekursiolle.
- **Vertaa suoraan ratkaisuun.** Neliöllinen suora ratkaisu on paras
  testireferenssi nopealle hajota ja hallitse -algoritmille.

## Itsearviointi

- Osaat kuvata hajota ja hallitse -menetelmän kolme vaihetta ja
  kirjoittaa algoritmin rekursioyhtälön.
- Osaat laskea inversiot $\Theta(n \log n)$-ajassa lomituksen
  yhteydessä ja perustella, miksi puoliskojen väliset inversiot saadaan
  lomituksessa.
- Osaat johtaa Karatsuban kolmen tulon kaavan ja sen aikavaativuuden
  $\Theta(n^{\log_2 3})$.
- Osaat kertoa rekursion hinnat ja keinot niiden hallitsemiseen.
