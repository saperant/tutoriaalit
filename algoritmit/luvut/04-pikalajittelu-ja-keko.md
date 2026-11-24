# Pikalajittelu ja kekolajittelu

Lomituslajittelu jakaa taulukon kahtia ilman ajattelua ja tekee työn
yhdistäessään puoliskot. *Pikalajittelu* (engl. quicksort) tekee
päinvastoin: se tekee työn jakaessaan ja yhdistää ilmaiseksi. Taulukko
jaetaan *jakoalkion* (engl. pivot) mukaan pienempiin ja suurempiin,
minkä jälkeen kumpikin osa lajitellaan rekursiivisesti. Kun osat ovat
lajiteltuja, koko taulukko on lajiteltu, eikä aputaulukkoa tarvita.

Pikalajittelu on käytännössä nopein yleiskäyttöinen vertailulajittelu,
koska sen sisin silmukka on yksinkertainen ja lukee muistia peräkkäin.
Sillä on kuitenkin neliöllinen pahin tapaus, ja koko luvun aihe on,
miten se vältetään.

## Jako

Lomuton jako (Nico Lomuton mukaan) valitsee jakoalkioksi välin
viimeisen alkion ja kerää sitä pienemmät välin alkuun:

```{.c tiedosto="esimerkit/04-pika.c" osa="lomuto"}
```

Jaon invariantti on, että kierroksen alussa `a[lo..i)` on pienempiä
kuin `p` ja `a[i..j)` suurempia tai yhtä suuria. Kun `j` saavuttaa
välin lopun, jakoalkio vaihdetaan kohtaan `i`, joka on sen lopullinen
paikka lajitellussa taulukossa. Jako on $\Theta(n)$ ja tekee
täsmälleen $n - 1$ vertailua.

Hyvällä jakoalkiolla, joka jakaa välin suunnilleen kahtia, rekursio
on kuin lomituslajittelussa: $T(n) = 2\,T(n/2) + \Theta(n) =
\Theta(n \log n)$. Huonolla, joka on välin pienin tai suurin alkio,
toinen osa on tyhjä ja toinen vain yhtä lyhyempi:
$T(n) = T(n - 1) + \Theta(n) = \Theta(n^2)$.

## Pahin tapaus ja satunnainen jakoalkio

Viimeinen alkio on huonoin mahdollinen jakoalkio juuri sille
syötteelle, joka on käytännössä yleisin: valmiiksi järjestetylle.
Esimerkki mittaa vertailut ja rekursion suurimman syvyyden 2000 alkion
taulukolla:

```{.tuloste tiedosto="esimerkit/04-pika.odotettu"}
```

Järjestetty syöte ja viimeinen alkio antavat tasan $n(n-1)/2$
vertailua ja rekursiosyvyyden $n - 1$. Syvyys on yhtä vakava ongelma
kuin aika: miljoonan alkion järjestetty taulukko kaataisi ohjelman
pinon ylivuotoon.

Korjaus on valita jakoalkio satunnaisesti. Silloin mikään syöte ei ole
erityisen huono, ja vertailuja on odotusarvoisesti
$2(n+1)H_n - 4n$, missä $H_n = 1 + 1/2 + \cdots + 1/n$ on harmoninen
luku. Suurilla $n$:n arvoilla tämä on noin $1{,}39\,n \log_2 n$.
Arvolla $n = 2000$ se on noin 24 700, mikä vastaa mittausta. Satunnaisuus on tässä algoritmin, ei syötteen
ominaisuus: hyökkääjä, joka ei tunne satunnaislukujen siementä, ei voi
rakentaa hidasta syötettä. Toinen yleinen tapa on *kolmen mediaani*:
jakoalkioksi otetaan ensimmäisen, keskimmäisen ja viimeisen alkion
mediaani. Se korjaa järjestetyn syötteen, mutta sille voi rakentaa
vihamielisen syötteen.

Satunnainen jakoalkio ei auta, kun kaikki alkiot ovat samoja. Lomuton
jako laittaa yhtä suuret jakoalkion oikealle puolelle, joten jako on
aina mahdollisimman epätasainen. Sama ongelma esiintyy lievempänä
aina, kun avaimissa on paljon toistoja, esimerkiksi lajiteltaessa
miljoonaa tilausta kymmenen tilan mukaan.

## Kolmijako

Korjaus on jakaa taulukko kolmeen osaan: pienempiin, yhtä suuriin ja
suurempiin. Yhtä suuret ovat jo lopullisilla paikoillaan, eivätkä ne
osallistu rekursioon. Menetelmä tunnetaan Dijkstran hollantilaisen
lipun ongelmana:

```{.c tiedosto="esimerkit/04-pika.c" osa="kolmijako"}
```

Invariantti on `a[lo..lt) < p`, `a[lt..i) == p` ja `a(gt..hi] > p`;
väli `a[i..gt]` on käsittelemättä. Kun kaikki alkiot ovat samoja,
yksi kierros riittää: $n$ vertailua ja rekursiosyvyys 1. Erisuurilla
alkioilla kolmijako on hieman hitaampi kuin Lomuton jako, koska se
tekee enemmän vaihtoja, mutta asymptoottisesti yhtä hyvä.

