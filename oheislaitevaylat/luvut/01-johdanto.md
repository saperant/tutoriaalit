# Johdanto {.runko-johdanto}

Mikrokontrolleri on harvoin yksin. Se lukee antureita, kirjoittaa
näytölle ja muistiin, ohjaa moottoreita ja keskustelee muiden
laitteiden kanssa. Piirien välillä tieto kulkee sarjaväylillä:
muutamalla johtimella, joita pitkin bitit siirtyvät peräkkäin. Väylä
on aina kahden asian summa. Linjalla on sähköinen ja ajallinen
protokolla, eli mitä jännitteet tarkoittavat ja milloin niitä
luetaan. Ohjelmassa on ajuri, joka muuttaa tämän protokollan
funktioiksi, kuten `lue_rekisteri` tai `laheta_kehys`.

Tämä tutoriaali käsittelee molempia:

- **väylien perusteita**: synkroninen ja asynkroninen siirto,
  pisteestä pisteeseen ja monipisteväylät, avokollektorilähdöt ja
  vetovastukset, jännitetasot ja differentiaalinen siirto
- **UARTia**: kehys, pariteetti, baudinopeuden virhe ja sen sieto,
  vuonohjaus, RS-232 ja RS-485 sekä kehysprotokolla tavuvirran päällä
- **SPI:tä**: kellon napaisuus ja vaihe, piirinvalinta, ketjutus ja
  tyypilliset laitteet, kuten flash-muisti ja A/D-muunnin
- **I2C:tä**: START ja STOP, osoitteet ja kuittaukset, rekisterien
  luku, kellonvenytys, arbitraatio ja jumiutuneen väylän vapautus
- **CANia**: dominantti ja resessiivinen taso, arbitraatio tunnisteella,
  bittitäyttö, CRC, virhelaskurit ja bitin ajoitus
- **DMA:ta**: kanavat, kuvaajaketjut, muistiaidat ja välimuistin
  yhtenäisyys
- **ajurikerroksia**: rajapinnat, virheiden käsittely ja aikarajat sekä
  ajurin testaus isäntäkoneella mallia vastaan.

Esitiedoiksi oletetaan taito *Mikrokontrollerit ja bare-metal-
ohjelmointi*: Cortex-M:n muistikartta, käynnistyskoodi, muistiin
kuvatut rekisterit ja `volatile`, keskeytykset ja NVIC sekä
keskeytyksen ja pääohjelman yhteinen data. Niitä ei toisteta tässä.
Taidot *Reaaliaikakäyttöjärjestelmät*, *Linux-ajurit* ja
*Laiteohjelmiston takaisinmallinnus* jatkavat tästä. Digitaalisen
logiikan puolelta väylät näkyvät taidoissa *RTL-suunnittelu* ja
*SoC-integraatio*, ja siirtoteiden fysiikka taidossa
*Tietoliikennetekniikka*.

## Laboratorio

Väylää opetellaan parhaiten logiikka-analysaattorin ja oikean laitteen
kanssa, mutta tutoriaalin esimerkit on tehty niin, että jokainen
tuloste voidaan testata. Työkaluja on kaksi.

**QEMU ja emuloidut laitteet.** Cortex-M-ohjelmat ajetaan QEMU:n
`mps2-an385`-kortilla samoin kuin paketissa *Mikrokontrollerit*.
Kortilla on viisi CMSDK-UARTia, viisi ARM:n PL022-SPI-lohkoa ja neljä
SBCon-lohkoa, joilla ohjelma ohjaa I2C-väylän linjoja itse. QEMU
osaa kytkeä väyliin emuloituja laitteita komentoriviltä:

```{.make tiedosto="esimerkit/Makefile" osa="laitteet"}
```

Laboratoriossa on siis lämpötila-anturi TMP105 ja EEPROM-muisti
(24C02-tyyppinen, 256 tavua) I2C-väylällä sekä nelikanavainen
A/D-muunnin MAX1111 SPI-väylällä. UART1 lukee tavunsa tiedostosta ja
kirjoittaa lähettämänsä toiseen tiedostoon, joten toista päätä voi
esittää isäntäkoneen ohjelma. DMA-esimerkki ajetaan kortilla
`mps2-an505` (Cortex-M33), koska sen mallissa on ARM:n PL081-DMA-ohjain.

