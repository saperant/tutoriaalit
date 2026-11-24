# SPI

SPI (Serial Peripheral Interface) on synkroninen, full-duplex-väylä,
jossa isäntä tuottaa kellon ja laite seuraa sitä. Se on yksinkertainen
ja nopea: siinä ei ole osoitteita, kuittauksia eikä tarkistussummia.
Tyypillisiä SPI-laitteita ovat flash-muistit, A/D- ja D/A-muuntimet,
näytöt, radiopiirit ja SD-kortit. Nopeus on muutamasta megahertsistä
yli sataan, ja flash-muisteissa on lisäksi nelibittinen Quad SPI.

## Signaalit ja siirto

| Signaali | Suunta | Tehtävä |
|----------|--------|---------|
| SCK | isännältä | kello |
| MOSI (COPI) | isännältä laitteelle | data laitteelle |
| MISO (CIPO) | laitteelta isännälle | data isännälle |
| CS (SS) | isännältä, yksi laitetta kohti | piirinvalinta, aktiivinen alhaalla |

Uudemmat dokumentit käyttävät nimiä *controller* ja *peripheral*
(COPI, CIPO). Molemmat päät ovat siirtorekistereitä, jotka on
kytketty renkaaksi. Jokaisella kellojaksolla isäntä siirtää yhden
bitin laitteelle ja laite yhden bitin isännälle, joten jokainen siirto
on *vaihto*. Jos isäntä haluaa vain lukea, se lähettää täytetavuja
(yleensä `0xFF` tai `0x00`), ja jos se haluaa vain kirjoittaa, se
hylkää vastaanotetut tavut. Eniten merkitsevä bitti kulkee yleensä
ensin.

Laite, jonka CS on ylhäällä, ei kuuntele kelloa ja päästää MISO-
lähtönsä irti (suurimpedanssinen tila), joten monta laitetta voi
jakaa saman MISO-johtimen. CS ei ole pelkkä valinta vaan myös
*transaktion raja*. Laite aloittaa komennon tulkinnan CS:n laskiessa
ja suorittaa sen tai hylkää keskeneräisen CS:n noustessa. Siksi
monitavuinen komento on lähetettävä yhden CS-jakson aikana.

## Moodit: CPOL ja CPHA

SPI:llä ei ole yhtä ajoitusta vaan neljä. CPOL on kellon lepotaso, ja
CPHA kertoo, kummalla reunalla data luetaan. Moodi on
$2 \cdot \mathrm{CPOL} + \mathrm{CPHA}$:

| Moodi | CPOL | CPHA | Lepotaso | Näytereuna | Siirtoreuna |
|-------|------|------|----------|------------|-------------|
| 0 | 0 | 0 | alhaalla | nouseva | laskeva |
| 1 | 0 | 1 | alhaalla | laskeva | nouseva |
| 2 | 1 | 0 | ylhäällä | laskeva | nouseva |
| 3 | 1 | 1 | ylhäällä | nouseva | laskeva |

Kun CPHA = 0, ensimmäinen bitti on linjalla jo CS:n laskiessa, ennen
ensimmäistä reunaa. Kun CPHA = 1, se asetetaan ensimmäisellä reunalla.
Malli simuloi siirron reuna kerrallaan. Kumpikin osapuoli tuntee
vain oman moodinsa ja päättää reunan suunnasta, näytteistääkö se vai
vaihtaako lähtöään. Samalla reunalla näytteet otetaan ennen kuin
lähdöt muuttuvat, kuten pitoaika vaatii:

```{.python tiedosto="esimerkit/python/mallit/spi.py" osa="siirto"}
```

```{.python tiedosto="esimerkit/python/spi_moodit.py" osa="aallot"}
```

```{.tuloste tiedosto="esimerkit/python/spi_moodit.odotettu"}
```

Aaltojen alla ovat bitit, jotka isäntä luki MISO-linjalta. Moodit 0 ja
3 lukevat samalla, nousevalla reunalla ja eroavat vain kellon
lepotasosta, samoin moodit 1 ja 2. Moni laite, kuten useimmat
flash-muistit, hyväksyy siksi kummankin parin moodit.

Väärän moodin oire näkyy tulosteen lopussa, ja se on hankala:

```{.python tiedosto="esimerkit/python/spi_moodit.py" osa="ristiin"}
```

Kun laite on väärässä moodissa, se voi silti vastaanottaa isännän
tavut oikein, mutta isännän lukema data on bitin myöhässä. `0x3C` tulee
perille muodossa `0x9E` tai `0x1E`. Kirjoitukset näyttävät
onnistuvan ja tunnisterekisterin luku antaa "melkein oikean" arvon.
Kun luettu arvo on kaksinkertainen tai puolikas odotetusta tai sen ylin
bitti on väärin, ensimmäinen epäilty on moodi.

