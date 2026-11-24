# Muistiin kuvatut rekisterit ja GPIO

Mikrokontrollerin oheislaitteita ohjataan *muistiin kuvatuilla
rekistereillä* (memory-mapped I/O, MMIO). Jokaisella oheislaitteella on
osoitealue, ja sen rekisterit näkyvät prosessorille muistipaikkoina:
kirjoitus osoitteeseen `0x40004000` lähettää merkin UART0:sta, ja luku
osoitteesta `0x40028000` kertoo LEDien tilan. Mitään erityisiä
I/O-käskyjä ei ole; samat `ldr`- ja `str`-käskyt, jotka käsittelevät
muuttujia, käsittelevät myös laitteita.

Rekisteri ei kuitenkaan ole muistia, ja erot ovat koko luvun aihe:

- **Luvulla voi olla sivuvaikutus.** UART:n DATA-rekisterin luku
  poistaa merkin vastaanottopuskurista; toinen luku antaa eri arvon.
- **Kirjoitus on käsky.** Kirjoitus voi käynnistää lähetyksen,
  nollata laskurin tai kuitata keskeytyksen. Sama arvo kahdesti
  tarkoittaa kahta tapahtumaa.
- **Arvo muuttuu itsestään.** Tilarekisterin bitit, ajastimen laskuri
  ja tulonastojen tila muuttuvat ohjelmasta riippumatta.
- **Bitit eivät ole tasavertaisia.** Osa on vain luettavia, osa
  nollautuu kirjoittamalla ykkönen (*write 1 to clear*, W1C), ja
  varattuihin bitteihin pitää kirjoittaa nollaa tai niiden vanha arvo.

## volatile

C-kääntäjä saa olettaa, että muistin sisältö muuttuu vain ohjelman
omien kirjoitusten seurauksena. Se saa jättää lukuja pois, yhdistää
peräkkäisiä kirjoituksia ja siirtää muistiviittauksia silmukoista
ulos. Muuttujille tämä on hyvä optimointi, rekistereille katastrofi.
Määre `volatile` kieltää sen: jokainen lähdekoodin luku ja kirjoitus
tehdään, oikean kokoisena ja samassa järjestyksessä muiden
`volatile`-viittausten kanssa.

```{.c tiedosto="esimerkit/04-ledit/main.c" osa="ilman-volatilea"}
```

```{.c tiedosto="esimerkit/04-ledit/main.c" osa="volatile-koe"}
```

```{.tuloste tiedosto="esimerkit/testit/04-ledit.odotettu"}
```

Rivi `ilman volatilea: B` on kääntäjän työtä: ensimmäinen kirjoitus
on samaan osoitteeseen kuin toinen, joten se on optimoijan silmissä
turha. Samaa sukua ovat silmukat, jotka odottavat tilabittiä
`while (!(UART0->STATE & BITTI))`: ilman `volatile`a kääntäjä lukee
rekisterin kerran ja pyörii ikuisesti. (Esimerkin `volatile`-versio
kirjoittaa kaksi merkkiä tarkistamatta, mahtuvatko ne lähettimeen.
QEMU lähettää jokaisen merkin heti, mutta oikea UART hukkaisi toisen.)

`volatile` ei tee kaikkea:

- **Se ei tee viittauksesta atomista.** `REG |= BITTI` on edelleen
  luku, muutos ja kirjoitus, joiden väliin voi tulla keskeytys
  (luku 7).
- **Se ei järjestä tavallisia muistiviittauksia.** Kääntäjä saa
  siirtää ei-`volatile`-muuttujan kirjoituksen `volatile`-kirjoituksen
  ohi. Tarvittaessa käytetään kääntäjäestettä tai `atomic_signal_fence`a.
- **Se ei odota laitetta.** Prosessori voi päästää kirjoituksen
  väylälle ja jatkaa ennen kuin oheislaite on sen vastaanottanut.
  Käsky `dsb` odottaa, että kaikki muistiviittaukset ovat valmiita.

## Rekisterit C:ssä

Yksittäinen rekisteri voidaan kuvata makrolla, joka muuntaa osoitteen
`volatile`-osoittimeksi ja lukee sen:

```{.c tiedosto="esimerkit/04-ledit/main.c" osa="makrot"}
```

