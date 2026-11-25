# Lopuksi {.runko-lahteet}

## Nyrkkisäännöt

- **Prioriteetit aikarajojen mukaan.** Lyhyin jakso tai määräaika
  korkeimmalle, ja vasteajat lasketaan.
- **Jaksolliset tehtävät `vTaskDelayUntil`illa.** `vTaskDelay`
  ajelehtii.
- **Kukaan ei pyöri.** Tehtävä odottaa jonossa, semaforissa tai
  ilmoituksessa, ei kysele lippua.
- **Keskeytys on lyhyt.** Kuittaus, välttämätön data, herätys ja
  `portYIELD_FROM_ISR`. Raskas työ tehtävään.
- **Keskeytysprioriteetit asetetaan itse.** Ytimen kanssa toimivat
  keskeytykset `configMAX_SYSCALL_INTERRUPT_PRIORITY`n puolelle, nopeimmat
  ytimen ohi.
- **Yhteinen resurssi mutexilla**, merkinanto semaforilla tai
  ilmoituksella. Kriittinen alue lyhyeksi.
- **Odotuksilla on aikarajat**, ja aikarajan täyttyminen on virhe, josta
  kerrotaan.
- **Muisti varataan staattisesti** tai käynnistyksessä, ajonaikaiset
  viestit poolista.
- **Pinot mitataan**, ja ylivuoto tunnistetaan laitteistolla, jos
  mahdollista.
- **`configASSERT` päällä kehityksessä.** Se löytää virheet, jotka
  muuten näkyvät satunnaisina kaatumisina.
- **Testit kahdella tasolla.** Logiikka isännällä, ajoitus ja laitteet
  emulaattorissa tai laitteessa, ajot deterministisiksi.

## Jatkotaidot

- *Oheislaiteväylät*: UART, SPI, I2C, CAN ja DMA sekä ajurien
  rakenne, jossa RTOSin jonot ja ilmoitukset ovat ajurin ja sovelluksen
  rajapinta
- *Laiteohjelmiston takaisinmallinnus*: valmiin laiteohjelmiston
  tehtävien, jonojen ja ytimen tunnistaminen konekoodista
- *Sulautettujen järjestelmien tietoturva*: turvallinen käynnistys,
  päivitykset ja tehtävien eristäminen MPU:lla
- *Sulautettu Linux*: kun laitteessa on muistinhallintayksikkö ja
  ohjelmistoa on paljon, Linux ja sen reaaliaikalaajennus
  (PREEMPT_RT) korvaavat RTOSin
- *Digitaalinen signaalinkäsittely*: reaaliaikainen näytteiden
  käsittely, jossa tämän tutoriaalin määräajat ja jonot ovat
  käytössä.

## Lähteet

Reaaliaikateoria:

- C. L. Liu ja J. W. Layland: *Scheduling Algorithms for
  Multiprogramming in a Hard-Real-Time Environment*. Journal of the
  ACM 20(1), 1973. RMS ja käyttöasteen raja.
- M. Joseph ja P. Pandya: *Finding Response Times in a Real-Time
  System*. The Computer Journal 29(5), 1986. Vasteaika-analyysi.
- N. Audsley, A. Burns, M. Richardson, K. Tindell ja A. Wellings:
  *Applying New Scheduling Theory to Static Priority Pre-emptive
  Scheduling*. Software Engineering Journal 8(5), 1993. Estoajat ja
  huojunta analyysissä.
- L. Sha, R. Rajkumar ja J. P. Lehoczky: *Priority Inheritance
  Protocols: An Approach to Real-Time Synchronization*. IEEE
  Transactions on Computers 39(9), 1990. Periytys ja prioriteettikatto.
- Giorgio Buttazzo: *Hard Real-Time Computing Systems*. 3. painos,
  Springer, 2011. Laaja oppikirja vuorontamisesta ja analyysistä.
- Mike Jones: *What really happened on Mars?* RISKS Digest 19(49),
  1997. Mars Pathfinderin prioriteetin inversio Glenn Reevesin
  kertomana.

Ytimet:

- FreeRTOS: ytimen dokumentaatio, rajapintaviite ja asetukset.
  <https://www.freertos.org/>
- Richard Barry: *Mastering the FreeRTOS Real Time Kernel – a Hands-On
  Tutorial Guide*. Ilmainen opas FreeRTOSin sivustolla.
- FreeRTOS-Kernel: lähdekoodi ja portit.
  <https://github.com/FreeRTOS/FreeRTOS-Kernel>
- Zephyr Project: dokumentaatio, erityisesti *Kernel Services*.
  <https://docs.zephyrproject.org/>
- Eclipse ThreadX. <https://github.com/eclipse-threadx>
- CMSIS-RTOS2. <https://arm-software.github.io/CMSIS_6/>

Laitteisto ja työkalut:

- ARM: *ARMv7-M Architecture Reference Manual* (DDI 0403).
  Poikkeusmalli, EXC_RETURN, PendSV ja BASEPRI.
  <https://developer.arm.com/documentation>
- Joseph Yiu: *The Definitive Guide to ARM Cortex-M3 and Cortex-M4
  Processors*. 3. painos, Newnes, 2014. Luvut käyttöjärjestelmätuesta
  ja kontekstinvaihdosta.
- QEMU: *Arm MPS2 and MPS3 boards* ja *TCG Instruction Counting*
  (`-icount`). <https://www.qemu.org/docs/master/>

Kide on kirjoitettu tätä tutoriaalia varten, ja sen rajapinta jäljittelee
FreeRTOSia. FreeRTOSin koodia ei ole kopioitu.
