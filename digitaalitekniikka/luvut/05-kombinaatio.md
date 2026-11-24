# Kombinaatiologiikan lohkot

*Kombinaatiologiikan* lähtö riippuu vain tulojen nykyisistä arvoista.
Siinä ei ole muistia eikä takaisinkytkentää. Muutama peruslohko
toistuu kaikkialla: multiplekseri valitsee, dekooderi osoittaa,
kooderi tiivistää ja vertailija päättää. Tässä luvussa ne kuvataan
SystemVerilogilla ja testataan kaikilla syötteillä.

## Multiplekseri

Multiplekseri (mux) valitsee yhden $2^k$ tulosta $k$-bittisellä
valintasignaalilla. Se on digitaalisuunnittelun yleisin lohko: jokainen
`if` ja `case` RTL-kuvauksessa on multiplekseri.

```{.systemverilog tiedosto="esimerkit/05-kombinaatio.sv" osa="mux"}
```

Porttitasolla neljän tulon mux on tulojen summa
$y = \bar{s}_1\bar{s}_0 d_0 + \bar{s}_1 s_0 d_1 + s_1\bar{s}_0 d_2 + s_1 s_0 d_3$.
Multiplekseri on myös *universaali*: $2^n$ tulon mux, jonka datatulot
ovat vakioita, toteuttaa minkä tahansa $n$ muuttujan funktion, kun
muuttujat kytketään valintaan. FPGA:n hakutaulu (LUT) on juuri tämä:
pieni muisti ja multiplekseri.

## Dekooderi ja kooderi

Dekooderi muuttaa $k$-bittisen koodin $2^k$ lähdöstä yhdeksi aktiiviseksi
(*one-hot*). Muistin osoitedekooderi valitsee rivin, käskydekooderi
ohjauslinjan.

```{.systemverilog tiedosto="esimerkit/05-kombinaatio.sv" osa="dekooderi"}
```

Kooderi tekee päinvastoin. Jos useampi tulo voi olla yhtä aikaa
aktiivinen, tarvitaan *prioriteettikooderi*, joka valitsee
merkitsevimmän. Keskeytysohjain valitsee näin tärkeimmän
keskeytyspyynnön.

```{.systemverilog tiedosto="esimerkit/05-kombinaatio.sv" osa="prioriteetti"}
```

`kelvollinen`-lähtö on tärkeä: ilman sitä indeksi 0 tarkoittaisi sekä
"pyyntö 0" että "ei pyyntöjä". Tämä on yleinen malli: dataan liitetään
bitti, joka kertoo, onko data merkityksellinen.

`if`–`else if`-ketju tuottaa prioriteettilogiikan, jossa ensimmäinen
ehto voittaa. Synteesissä se on multipleksereiden ketju, jonka viive
kasvaa ehtojen määrän mukana. Jos ehdot ovat toisensa poissulkevia,
`case` (tai `unique case`) kertoo sen työkalulle, ja tulos on
rinnakkainen valinta.

## Vertailija

Yhtäsuuruusvertailu on XNOR-porttien AND: kaikkien bittien on oltava
samat. Suuruusvertailu ratkeaa ensimmäisestä eroavasta bitistä
eniten merkitsevästä alkaen:

```{.systemverilog tiedosto="esimerkit/05-kombinaatio.sv" osa="vertailija"}
```

Silmukka ei ole laitteistossa silmukka vaan neljä kopiota samasta
logiikasta. `for` kuvaa toistuvan rakenteen, ja synteesi purkaa sen.
Etumerkittömälle vertailulle $a < b$ on myös toinen toteutus: laske
$a - b$ ja katso muistibitti (luku 6). Synteesityökalu valitsee
toteutuksen itse, kun kuvauksessa lukee `a < b`.

## Tyhjentävä testipenkki

Testipenkki käy läpi kaikki syötekombinaatiot ja vertaa lähtöä
viitteeseen, joka on kirjoitettu eri tavalla kuin piiri (esimerkiksi
`d[s]` vs. tulojen summa tai `a < b` vs. bittivertailu):

```{.systemverilog tiedosto="esimerkit/05-kombinaatio.sv" osa="testipenkki"}
```

```{.tuloste tiedosto="esimerkit/05-kombinaatio.odotettu"}
```

`#1` antaa kombinaatiologiikalle aikaa laskea uuden arvon ennen
tarkistusta. Testipenkki ei tulosta jokaista tapausta, vaan laskee
virheet ja kaatuu (`$fatal`), jos niitä on. Tällainen
*itsetarkistava* testi voidaan ajaa automaattisesti jokaisen muutoksen
jälkeen.

## Käytännössä

- **Jokainen `if` on multiplekseri.** Kun luet RTL-kuvausta, näe
  valinnat multipleksereinä ja ehtoketjut prioriteettiketjuina. Pitkä
  `if`–`else if`-ketju on pitkä viive.
- **Kelvollisuusbitti datan rinnalla.** Kun lähtö ei aina ole
  merkityksellinen, lisää bitti, joka kertoo sen. Malli toistuu
  väylissä, FIFOissa ja liukuhihnoissa.
- **One-hot on nopea, binäärikoodi tiivis.** Dekoodattu one-hot-signaali
  ohjaa suoraan, mutta vie $2^k$ johdinta. Pitkät matkat kulkevat
  koodattuna, ja dekoodaus tehdään perillä.
- **Viite eri tavalla kuin toteutus.** Testipenkin viitemalli
  kirjoitetaan eri tavalla kuin testattava piiri. Jos molemmat
  kopioidaan samasta ajatuksesta, sama virhe on molemmissa.

## Itsearviointi

- Osaat toteuttaa multiplekserin, dekooderin, prioriteettikooderin ja
  vertailijan ja selittää niiden käyttökohteet.
- Osaat kertoa, miksi multiplekseri on universaali ja miten se liittyy
  FPGA:n hakutauluun.
- Osaat selittää, miksi `if`–`else if`-ketju tuottaa
  prioriteettilogiikkaa.
- Osaat kirjoittaa itsetarkistavan tyhjentävän testipenkin
  kombinaatiologiikalle.
