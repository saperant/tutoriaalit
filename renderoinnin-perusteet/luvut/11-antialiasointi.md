# Reunanpehmennys

Rasteroija testaa vain pikselin keskipisteen. Pikseli, jonka kolmio
peittää 49-prosenttisesti, jää tyhjäksi, ja 51-prosenttisesti peitetty
täyttyy kokonaan. Vinot reunat muuttuvat portaiksi, ohuet kappaleet
katkeilevat, ja liikkuvan reunan portaat vaeltavat. Tämä on samaa
aliasointia kuin tekstuureissa, mutta sitä ei voi suodattaa etukäteen,
koska reuna syntyy vasta rasteroinnissa. Ratkaisuna on ottaa
pikselistä useampi näyte: **reunanpehmennys** (antialiasing, AA).

## Ylinäytteistys

**Ylinäytteistys** (supersampling, SSAA) renderöi kuvan suurempana ja
pienentää sen keskiarvoistamalla. Kaksinkertainen resoluutio kumpaankin
suuntaan antaa neljä näytettä pikseliä kohden ja tasoittaa reunan
viiteen kirkkaustasoon. Keskiarvo lasketaan lineaarisilla arvoilla,
kuten kaikki muukin sekoitus:

```{.cpp tiedosto="esimerkit/yhteinen/putki.hpp" osa="kohde"}
```

SSAA on yksinkertainen ja korjaa kaiken aliasoinnin: reunat,
tekstuurit, kiiltopisteet ja ohuet kappaleet. Hinta on suora: neljä
näytettä tarkoittaa neljä kertaa enemmän fragmenttivarjostimen
suorituksia ja neljä kertaa suuremman puskurin. Luvun *Tekstuurit*
vertailukuva ja seuraavan luvun kohtaus on renderöity näin.

## Näytekuviot

Näytteiden paikoilla on väliä. Säännöllinen $n \times n$ -ruudukko
antaa vaakasuoralle tai pystysuoralle reunalle vain $n + 1$
kirkkaustasoa, vaikka näytteitä on $n^2$. Lähes vaakasuorat reunat,
joissa porrastus näkyy eniten, hyötyvät siksi eniten **kierretystä
kuviosta** (rotated grid), jossa jokainen näyte on eri rivillä ja eri
sarakkeella. Neljä kierrettyä näytettä antaa vaaka- ja pystyreunoille
viisi tasoa, saman verran kuin $4 \times 4$ -ruudukko neljänneksellä
sen näytteistä. $2 \times 2$ -ruudukko antaa vain kolme.

![Näytteiden paikat pikselin sisällä. Oikean reunan merkit näyttävät,
kuinka monella eri korkeudella näytteitä on: yhtä monessa portaassa
vaakasuora reuna voi liukua pikselin
yli.](kuvat/11-naytekuviot.png){width=75%}

```{.cpp tiedosto="esimerkit/11-antialiasointi.cpp" osa="naytteet"}
```

## Moninäytteistys

**Moninäytteistys** (multisample AA, MSAA) erottaa peiton ja
varjostuksen. Peittotesti ja syvyystesti tehdään jokaisessa
näytteessä, mutta fragmenttivarjostin suoritetaan vain kerran
pikseliä ja kolmiota kohden, ja sen tulos kirjoitetaan kaikkiin
peitettyihin näytteisiin. Lopuksi näytteet keskiarvoistetaan
(**resolve**). Reunat pehmenevät kuten ylinäytteistyksessä, mutta
varjostus maksaa lähes saman kuin ilman reunanpehmennystä; vain
reunapikselit, joissa on useampi kolmio, varjostetaan useaan kertaan.

Esimerkki mittaa kolmion peiton virheen eri tavoilla. Tarkka peitto
lasketaan 256 näytteellä pikseliä kohden, ja varjostuskertojen määrä
kertoo hinnan:

```{.cpp tiedosto="esimerkit/11-antialiasointi.cpp" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/11-antialiasointi.odotettu"}
```