## PL022-ajuri

Mikrokontrollerin SPI-lohko tekee bittitason työn. Ohjelma asettaa
moodin, sanan pituuden ja kellon ja kirjoittaa tavut FIFOon. ARM:n
PL022 jakaa kellon kahdessa vaiheessa:
$f_{SCK} = f_{SSPCLK} / (\mathrm{CPSDVSR} \cdot (1 + \mathrm{SCR}))$,
jossa esijakaja CPSDVSR on parillinen. Laitteen datalehti antaa suurimman
sallitun kellon, joten ajuri valitsee lähimmän nopeuden, joka ei ylitä
sitä:

```{.c tiedosto="esimerkit/ajurit/pl022.c" osa="kello"}
```

```{.c tiedosto="esimerkit/ajurit/pl022.c" osa="alusta"}
```

Siirtofunktio pitää lähetys-FIFOa täynnä, mutta enintään kahdeksan
kehystä matkalla kerrallaan. Jokaisesta lähetetystä kehyksestä
syntyy vastaanotettu kehys, ja jos lähetys-FIFOon kirjoitetaan
enemmän kuin vastaanotto-FIFOon mahtuu, vastaanotto vuotaa yli.
Odotukset ovat rajattuja: jos FIFO ei etene, funktio palauttaa
aikarajavirheen eikä jää ikuiseen silmukkaan.

```{.c tiedosto="esimerkit/ajurit/pl022.c" osa="siirto"}
```

PL022:ssa on silmukkatila (LBM), joka kytkee lähetyksen lohkon sisällä
vastaanottoon. Sillä ajurin ja FIFOjen toiminnan voi todeta ennen kuin
laitteita on kytketty, myös tuotantotestissä.

```{.c tiedosto="esimerkit/04-spi-adc/main.c" osa="itsetesti"}
```

## A/D-muunnin MAX1111

MAX1111 on kahdeksanbittinen nelikanavainen A/D-muunnin, jossa on
sisäinen 2,048 V:n referenssi. Muunnos on kolmen tavun siirto:
ohjaustavu kertoo kanavan ja tilan, ja kahden seuraavan tavun aikana
tulos siirtyy ulos. Tulos ei ole tavun rajalla vaan jakautuu kahden
tavun yli. Tällainen bittien sijoittelu on tavallista ja kannattaa
tarkistaa datalehden ajoituskaaviosta.

```{.c tiedosto="esimerkit/04-spi-adc/main.c" osa="ohjaustavu"}
```

```{.c tiedosto="esimerkit/04-spi-adc/main.c" osa="muunnos"}
```

```{.c tiedosto="esimerkit/04-spi-adc/main.c" osa="main"}
```

```{.tuloste tiedosto="esimerkit/testit/04-spi-adc.odotettu"}
```

QEMU antaa kanavien jännitteet komentoriviltä (`input0` … `input3`,
ks. luku 1). Koodi 255 vastaa referenssiä vähennettynä yhdellä
LSB:llä, eli 8-bittisen muuntimen täysi asteikko on 2048 · 255/256 =
2040 mV. QEMU:n PL022 ei ohjaa CS-linjaa, ja laite on aina valittuna.
Oikeassa piirissä CS ohjataan joko lohkon omalla lähdöllä tai
GPIO-nastalla. GPIO:lla CS lasketaan ennen ensimmäistä tavua ja
nostetaan vasta, kun lohko on lopettanut (SR:n BSY-bitti nolla), ei
heti kun viimeinen tavu on kirjoitettu FIFOon.

## Ketjutus

Kun laitteita on paljon ja nastoja vähän, siirtorekisterilaitteet
(esim. LED-ajurit ja 74HC595-tyyppiset lähtörekisterit) ketjutetaan:
ensimmäisen MISO kytketään toisen MOSI:in, ja kaikilla on yhteinen CS.
Ketju on yksi pitkä siirtorekisteri. Ensimmäisenä lähetetty tavu
päätyy kauimmaiseen laitteeseen, ja CS:n nousu lukitsee kaikkien
arvot kerralla.

```{.python tiedosto="esimerkit/python/mallit/spi.py" osa="ketju"}
```

```{.python tiedosto="esimerkit/python/spi_laitteet.py" osa="ketju"}
```

Tuloste on alempana flash-esimerkin perässä.

## Flash-muisti