**Python-mallit.** QEMU:n laitteet toimivat tavutasolla: ne eivät
tuota jännitteitä eivätkä ajoitusta, eikä niissä ole CAN-väylää
lainkaan. Siksi linjatason ilmiöt näytetään Python-malleilla
(`esimerkit/python/mallit/`). Ne tuottavat linjojen tasot
aika-askelittain, ja dekooderit purkavat ne takaisin kuten
logiikka-analysaattori. Mallien aaltomuodot piirretään tekstinä:
ylätaso on ylemmän rivin viiva, alataso alemman ja pystyviiva
merkitsee muutosta (`python/mallit/aalto.py`).

Mallit tarkistetaan työkaluilla ruff ja `mypy --strict`, ja niiden
yksikkötestit (`esimerkit/python/testit/`) ajetaan pytestillä. Testit
käyvät läpi satunnaisia syötteitä kiinteällä siemenellä: esimerkiksi
jokaisen CAN-kehyksen on kuljettava täytön, CRC:n ja purun läpi
ehjänä, ja jokaisen yksittäisen bittivirheen on jäätävä kiinni.

Kolmas osa ovat ajurien **isäntätestit**: luvun 8 ajurit käännetään
myös isäntäkoneen kääntäjällä sanitoijien kanssa ja ajetaan
laitemalleja vastaan.

Esimerkkihakemiston Makefile kääntää ja ajaa kaiken. Kunkin
Cortex-M-ohjelman tuloste ja paluuarvo verrataan tiedostoon
`testit/<nimi>.odotettu`:

```{.make tiedosto="esimerkit/Makefile" osa="liput"}
```

```{.make tiedosto="esimerkit/Makefile" osa="ajo"}
```

Komennot esimerkkihakemistossa:

```text
make                  # kaikki: QEMU-ajot, isäntätestit, Python-mallit
make aja E=05-i2c     # yksi ohjelma päätteessä
make -C python        # vain Python-mallit
make siivoa
```

Tarvittavat paketit (Debian ja Ubuntu) ovat `gcc-arm-none-eabi`,
`libnewlib-arm-none-eabi` ja `qemu-system-arm` sekä Pythonin puolella
`ruff`, `mypy` ja `pytest`. Kehityskontissa
`.devcontainer/oheislaitevaylat` ne ovat valmiina. Esimerkit eivät
riipu ajoituksesta: QEMU ajaa ohjelmia eri nopeudella kuormituksen
mukaan, joten yksikään tulos ei perustu kellonaikaan.

## Ensimmäinen ohjelma: kuka väylällä on?

Ennen kuin ajuri koskee laitteeseen, sen kannattaa varmistaa, että
osoitteessa on oikea laite. ARM:n oheislaitteissa osoitealueen lopussa
on tunnistelohko: osanumero, valmistajan JEP106-tunnus ja versio.

```{.c tiedosto="esimerkit/01-tunnistus/main.c" osa="tunniste"}
```

```{.c tiedosto="esimerkit/01-tunnistus/main.c" osa="main"}
```

```{.tuloste tiedosto="esimerkit/testit/01-tunnistus.odotettu"}
```

UARTit ovat CMSDK:n osa `0x821`. SPI-lohko on PrimeCell PL022
(`0x022`) ja valmistajatunnus `0x41` eli ASCII-merkki `A`, jota ARM
käyttää PrimeCell-lohkoissa. Valmistajien omissa oheislaitteissa
vastaava tieto on usein piirin tunnisterekisterissä, ja ulkoisissa
piireissä tunnisterekisterissä (I2C-anturit) tai erillisellä
komennolla (SPI-flashin `0x9F`). Tunnisteen tarkistus maksaa muutaman
väyläsiirron. Se löytää väärin juotetun piirin, väärän osoitteen
ja kopioidun koodin, joka olettaa eri laitteen.

Paketin luvut etenevät linjalta ylöspäin. Luku 2 käsittelee
väylien sähköiset perusteet, luvut 3–6 yksittäiset väylät, luku 7 DMA:n
ja luku 8 ajurin rakenteen ja testauksen.
