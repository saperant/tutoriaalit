# UART

UART (Universal Asynchronous Receiver-Transmitter) on vanhin ja
yksinkertaisin sarjaväylä: kaksi johdinta, TX ja RX, ristiin kytkettyinä,
ja yhteinen maa. Se on edelleen sulautetun laitteen tärkein
debug-yhteys, ja sen yli kulkevat GPS-vastaanottimien,
modeemien, Bluetooth-moduulien ja teollisuuden Modbus-laitteiden
viestit. Mikrokontrollerin UART on oheislaite, joka muuttaa tavun
bittijonoksi ja takaisin. Kaikki muu, kuten viestien rajat,
virheentarkistus ja kuittaukset, on ohjelman tehtävä.

## Kehys

Lepotilassa linja on ylhäällä. Kehys alkaa START-bitillä (0), jonka
jälkeen tulevat databitit vähiten merkitsevä ensin, valinnainen
pariteettibitti ja yksi tai kaksi STOP-bittiä (1). Muoto merkitään
lyhenteellä, esimerkiksi 8N1: kahdeksan databittiä, ei pariteettia,
yksi STOP-bitti. Se on nykyään lähes aina oletus; 7E1 ja 8E1 näkyvät
vanhemmissa protokollissa.

```{.python tiedosto="esimerkit/python/uart_kehys.py" osa="aalto"}
```

```{.tuloste tiedosto="esimerkit/python/uart_kehys.odotettu"}
```

Tavu `0x4B` lähtee linjalle järjestyksessä 1, 1, 0, 1, 0, 0, 1, 0, eli
bittijärjestys on käänteinen siihen, miten luku kirjoitetaan.
Parillinen pariteetti (E) täydentää ykkösten määrän parilliseksi.
Pariteetti löytää jokaisen yhden bitin virheen mutta ei kahden, eikä
se kerro, mikä bitti kääntyi. Sen arvo on vähäinen, ja nykyiset
protokollat tarkistavat kokonaisia viestejä CRC:llä.

## Vastaanotin

Vastaanotin ei tiedä, milloin kehys alkaa. Se näytteistää linjaa
tyypillisesti 16 kertaa bitin aikana ja odottaa laskevaa reunaa. Kun
reuna tulee, se tarkistaa puolen bitin päästä, että linja on yhä
alhaalla. Lyhyt häiriöpiikki ei siis käynnistä vastaanottoa. Sen
jälkeen se lukee jokaisen bitin tämän keskikohdan ajoituksella, 16
näytteen välein:

```{.python tiedosto="esimerkit/python/mallit/uart.py" osa="vastaanotto"}
```

Oikeat UARTit ottavat keskikohdasta usein kolme näytettä ja
äänestävät, mikä vaimentaa yksittäisiä häiriöitä. Virheitä on kolmea
lajia, ja ne näkyvät tulosteen lopussa:

```{.python tiedosto="esimerkit/python/uart_kehys.py" osa="virheet"}
```

- **Pariteettivirhe**: häiriö käänsi ensimmäisen kehyksen bitin d2,
  ja `0x4F` vastaanotettiin `0x4B`:nä. Pariteetti huomasi sen.
- **Kehysvirhe** (framing error): STOP-bitin paikalla oli nolla.
  Syynä on yleensä väärä nopeus tai muoto, häiriö tai *katko*
  (break), jossa lähettäjä pitää linjan tarkoituksella alhaalla yli
  kehyksen ajan. Katkoa käytetään merkkinä esimerkiksi LIN-väylässä
  ja käynnistyslatainten herättämisessä.
- **Ylivuoto** (overrun): uusi tavu valmistui ennen kuin ohjelma luki
  edellisen. Linjalla ei ollut mitään vikaa, vika oli ohjelmassa.
  Siitä lisää alempana.

Lyhyt piikki lepotilassa ei tuottanut mitään, koska START-bitin
keskikohdan tarkistus hylkäsi sen.

## Nopeus ja sen virhe

UARTin nopeus saadaan jakamalla oheislaitteen kello. Klassinen UART
(16550 ja useimmat mikrokontrollerit) jakaa kellon ensin kuudella-
toista ylinäytteistystä varten. CMSDK-UART käyttää jakajaa
`BAUDDIV = kello / nopeus` suoraan. Jakaja on kokonaisluku, joten
nopeus pyöristyy:

```{.python tiedosto="esimerkit/python/uart_nopeus.py" osa="jakajat"}
```

