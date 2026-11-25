# Viivat

**Rasterointi** on jatkuvan muodon muuttamista pikseleiksi: mitkä
ruudukon pikselit kuuluvat viivaan tai kolmioon? Viiva on
yksinkertaisin tapaus, ja siinä näkyvät jo kaikki rasteroinnin
teemat: pyöristys, symmetria ja se, että sama pikseli ei saa riippua
siitä, mihin suuntaan viiva piirretään.

Viivoja käytetään rautalankamalleissa, virheenjäljityksessä (normaalit,
rajaavat laatikot, kameran näkökartio) ja käyttöliittymissä.
Näytönohjaimet piirtävät nykyään viivat yleensä ohuina kolmioina, mutta
ohjelmistossa suora algoritmi on yksinkertaisempi.

## Pikselin keskipiste

Pikseli on pieni neliö, ja sen **keskipiste** on kohdassa
$(x + 0{,}5,\; y + 0{,}5)$. Rasterointisäännöt kysyvät, kuuluuko
keskipiste muotoon. Sopimus kuulostaa pikkutarkalta, mutta ilman sitä
kaksi vierekkäistä kolmiota eivät sovi saumattomasti yhteen eikä
skaalattu kuva pysy paikallaan. Sama sopimus on OpenGL:ssä,
Direct3D 10:stä lähtien ja Vulkanissa.

Viivassa sopimus tarkoittaa, että jokaisella pidemmän akselin
sarakkeella valitaan se pikseli, jonka keskipiste on lähimpänä ideaalia
suoraa.

## DDA

Suorin tapa on kulkea pidemmän akselin suuntaan pikseli kerrallaan ja
laskea toinen koordinaatti suoran yhtälöstä. Tämä on **DDA**
(digital differential analyzer):

```{.cpp tiedosto="esimerkit/03-viivat.cpp" osa="dda"}
```

DDA on oikein, mutta se laskee liukuluvuilla ja pyöristää joka
askeleella. Vanhoilla prosessoreilla liukuluvut olivat hitaita, ja
pyöristys tekee tuloksesta riippuvaisen laskentajärjestyksestä:
kun $t \cdot (x_1 - x_0)$ on täsmälleen puolikas, liukuluvun
pyöristysvirhe ratkaisee, kumpaan suuntaan päädytään.

## Bresenhamin algoritmi

Jack Bresenham huomasi vuonna 1965, että koko viivan voi piirtää
kokonaisluvuilla. Algoritmi pitää kirjaa virheestä, eli siitä, kuinka
kaukana valittu pikseli on ideaalista suorasta, skaalattuna niin, että
kaikki suureet ovat kokonaislukuja. Joka askeleella valitaan se
naapuri, joka pitää virheen pienimpänä. Alla on yleinen versio, joka
toimii kaikkiin kahdeksaan suuntaan ilman erillisiä tapauksia:

```{.cpp tiedosto="esimerkit/yhteinen/rasteri.hpp" osa="bresenham"}
```

Muuttuja `virhe` on suoran implisiittisen yhtälön
$F(x, y) = |\Delta y| \, x - |\Delta x| \, y$ arvo (etumerkit
sovitettuina) siinä pikselissä, johon vinoaskel veisi. Sen kaksinkertaista
arvoa verrataan askelten hintoihin: kun `e2 >= dy`, vaakasuora askel
vie lähemmäs suoraa, ja kun `e2 <= dx`, pystysuora askel. Kun
molemmat ehdot pätevät, otetaan vinoaskel. Askeleen jälkeen virhe
päivitetään lisäämällä askeleen hinta, joten mitään ei tarvitse laskea
uudelleen alusta. Silmukassa on
vain yhteen- ja vähennyslaskuja ja vertailuja, joten se sopii
laitteistoon ja mikro-ohjaimiin. Pelkät kokonaisluvut tekevät siitä
myös täysin toistettavan.

Lyhyen viivan askeleet näyttävät, miten y-askel tapahtuu joka toisella
sarakkeella, kun kulmakerroin on $3/7$:

```{.cpp tiedosto="esimerkit/03-viivat.cpp" osa="askeleet"}
```

## Vertailu

Seuraava ohjelma piirtää viivoja keskipisteestä joka suuntaan ja
merkitsee pikselit, joissa algoritmit eroavat: `#` on molemmissa, `B`
vain Bresenhamilla ja `D` vain DDA:lla.

```{.cpp tiedosto="esimerkit/03-viivat.cpp" osa="tahti"}
```

```{.tuloste tiedosto="esimerkit/03-viivat.odotettu"}
```

![Sama ruudukko kuvana kahdeksankertaisesti suurennettuna. Vaaleat
pikselit ovat samat molemmilla algoritmeilla, oranssit piirsi vain
Bresenham ja siniset vain DDA.](kuvat/03-viivat.png){width=70%}

Erot syntyvät vain sarakkeissa, joissa ideaali suora kulkee
täsmälleen kahden pikselin keskipisteiden puolivälistä. Silloin
kumpikin pikseli on yhtä hyvä, ja algoritmit ratkaisevat tasapelin
eri suuntiin. Viivassa kohti pistettä $(40, 0)$ kulmakerroin on
$-1/2$, joten tasapeli tulee joka toisella sarakkeella. Bresenham valitsee
aina saman puolen suhteessa *piirtosuuntaan*, joten viiva
$(20, 10) \to (40, 0)$ ja viiva $(40, 0) \to (20, 10)$ voivat erota
yhden pikselin verran. Jos samaa viivaa piirretään molempiin suuntiin
(esimerkiksi monikulmion reunat), päätepisteet kannattaa järjestää
ennen piirtoa, jotta tulos on symmetrinen.

## Paksut ja pehmeät viivat

Bresenhamin viiva on yhden pikselin levyinen ja portaikkoinen.
Pehmeissä viivoissa pikselin kirkkaus riippuu sen etäisyydestä
ideaaliin suoraan (Xiaolin Wun algoritmi) tai siitä, kuinka suuren osan
pikselistä viiva peittää. Paksu viiva on käytännössä suorakulmio, eli
kaksi kolmiota, ja sen piirtäminen palautuu seuraavan luvun
kolmiorasterointiin. Reunanpehmennystä käsitellään yleisesti luvussa
*Reunanpehmennys*.

## Käytännössä

- **Sovi pikselin keskipisteestä.** Kaikki rasterointisäännöt
  vertaavat keskipistettä $(x + 0{,}5, y + 0{,}5)$; puolen pikselin
  virheet ovat yleisin syy saumoihin ja siirtymiin.
- **Kokonaisluvut tekevät tuloksesta toistettavan.** Bresenham on
  esimerkki siitä, miten jatkuvan ongelman voi ratkaista tarkasti
  skaalaamalla suureet kokonaisluvuiksi.
- **Järjestä päätepisteet**, jos saman viivan on oltava täsmälleen
  sama kumpaankin suuntaan piirrettynä.
- **Virheenjäljitysviivat** (normaalit, rajauslaatikot, kehykset)
  ovat halvin tapa nähdä, mitä 3D-kohtauksessa tapahtuu.

## Itsearviointi

- Osaat selittää pikselin keskipisteen sopimuksen ja miksi se on
  tärkeä.
- Osaat kuvata DDA:n ja Bresenhamin algoritmin erot.
- Osaat selittää, mitä Bresenhamin virhetermi tarkoittaa ja miksi
  algoritmi tarvitsee vain kokonaislukuja.
- Osaat kertoa, milloin viivan piirtosuunta vaikuttaa tulokseen.
