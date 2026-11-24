# Lopuksi {.runko-lahteet}

## Nyrkkisäännöt

1. **Lue datalehti ja väylän määrittely.** Ajoituskaavio, moodi,
   bittijärjestys, osoite ja virheiden käytös ovat siellä.
2. **Katso linjaa.** Logiikka-analysaattori dekoodaa väylän, ja
   oskilloskooppi näyttää reunat ja tasot. Suurin osa väylävioista
   näkyy minuutissa.
3. **Rajaa jokainen odotus ja palauta virhe.** Väylä voi jumiutua,
   laite voi kadota ja johdin irrota.
4. **Kehystä ja tarkista.** Tavuvirta tarvitsee erottimen ja CRC:n,
   ja jokainen viesti kuittauksen.
5. **Suunnittele puskurit ja vuonohjaus.** Täysi puskuri pysäyttää
   lähettäjän, se ei hukkaa dataa hiljaa.
6. **Erota laiteajuri väylästä ja testaa se mallia vastaan.**
7. **Älä usko emulaattoria laitteen yksityiskohdissa.** Testaa
   lopuksi oikealla piirillä.

## Oikeaan laitteeseen

Esimerkit siirtyvät oikeaan piiriin kolmessa kohdassa. Rekisterien
määrittelyt (`mps2.h`, `pl081.h`) korvataan valmistajan CMSIS-
otsakkeilla, väyläohjaimet piirin omilla lohkoilla, ja odotusrajat
mitataan ajassa kierrosten sijasta. Laiteajurit (`at24.c`, MAX1111:n
funktiot) siirtyvät sellaisinaan.

Linjan katsomiseen riittää aluksi edullinen USB-logiikka-analysaattori
ja avoin sigrok-ohjelmisto (PulseView). Niissä on dekooderit UARTille,
SPI:lle, I2C:lle ja CANille sekä monille laitteille, esimerkiksi
SPI-flashille ja EEPROMille. CAN-väylää kuunnellaan Linuxissa USB-
sovittimella ja SocketCANilla (`candump`, `cansend`). Ensimmäinen
kokeilu kannattaa tehdä kahdella mikrokontrollerilla pöydällä
ennen kuin laite kytketään autoon tai koneeseen.

## Lähteet

Väylien määrittelyt:

- NXP: *UM10204, I2C-bus specification and user manual*. Rev. 7.0,
  2021. <https://www.nxp.com/docs/en/user-guide/UM10204.pdf>
- Bosch: *CAN Specification Version 2.0*, 1991, sekä ISO 11898-1
  (CAN ja CAN FD, datalinkkikerros) ja ISO 11898-2 (lähetinpiiri).
- CAN in Automation (CiA): bitin ajoituksen ja väylän pituuden
  suositukset. <https://www.can-cia.org/>
- SMBus Specification, versio 3.x. <http://smbus.org/specs/>
- TIA/EIA-485 ja TIA/EIA-232: RS-485:n ja RS-232:n sähköiset
  määrittelyt.
- JEDEC JESD216: *Serial Flash Discoverable Parameters (SFDP)*.
- Stuart Cheshire, Mary Baker: *Consistent Overhead Byte Stuffing*.
  IEEE/ACM Transactions on Networking 7(2), 1999.

Oheislaitteet ja piirit:

- ARM: *PrimeCell Synchronous Serial Port (PL022) Technical Reference
  Manual* (DDI 0194) ja *PrimeCell DMA Controller (PL080/PL081)
  Technical Reference Manual* (DDI 0196 ja DDI 0218).
- ARM: *Cortex-M System Design Kit Technical Reference Manual*
  (DDI 0479). CMSDK-UART.
- ARM: *Application Note AN385* ja *AN505*: MPS2-korttien
  muistikartat. <https://developer.arm.com/documentation>
- Analog Devices (Maxim): MAX1110/MAX1111-datalehti. Texas
  Instruments: TMP105-datalehti. Microchip: 24C02-datalehti ja
  sovellusohje ACK-kyselystä.
- QEMU: *Arm MPS2 and MPS3 boards* ja laitemallien lähdekoodi
  (`hw/ssi/pl022.c`, `hw/i2c/bitbang_i2c.c`, `hw/dma/pl080.c`).
  <https://www.qemu.org/docs/master/>

Kirjat ja artikkelit:

- Elecia White: *Making Embedded Systems*. 2. painos, O'Reilly, 2024.
  Luvut oheislaitteista ja ajurien rakenteesta.
- Joseph Yiu: *Definitive Guide to Arm Cortex-M23 and Cortex-M33
  Processors*. Newnes, 2020. DMA ja TrustZone-ympäristö.
- Steve Corrigan: *Introduction to the Controller Area Network
  (CAN)*. Texas Instruments, sovellusraportti SLOA101.
- Arm: *Cortex-M7 Processor Technical Reference Manual*. Välimuisti
  ja sen ylläpito.
- sigrok-projekti: protokolladekooderien dokumentaatio.
  <https://sigrok.org/wiki/Protocol_decoders>

Tämä teos on lisensoitu Creative Commons Nimeä–JaaSamoin 4.0
Kansainvälinen -lisenssillä (CC BY-SA 4.0).