Kuinka paljon virhettä vastaanotin kestää? Se tahdistuu START-bitin
reunaan ja lukee viimeisen bitin, STOP-bitin, noin 9,5 bitin päästä.
Kun näyte saa siirtyä enintään puoli bittiä ja reunan havaitsemisen
epätarkkuus on yksi näyte (1/16 bittiä), suurin sallittu ero on
$(0{,}5 - 1/16) / 9{,}5 \approx 4{,}6\,\%$. Malli kokeilee samaa:

```{.python tiedosto="esimerkit/python/uart_nopeus.py" osa="sieto"}
```

```{.tuloste tiedosto="esimerkit/python/uart_nopeus.odotettu"}
```

Mallin raja on epäsymmetrinen, koska vastaanotin havaitsee reunan
aina hieman myöhässä ja näytteistää siksi bitin keskikohdan jälkeen.
Hitaampi lähetin osuu silloin pidempään oikealle kohdalle. Raja on
kahden laitteen yhteinen. Jos kumpikin on 2,5 % pielessä vastakkaisiin
suuntiin, yhteys katkeilee, vaikka kumpikin on "melkein oikein".
Taulukko kertoo myös, miksi UART-piireissä on usein 1,8432 MHz:n tai
14,7456 MHz:n kide: ne jakautuvat tasan kaikilla tavallisilla
nopeuksilla. 16 MHz:n kellolla 115 200 bit/s on jo -3,5 % pielessä.
Mikrokontrollerin sisäinen RC-oskillaattori voi heittää lämpötilan
mukaan useita prosentteja. Sillä UART toimii vain kalibroituna tai
hitaasti, tai jos nopeus mitataan vastapuolen lähettämästä
tunnetusta tavusta (autobaud).

## Keskeytysohjattu lähetys

Pollaava lähetys pysäyttää ohjelman jokaisen tavun ajaksi: 115 200
bit/s:n nopeudella yksi tavu kestää 87 µs, mikä on Cortex-M3:lla
tuhansia käskyjä. Parempi tapa on kirjoittaa teksti renkaaseen ja antaa
lähetyskeskeytyksen siirtää tavut lähettimeen. Rengaspuskuri on sama
kuin paketin *Mikrokontrollerit* luvussa 7.

```{.c tiedosto="esimerkit/02-lahetys/main.c" osa="keskeytys"}
```

Hankalin kohta on käynnistys. CMSDK-UART, kuten moni muu UART,
keskeyttää lähetyksen osalta vain, kun lähetysrekisteri *tyhjenee*.
Joutilas lähetin on jo tyhjä, joten keskeytyksen salliminen ei tuota
mitään. Ensimmäinen tavu on kirjoitettava itse, ja vasta keskeytyksen
sallimisen jälkeen. Muuten tyhjeneminen ehtii tapahtua ennen
sallimista ja menee ohi.

```{.c tiedosto="esimerkit/02-lahetys/main.c" osa="kaynnista"}
```

```{.c tiedosto="esimerkit/02-lahetys/main.c" osa="kirjoita"}
```

```{.c tiedosto="esimerkit/02-lahetys/main.c" osa="main"}
```

```{.tuloste tiedosto="esimerkit/testit/02-lahetys.odotettu"}
```

Sama ohjelma ilman ensimmäisen tavun kirjoitusta
(`-DILMAN_KAYNNISTYSTA`) täyttää renkaan eikä lähetä mitään:

```{.tuloste tiedosto="esimerkit/testit/02-lahetys-virhe.odotettu"}
```

Virhe on salakavala, koska pollaavan ja keskeytysohjatun lähetyksen
sekoittaminen peittää sen. Jos jokin muu kohta ohjelmassa tulostaa
pollaamalla, sen tavun jälkeinen tyhjeneminen käynnistää
keskeytysketjun, ja jonossa odottanut teksti ilmestyy yllättäen.
Toinen yleinen virhe olisi TXINTEN-bitin muuttaminen keskeytysten
ollessa sallittuina: käsittelijä voi poistaa bitin juuri sen jälkeen,
kun pääohjelma on todennut lähetyksen olevan käynnissä. Siksi
`kaynnista` kutsutaan kriittisessä osiossa.

## Vuonohjaus

Vastaanottimessa on yleensä vain muutaman tavun FIFO, ja ohjelman on
luettava tavut ennen kuin seuraavat ehtivät perille. Jos se ei ehdi,
syntyy ylivuoto ja tavuja katoaa. Vuonohjaus kertoo lähettäjälle,
milloin sen on odotettava:

- **Laitteistovuonohjaus** RTS/CTS: vastaanottaja nostaa RTS-linjansa
  (vastapuolen CTS), kun puskuri on täyttymässä, ja lähetin pysähtyy
  tavun rajalla. Monessa UARTissa tämä toimii ilman ohjelmaa.
- **Ohjelmallinen vuonohjaus** XON/XOFF: vastaanottaja lähettää
  merkin 0x13 (pysähdy) ja 0x11 (jatka). Se ei toimi binääridatan
  kanssa, koska samat tavut voivat esiintyä datassa.
- **Protokollatason vuonohjaus**: lähettäjä odottaa kuittausta
  jokaiseen viestiin tai sallittuun ikkunaan asti.

Seuraavan esimerkin ensimmäinen versio luki UART1:n tavut keskeytyksessä
renkaaseen ilman mitään vuonohjausta, ja se jäi QEMU:ssa jumiin. QEMU
syöttää tiedoston tavut niin nopeasti kuin vastaanotin ottaa niitä
vastaan. Rengas täyttyi, kun pääohjelma lähetti vastauksia, ja
loput tavut, mukaan lukien viimeisen kehyksen erotin, katosivat. Sama
tapahtuu oikeassa laitteessa, kun lähettäjä on nopea ja vastaanottaja
tekee välillä jotain muuta. Korjaus on vuonohjaus ohjelmassa: kun
rengas on täynnä, käsittelijä jättää tavun vastaanottimeen ja kytkee
keskeytyksen pois. Täysi vastaanotin ei ota uutta tavua vastaan, ja
QEMU odottaa. Oikealla linjalla sama tila nostaisi RTS:n.

```{.c tiedosto="esimerkit/03-kehykset/main.c" osa="vastaanotto"}
```

## Kehykset tavuvirrassa

UART siirtää tavuja, mutta sovellus tarvitsee viestejä. Vastaanottajan
on tiedettävä, missä viesti alkaa ja loppuu, huomattava vioittunut
viesti ja löydettävä seuraavan alku, kun jotain on kadonnut. Tavallisia
ratkaisuja on kolme:

| Tapa | Esimerkkejä | Hyvää | Huonoa |
|------------------|----------------|------------------|------------------|
| Tekstirivit | NMEA (GPS), AT-komennot | luettava, helppo debugata | vain tekstiä, rivinvaihto ei saa esiintyä datassa |
| Hiljaisuus viestien välissä | Modbus RTU (3,5 merkin tauko) | ei lisätavuja | ajoitus pitää mitata tarkasti |
| Erotin ja tavujen koodaus | SLIP, COBS, HDLC | binääridata, tahdistus palautuu heti | koodaus lisää vähän tavuja |

Esimerkki käyttää COBSia (Consistent Overhead Byte Stuffing). Viestin
perään lisätään CRC-16, ja koko kehys koodataan niin, ettei siinä ole
yhtään nollatavua. Nolla kelpaa siksi kehysten erottimeksi. Koodaus
korvaa jokaisen nollan etäisyydellä seuraavaan nollaan, ja lohkon
ensimmäinen tavu kertoo sen pituuden. Lisätavuja tulee yksi
jokaista 254 tavua kohti, datasta riippumatta.

```{.c tiedosto="esimerkit/03-kehykset/kehys.h" osa="rajapinta"}
```

```{.c tiedosto="esimerkit/03-kehykset/kehys.c" osa="koodaa"}
```

Purku tekee saman käänteisesti ja hylkää lohkon, jossa on nolla tai
liian pitkä hyppy. CRC-16 lasketaan bitti kerrallaan. Taulukkoversio on nopeampi mutta
vie 512 tavua flashia. Kun CRC lisätään viestin perään suurin tavu
ensin, koko kehyksen CRC on nolla, ja vastaanottaja tarkistaa sen
yhdellä kutsulla.

```{.c tiedosto="esimerkit/03-kehykset/kehys.c" osa="crc"}
```

Laite on yksinkertainen palvelin. Se kokoaa tavuja erottimeen asti,
purkaa ja tarkistaa kehyksen ja vastaa jokaiseen kehykseen joko
vastauksella tai kieltävällä kuittauksella (NAK), jossa on syy.
Liian pitkä kehys luetaan erottimeen asti ja hylätään: koska erotin
ei voi esiintyä kehyksen sisällä, tahdistus palautuu aina seuraavan
nollan kohdalla. Vastaus koodataan samalla tavalla ja lähetetään
pollaamalla.