Oheislaitteessa on kuitenkin useita rekistereitä peräkkäin, ja
CMSIS-tyyli kuvaa ne rakenteena, jonka jäsenet ovat rekisterit
oikeissa siirtymissä. Rakenneosoitin oheislaitteen perusosoitteeseen
antaa nimetyt rekisterit, ja saman tyypin voi käyttää kaikille saman
laitteen kopioille (UART0, UART1, ...). `_Static_assert` tarkistaa
käännösaikana, että siirtymät vastaavat käyttöohjetta. Tyhjät välit
täytetään varatuilla jäsenillä.

```{.c tiedosto="esimerkit/yhteinen/mps2.h" osa="uart"}
```

```{.c tiedosto="esimerkit/yhteinen/mps2.h" osa="fpgaio"}
```

Vain luettava rekisteri on `volatile const`: kääntäjä estää
kirjoituksen. C:n bittikenttärakenteita (`uint32_t TXEN : 1;`) ei
yleensä käytetä rekistereille: bittien järjestys ja viittauksen leveys
ovat toteutuksen määrittelemiä, ja jokainen kenttäkirjoitus on
piilotettu luku–muutos–kirjoitus. Sen sijaan käytetään maskeja ja
siirtoja.

## Bittioperaatiot

----------------------------------------------------------------------------
Tarkoitus        Lauseke                                     Huomio
---------------- ------------------------------------------- -----------------
bitti päälle     `REG |= MASKI;`                             luku, muutos,
                                                             kirjoitus

bitti pois       `REG &= ~MASKI;`                            sama

vaihda           `REG ^= MASKI;`                             sama

testaa           `if (REG & MASKI)`                          yksi luku

kenttä           `REG = (REG & ~(0xFu << 4)) | (arvo << 4);` nollaa ensin,
                                                             sitten aseta

kuittaus (W1C)   `REG = MASKI;`                              ei `|=`: se
                                                             kuittaisi muutkin
----------------------------------------------------------------------------

```{.c tiedosto="esimerkit/04-ledit/main.c" osa="rmw"}
```

Viimeinen rivi taulukossa on yleinen virhe. Jos keskeytyksen tilabitit
kuitataan kirjoittamalla ykkönen, `REG |= BITTI` lukee kaikki
odottavat bitit ja kirjoittaa ne takaisin ykkösinä, jolloin myös
käsittelemättömät keskeytykset kuitataan. Kuittaus tehdään aina
suoralla kirjoituksella.

Luku–muutos–kirjoitus ei ole atominen. Jos pääohjelma ja keskeytys
muuttavat saman rekisterin eri bittejä, toinen muutos voi kadota.
Siksi monissa oheislaitteissa on erilliset aseta- ja nollaa-rekisterit
(STM32:n GPIO:n BSRR, CMSDK:n OUTENSET ja OUTENCLR): kirjoitus
muuttaa vain ne bitit, joissa on ykkönen.

### Bit-band

Cortex-M3:ssa ja -M4:ssä on toinen ratkaisu. SRAM-alueen ja
oheislaitealueen ensimmäisen megatavun jokaisella *bitillä* on oma
32-bittinen *alias*-sanansa. Kirjoitus aliakseen muuttaa vain sen
bitin, ja väylä tekee muutoksen yhtenä jakamattomana operaationa.

```{.c tiedosto="esimerkit/04-ledit/main.c" osa="bittialue"}
```

```{.c tiedosto="esimerkit/04-ledit/main.c" osa="bittialue-kaytto"}
```

Bit-band puuttuu Cortex-M0+:sta, -M7:stä ja ARMv8-M:stä, joten
siirrettävä koodi käyttää aseta- ja nollaa-rekistereitä tai lyhyttä
kriittistä osiota.

## GPIO

Yleiskäyttöinen I/O (General Purpose I/O, GPIO) on mikrokontrollerin
yksinkertaisin oheislaite: nasta, jonka jännitettä ohjelma lukee tai
asettaa. Nastat on ryhmitelty *portteihin* (PA, PB, ... tai P0, P1),
ja portin rekistereissä on bitti kullekin nastalle. Tyypillisen
GPIO-lohkon rekisterit:

