# Lopuksi {.runko-lahteet}

## Nyrkkisäännöt

1. **Lue piirin käyttöohje ja ytimen käyttöopas.** Jokainen rekisteri,
   bitti ja sivuvaikutus on kuvattu niissä; arvaaminen maksaa päiviä.
2. **Kirjoita vikakäsittelijä ja oletuskäsittelijä ensin.** Ne
   kertovat, missä ja miksi ohjelma pysähtyi.
3. **`volatile` rekistereille ja jaetuille muuttujille, mutta ei
   atomisuuden korvikkeena.** Luku–muutos–kirjoitus suojataan.
4. **Kuittaa keskeytyksen syy ja pidä käsittelijä lyhyenä.** Työ
   siirretään pääohjelmalle jonon kautta.
5. **Kriittinen osio tallentaa ja palauttaa PRIMASKin** ja on
   muutaman käskyn mittainen.
6. **Laske aika etumerkittömällä erotuksella** ja testaa laskurin
   pyörähdys.
7. **Nuku, kun työtä ei ole**, ja tee tarkistus ja WFI keskeytykset
   kiellettyinä.
8. **Mikään pääsilmukan funktio ei odota.** Odottava toiminta on
   tilakone.
9. **Erota logiikka ajureista** ja testaa se isäntäkoneella.
10. **Laukaise kilpailutilanteet tarkoituksella testissä.** Satunnaisesti
    ilmenevää virhettä ei löydä odottamalla.

## Oikeaan laitteeseen

Esimerkit siirtyvät oikealle kehityskortille muuttamalla neljää asiaa:
linkkeriskriptin muistialueet, vektoritaulun ulkoiset keskeytykset ja
`mps2.h`:n oheislaitteet piirin käyttöohjeen mukaan sekä
käynnistyskoodiin kellojen, oheislaitteiden kellojen ja nastojen
alustus. Ytimen osat (NVIC, SysTick, SCB, MPU, vikakäsittelijä) toimivat
sellaisinaan. Edullisia aloituskortteja ovat esimerkiksi ST:n Nucleo-
ja Discovery-kortit (Cortex-M0+–M7), Nordicin nRF52- ja
nRF54-kehityskortit (Cortex-M4 ja M33) sekä Raspberry Pi Pico ja Pico 2
(Cortex-M0+ ja M33). Kahdessa ensimmäisessä on debug-sovitin mukana,
Picolle tarvitaan erillinen, esimerkiksi Raspberry Pi Debug Probe.

## Jatkotaidot

- *Oheislaiteväylät*: UART, SPI, I2C, CAN ja DMA sekä ajurikerrosten
  suunnittelu; myös ulkoinen A/D-muunnin SPI-väylässä
- *Reaaliaikakäyttöjärjestelmät*: säikeet, ajoitus, synkronointi ja
  prioriteetti-inversio; jatkaa luvun 5 PendSV:stä ja prosessipinosta
  säikeenvaihtoon
- *Digitaalinen signaalinkäsittely*: mitä ajastimen tahdittamilla
  näytteillä tehdään
- *Laiteohjelmiston takaisinmallinnus*: valmiin laiteohjelmiston
  purkaminen ja analyysi
- *Sulautettujen järjestelmien tietoturva*: turvallinen käynnistys,
  päivitykset ja debug-portin suojaus
- *Sulautettu Linux*: kun laite on niin suuri, että siinä on
  muistinhallintayksikkö ja käyttöjärjestelmä.

## Lähteet

ARM:n dokumentaatio (<https://developer.arm.com/documentation>):

- *ARMv7-M Architecture Reference Manual* (DDI 0403). Käskyt,
  poikkeusmalli, muistimalli ja järjestelmärekisterit.
- *Cortex-M3 Devices Generic User Guide* (DUI 0552). Ohjelmoijan
  näkökulma ytimeen; vastaavat oppaat ovat muillekin ytimille.
- *Cortex-M System Design Kit Technical Reference Manual* (DDI 0479).
  CMSDK:n UART, ajastimet ja GPIO.
- *Application Note AN385: ARM Cortex-M3 SMM on V2M-MPS2*. Esimerkkien
  kohdekortin muistikartta ja keskeytykset.
- *Procedure Call Standard for the Arm Architecture* (AAPCS).
- CMSIS: *Common Microcontroller Software Interface Standard*.
  <https://arm-software.github.io/CMSIS_6/>

Työkalut:

- QEMU: *Arm MPS2 and MPS3 boards* ja *GDB usage*.
  <https://www.qemu.org/docs/master/>
- GNU-linkkerin käsikirja, luku *Linker Scripts*.
  <https://sourceware.org/binutils/docs/ld/>
- *Debugging with GDB*. <https://sourceware.org/gdb/documentation/>
- Arm GNU Toolchain. <https://developer.arm.com/downloads/-/arm-gnu-toolchain-downloads>

Kirjat ja artikkelit:

- Joseph Yiu: *The Definitive Guide to ARM Cortex-M3 and Cortex-M4
  Processors*. 3. painos, Newnes, 2014.
- Joseph Yiu: *Definitive Guide to Arm Cortex-M23 and Cortex-M33
  Processors*. Newnes, 2020.
- Elecia White: *Making Embedded Systems*. 2. painos, O'Reilly, 2024.
- Miro Samek: *Practical UML Statecharts in C/C++*. 2. painos, Newnes,
  2008.
- Jack Ganssle: *A Guide to Debouncing*. <http://www.ganssle.com/debouncing.htm>
- Memfault Interrupt -blogi: *How to debug a HardFault on an ARM
  Cortex-M MCU* ja *A Practical guide to ARM Cortex-M Exception
  Handling*. <https://interrupt.memfault.com/>

Tämä teos on lisensoitu Creative Commons Nimeä–JaaSamoin 4.0
Kansainvälinen -lisenssillä (CC BY-SA 4.0).