```{.c tiedosto="esimerkit/03-kehykset/main.c" osa="main"}
```

Isäntää esittää Python-ohjelma. Sen komentosarjassa on tarkoituksella
yksi kääntynyt bitti, linjahäiriötä, liian pitkä kehys ja tuntematon
komento. Mallin COBS ja CRC (`python/mallit/kehys.py`) on kirjoitettu
erikseen C-koodista, joten ajo testaa myös, että kaksi toteutusta
ovat yhtä mieltä.

```{.python tiedosto="esimerkit/python/kehykset.py" osa="tuota"}
```

```{.make tiedosto="esimerkit/Makefile" osa="kehykset"}
```

Laitteen konsoli ja isännän purkamat vastaukset:

```{.tuloste tiedosto="esimerkit/testit/03-kehykset.odotettu"}
```

```{.tuloste tiedosto="esimerkit/testit/03-kehykset-isanta.odotettu"}
```

## RS-232 ja RS-485

UARTin TTL-tason signaalit kulkevat piirilevyllä ja lyhyessä
kaapelissa. Pidemmälle mentäessä UARTin perään kytketään linjapiiri:

- **RS-232** on pisteestä pisteeseen kulkeva ±-jännitteinen linja
  (luku 2), jossa on myös RTS/CTS- ja DTR/DSR-ohjauslinjat. USB-
  sarjamuuntimet esittävät sen tietokoneelle COM-porttina tai
  laitteena `/dev/ttyUSB0`.
- **RS-485** on differentiaalinen monipisteväylä, johon voi kytkeä
  kymmeniä laitteita ja joka kulkee yli kilometrin. Kaksijohtimisena
  se on half-duplex, joten jokainen laite kytkee lähettimensä
  (DE, driver enable) päälle vain omaksi vuorokseen. Väylää käyttää
  esimerkiksi Modbus RTU, joka määrittelee osoitteet, komennot ja CRC:n.

RS-485:n tavallisin ohjelmavirhe on lähettimen sulkeminen liian
aikaisin. Lähetysrekisteri tyhjenee (TX empty), kun viimeinen tavu on
siirtynyt siirtorekisteriin, mutta tavu on silloin vasta lähdössä
linjalle. DE saa laskea vasta, kun viimeinenkin STOP-bitti on
lähetetty. Siihen tarvitaan oma keskeytys (TX complete) tai ajastin.
Monessa UARTissa on suoraan DE-lähtö, joka hoitaa tämän laitteistolla.

## Käytännössä

- **Käytä 8N1-muotoa ja nopeutta, jonka kello jakaa tarkasti.**
  Laske jakajan virhe, ja pidä kummankin pään virhe alle noin 2
  prosentin.
- **Lähetä keskeytyksillä tai DMA:lla ja vastaanota renkaaseen.**
  Käynnistä keskeytysohjattu lähetys oikein: salli keskeytys ja
  kirjoita ensimmäinen tavu itse.
- **Suunnittele vuonohjaus.** Täysi puskuri saa pysäyttää lähettäjän
  (RTS/CTS tai lukemisen keskeyttäminen), ei hukata tavuja hiljaa.
  Laske ylivuodot ja kehysvirheet ja raportoi ne.
- **Kehystä viestit** COBSilla, SLIPillä tai muulla erottimeen
  perustuvalla tavalla, ja lisää CRC. Vastaa jokaiseen kehykseen
  myönteisesti tai kieltävästi, jotta lähettäjä tietää, mitä on
  lähetettävä uudelleen.
- **RS-485:ssä sulje lähetin vasta viimeisen STOP-bitin jälkeen.**

## Itsearviointi

- Osaat piirtää 8N1- ja 8E1-kehyksen annetusta tavusta ja nimetä
  pariteetti-, kehys- ja ylivuotovirheen syyt.
- Osaat selittää, miten vastaanotin tahdistuu ja näytteistää, ja
  laskea, kuinka suuren nopeuseron yhteys sietää.
- Osaat laskea UARTin jakajan ja sen virheen annetulle kellolle.
- Osaat toteuttaa keskeytysohjatun lähetyksen ja käynnistää sen
  oikein.
- Osaat toteuttaa vuonohjauksen ja kehysprotokollan (COBS ja CRC)
  ja selittää, miksi tahdistus palautuu virheen jälkeen.