![Kolmion peitto pikselin kirkkautena, kahdeksankertaisesti
suurennettuna. Ylhäällä ilman reunanpehmennystä ja SSAA 2 × 2,
alhaalla SSAA 4 × 4 ja MSAA neljällä kierretyllä
näytteellä.](kuvat/11-antialiasointi.png){width=85%}

Ilman reunanpehmennystä suurin virhe on 0,66: reunapikseli, josta
kaksi kolmasosaa on kolmion sisällä, jää tyhjäksi. $2 \times 2$
-ruudukko pudottaa keskivirheen kolmannekseen ja $4 \times 4$
kymmenesosaan, mutta varjostuskerrat nelin- ja kuusitoistakertaistuvat.
Neljän kierretyn näytteen MSAA on keskivirheeltään parempi kuin
$2 \times 2$ -ruudukko ja varjostaa vain 238 kertaa: jokainen kolmion
pikseli kerran, mukaan lukien 30 reunapikseliä, joita yksi näyte ei
tavoittanut. Merkkikuvassa reunat ovat porrastuksen sijaan liukuvia
sävyjä.

MSAA ei pehmennä varjostuksen sisäistä aliasointia: välkkyvä tekstuuri
tai terävä kiiltopiste kolmion keskellä näytetään edelleen yhdellä
näytteellä. Siksi tekstuurit tarvitsevat mipmapit myös MSAA:n kanssa.
MSAA:n puskurit ovat myös suuria, ja se sopii huonosti viivästettyyn
varjostukseen (deferred shading), jossa valaistus lasketaan
myöhemmin erillisistä puskureista.

## Jälkikäsittely ja ajallinen pehmennys

Nykyiset pelit käyttävät usein menetelmiä, jotka toimivat valmiilla
kuvalla:

- **FXAA ja SMAA** etsivät kuvasta reunoja kirkkauseroista ja
  sumentavat niitä reunan suuntaisesti. Ne ovat halpoja mutta eivät
  tiedä alipikselin geometriasta, joten ohuet kappaleet katkeilevat
  edelleen.
- **TAA** (temporal AA) siirtää kameraa joka ruudulla hieman
  alipikselin verran ja yhdistää uuden kuvan edellisiin. Ajan mittaan
  pikseli saa kymmeniä näytteitä yhden hinnalla. Liikkuvien
  kappaleiden kohdalla vanhat näytteet on siirrettävä liikevektoreilla
  tai hylättävä, muuten syntyy haamukuvia.
- **Skaalaavat menetelmät** (DLSS, FSR, XeSS) yhdistävät ajallisen
  pehmennyksen ja kuvan suurentamisen: kuva renderöidään pienempänä ja
  rekonstruoidaan näyttöresoluutioon.

Kaikkien taustalla on sama ajatus kuin tässä luvussa: yksi näyte
pikselin keskeltä ei riitä, ja lisänäytteet hankitaan tilasta, ajasta
tai molemmista.

## Käytännössä

- **MSAA geometrian reunoille** silloin, kun putki on suora
  (forward rendering) ja puskurimuisti riittää; mipmapit ja suodatus
  hoitavat tekstuurit.
- **SSAA vertailukuviin ja laadukkaisiin kuvakaappauksiin**, kun
  aikaa on.
- **Keskiarvoista lineaarisilla arvoilla.** sRGB-arvojen keskiarvo
  tekee pehmennetyistä reunoista liian tummia.
- **Kierretty kuvio** antaa enemmän tasoja lähes vaakasuorille
  reunoille kuin säännöllinen ruudukko samalla näytemäärällä.
- **Jälkikäsittely ja TAA** ovat halpoja mutta tuovat sumeutta ja
  haamukuvia; ne tarvitsevat liikevektorit ja huolellista viritystä.

## Itsearviointi

- Osaat selittää, mistä porrastus syntyy ja miksi se on aliasointia.
- Osaat kuvata ylinäytteistyksen ja moninäytteistyksen eron ja niiden
  kustannukset.
- Osaat perustella, miksi kierretty näytekuvio on parempi kuin
  säännöllinen ruudukko.
- Osaat kertoa, mitä MSAA ei korjaa ja mitä jälkikäsittely- ja
  ajalliset menetelmät tekevät.