| Rekisteri | Tehtävä |
|-----------|---------|
| suunta (MODER, DIR, OUTENSET) | tulo vai lähtö |
| lähtö (ODR, OUT, DATAOUT) | lähtönastojen taso |
| aseta ja nollaa (BSRR, OUTSET, OUTCLR) | atominen muutos yksittäisille nastoille |
| tulo (IDR, IN, DATA) | nastojen todellinen taso |
| ylös- ja alasveto (PUPDR, PULL) | sisäinen vastus, kun nasta on tulona |
| lähtötyyppi (OTYPER) | push-pull tai avoin nielu (I2C, jaetut linjat) |
| vaihtoehtoinen toiminto (AFR, ALTFUNCSET) | nasta UART:lle, SPI:lle tai ajastimelle |
| keskeytys (EXTI, INTENSET) | keskeytys reunasta tai tasosta |

Kolme asiaa yllättää ensimmäisellä kerralla:

1. **Oheislaitteen kello on sallittava.** Virransäästön vuoksi
   useimpien piirien oheislaitteet ovat resetin jälkeen ilman kelloa,
   eivätkä niiden rekisterit reagoi kirjoituksiin. STM32:lla
   ensimmäinen rivi on esimerkiksi `RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN`.
2. **Nasta on yhteinen.** Sama nasta voi olla GPIO, UART:n lähetys tai
   ajastimen lähtö; vaihtoehtoisen toiminnon valinta kytkee sen.
3. **LED on usein aktiivinen nollalla.** Kortin kytkentä ratkaisee:
   jos LED on kytketty käyttöjännitteen ja nastan väliin, nolla
   sytyttää sen. Tarkista kortin kytkentäkaavio.

Tulonastan arvo on myös usein epävakaa: painonapin kosketin värähtelee
millisekuntien ajan, ja kytkemätön tulo kelluu. Ensimmäiseen auttaa
suodatus (luku 11), jälkimmäiseen ylös- tai alasvetovastus.

QEMU:n mps2-an385-mallissa CMSDK:n GPIO-lohkot ovat mallintamatta,
joten esimerkit käyttävät FPGA-I/O-lohkon LED-rekisteriä, joka
käyttäytyy kuin GPIO-lähtöportti, jossa on kaksi nastaa.

## UART-ajuri

Konsolin ajuri on pienin mahdollinen oheislaiteajuri: alustus kirjoittaa
kellon jakajan ja käyttöönottobitit, ja lähetys odottaa, kunnes
lähetysrekisteri on vapaa.

```{.c tiedosto="esimerkit/yhteinen/konsoli.c" osa="alusta"}
```

Jakaja määrää siirtonopeuden: 25 MHz / 217 ≈ 115 200 bittiä
sekunnissa. Odotussilmukka on *pollausta*: prosessori kysyy tilaa
yhä uudelleen. Yksi merkki kestää tällä nopeudella noin 87
mikrosekuntia, mikä on 25 MHz:n prosessorille yli 2000 kellojaksoa
odottelua. Pienissä ohjelmissa se on hyväksyttävää; keskeytysohjattu
vastaanotto on luvussa 7 ja DMA taidossa *Oheislaiteväylät*.

## Käytännössä

- **Käytä aina `volatile`a rekistereille ja keskeytysten jakamille
  muuttujille**, mutta älä odota siltä atomisuutta tai järjestystä
  tavallisten muuttujien kanssa.
- **Lue käyttöohjeen rekisterikuvaus bitti bitiltä.** Merkinnät `rc_w1`,
  `w1c`, `ro` ja `reserved` kertovat, miten bittiin saa kirjoittaa.
- **Kuittaa W1C-bitit suoralla kirjoituksella**, älä `|=`-operaatiolla.
- **Muuta jaettuja rekistereitä atomisesti**: aseta- ja
  nollaa-rekistereillä, bit-bandilla tai kriittisessä osiossa.
- **Tarkista rakenteiden siirtymät käännösaikana** `_Static_assert`illa,
  jos kirjoitat rekisterimäärittelyt itse.
- **Muista oheislaitteen kello ja nastan toiminnon valinta**, kun
  rekisteri ei näytä tottelevan.

## Itsearviointi

- Osaat selittää, miksi oheislaiterekisteri ei ole tavallista muistia,
  ja mitä `volatile` takaa ja mitä ei.
- Osaat kuvata oheislaitteen rekisterit C-rakenteena ja tarkistaa sen
  siirtymät käännösaikana.
- Osaat asettaa, nollata, vaihtaa ja testata bittejä ja päivittää
  monibittisen kentän.
- Osaat tunnistaa luku–muutos–kirjoitus-operaation vaarat ja W1C-bittien
  oikean kuittauksen.
- Osaat luetella GPIO-lohkon tyypilliset rekisterit ja syyt, miksi
  nasta ei tottele.