Rekursiosyvyyden voi rajoittaa myös takuulla. Kun rekursio tehdään
aina lyhyempään osaan ja pidempi käsitellään silmukassa, syvyys on
enintään $\log_2 n$ jakoalkiosta riippumatta.

## Kekolajittelu

Kekolajittelu käyttää tietorakenteiden luvun 9 binäärikekoa. Taulukko
kekoutetaan maksimikeoksi, jolloin suurin alkio on indeksissä 0. Se
vaihdetaan taulukon viimeiseksi, keko lyhenee yhdellä, ja uusi juuri
lasketaan paikalleen. Toistamalla saadaan alkiot suuruusjärjestyksessä
taulukon lopusta alkuun:

```{.c tiedosto="esimerkit/04-keko.c" osa="keko"}
```

```{.tuloste tiedosto="esimerkit/04-keko.odotettu"}
```

Kekoutus on $O(n)$, ja jokainen $n - 1$ poistosta on $O(\log n)$.
Kekolajittelu on siis $O(n \log n)$ myös pahimmassa tapauksessa ja
lajittelee paikallaan ilman lisämuistia. Vertailujen määrä tuskin
riippuu syötteestä. Testi vertaa tulosta `qsort`-funktioon 300
satunnaisella taulukolla; vertailijan oikea kirjoitustapa käsitellään
luvussa 5.

Kekolajittelu ei ole vakaa, ja käytännössä se on pikalajittelua
hitaampi. Lapset ovat taulukossa kaukana vanhemmistaan, joten suurella
taulukolla lähes jokainen laskeminen hyppää välimuistin ohi. Sen
tärkein käyttö on varmistus: *introsort* aloittaa pikalajittelulla ja
vaihtaa kekolajitteluun, jos rekursio syvenee yli $2 \log_2 n$:n.
Lopuksi pienet osataulukot viimeistellään lisäyslajittelulla. Näin
saadaan pikalajittelun nopeus, kekolajittelun takuu ja
lisäyslajittelun pieni vakiokerroin. C++:n `std::sort` on tavallisesti
introsort. C-kirjastojen `qsort` vaihtelee toteutuksesta toiseen, ja
osa käyttää lomituslajittelua.

## Vertailu

| Algoritmi | Pahin | Keskimäärin | Lisämuisti | Vakaa |
|-----------|-------|-------------|------------|-------|
| lisäys | $\Theta(n^2)$ | $\Theta(n^2)$ | $O(1)$ | kyllä |
| lomitus | $\Theta(n \log n)$ | $\Theta(n \log n)$ | $\Theta(n)$ | kyllä |
| pika, satunnainen | $\Theta(n^2)$ | $\Theta(n \log n)$ | $O(\log n)$ pino | ei |
| keko | $\Theta(n \log n)$ | $\Theta(n \log n)$ | $O(1)$ | ei |
| introsort | $\Theta(n \log n)$ | $\Theta(n \log n)$ | $O(\log n)$ pino | ei |

Pikalajittelun pino on $O(\log n)$ vain, jos rekursio tehdään
lyhyempään osaan. Satunnaistetun pikalajittelun pahin tapaus on
äärimmäisen epätodennäköinen, mutta se on olemassa.

## Käytännössä

- **Käytä kirjaston lajittelua.** `qsort` ja `std::sort` ovat
  testattuja ja ottavat huomioon pahimman tapauksen. Oma lajittelu on
  perusteltu vain, kun tarvitaan ominaisuus, jota kirjasto ei lupaa,
  kuten vakaus tai laskettavat vertailut.
- **Älä ota jakoalkioksi ensimmäistä tai viimeistä alkiota.**
  Järjestetty syöte on todellisuudessa yleinen, ja se tekee
  pikalajittelusta neliöllisen ja kaataa pinon.
- **Varaudu toistoihin.** Kolmijako tekee yhtä suurista avaimista
  halvan; ilman sitä tasainen data on pahin tapaus.
- **Rajoita rekursiosyvyys.** Rekursio lyhyempään osaan ja silmukka
  pidempään takaa $O(\log n)$ pinon. Introsortin syvyysraja takaa
  myös ajan.
- **Pienet osataulukot lisäyslajittelulla.** 16–32 alkion raja on
  tavallinen, mutta oikea arvo kannattaa mitata.

## Itsearviointi

- Osaat kirjoittaa Lomuton jaon ja perustella sen invariantilla.
- Osaat selittää, miksi järjestetty syöte ja viimeinen alkio
  jakoalkiona antavat neliöllisen ajan, ja miksi satunnainen
  jakoalkio korjaa sen.
- Osaat kirjoittaa kolmijaon ja selittää, miksi se tekee yhtä
  suurten avainten syötteestä halvan.
- Osaat kuvata kekolajittelun ja introsortin sekä vertailla
  lajittelualgoritmeja ajan, muistin ja vakauden suhteen.