SPI NOR -flash on tavallisin SPI-laite: siihen tallennetaan
laiteohjelmisto, asetukset ja lokit. Lähes kaikki valmistajat
käyttävät samaa komentokantaa, jonka juuret ovat 25-sarjan piireissä.
Komento on transaktion ensimmäinen tavu, ja sitä seuraavat 24-
bittinen osoite ja data:

```{.python tiedosto="esimerkit/python/mallit/spiflash.py" osa="komennot"}
```

Flash-muistin säännöt ovat toisenlaiset kuin RAMin:

- **Ohjelmointi voi vain nollata bittejä.** Ykköseksi bitit palaavat
  vain tyhjennyksessä, ja tyhjennys koskee kokonaista sektoria
  (tyypillisesti 4 KiB) tai lohkoa.
- **Ennen jokaista ohjelmointia tai tyhjennystä tarvitaan WREN.**
  Se asettaa tilarekisterin WEL-bitin, ja operaatio nollaa sen.
  Unohdettu WREN on yleisin flash-virhe: piiri hylkää komennon
  hiljaa.
- **Operaatio kestää**: sivun ohjelmointi millisekunteja ja sektorin
  tyhjennys kymmeniä tai satoja millisekunteja. Sen ajan tilarekisterin
  WIP-bitti on 1, eikä piiri hyväksy muita komentoja.
- **Ohjelmointi kiertää sivun sisällä.** Sivu on 256 tavua, ja jos
  kirjoitus ylittää sivun rajan, osoite kiertää saman sivun alkuun
  eikä jatka seuraavalle.

Malli `SpiFlash` toteuttaa nämä säännöt komentotasolla: jokainen
transaktio saa MOSI-tavut ja palauttaa yhtä monta MISO-tavua.
Jäljitysfunktio tulostaa transaktiot kuten logiikka-analysaattorin
SPI-dekooderi.

```{.python tiedosto="esimerkit/python/spi_laitteet.py" osa="jaljitys"}
```

```{.python tiedosto="esimerkit/python/spi_laitteet.py" osa="istunto"}
```

```{.tuloste tiedosto="esimerkit/python/spi_laitteet.odotettu"}
```

Jäljityksestä näkyvät säännöt yksi kerrallaan. Ohjelmointi ilman
WRENiä ei muuttanut mitään. Neljän tavun kirjoitus osoitteeseen
`0x10FE` jakautui kahtia: "AB" meni sivun loppuun ja "CD" sivun
alkuun `0x1000`, ei osoitteeseen `0x1100`. Tyhjennys palautti
sektorin ykkösiksi. Oikea ajuri jakaa kirjoitukset sivun rajoilla
samoin kuin EEPROM-ajuri luvussa 8. Lisäksi se tarkistaa piirin
tunnisteen (`EF 40 18` on 128 megabitin piiri) ja lukee
parametritaulukon (SFDP), josta selviävät sivun ja sektorin koot ja
tuetut komennot.

## Käytännössä

- **Tarkista moodi, bittijärjestys ja suurin kello datalehdestä**
  ennen ensimmäistä siirtoa. Jos luettu data on bitin siirtynyt, moodi
  on väärä.
- **Pidä CS alhaalla koko komennon ajan** ja nosta se vasta, kun lohko
  on lopettanut siirron. Huomioi datalehden CS-viiveet.
- **Rajaa jokainen odotus** ja palauta virhe, jos laite tai lohko ei
  etene.
- **Testaa ajuri silmukkatilassa** tai kytkemällä MOSI ja MISO yhteen
  ennen kuin epäilet laitetta.
- **Flash: WREN ennen jokaista ohjelmointia ja tyhjennystä, WIP:n
  kysely jälkeen, kirjoitukset sivun rajoilla.** Lue tunniste ja SFDP
  äläkä kovakoodaa piirin kokoa.

## Itsearviointi

- Osaat selittää, miksi jokainen SPI-siirto on vaihto ja mitä CS:n
  lasku ja nousu merkitsevät laitteelle.
- Osaat piirtää moodien 0–3 ajoitukset ja tunnistaa väärän moodin
  oireen datasta.
- Osaat laskea PL022:n kellonjakajat ja toteuttaa FIFOa käyttävän
  siirron, joka ei vuoda yli eikä jää jumiin.
- Osaat lukea A/D-muuntimen tuloksen, joka jakautuu tavujen rajan yli,
  ja muuttaa sen jännitteeksi.
- Osaat käyttää SPI-flashia: tunniste, WREN, ohjelmointi sivuittain,
  WIP-kysely ja sektorin tyhjennys.
