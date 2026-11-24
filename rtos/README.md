# Reaaliaikakäyttöjärjestelmät

Tiivis suomenkielinen tutoriaali reaaliaikakäyttöjärjestelmistä
Cortex-M:llä: tehtävät ja prioriteettipohjainen vuorontaminen,
kontekstinvaihto, keskeytykset, jonot, semaforit, mutexit ja
prioriteetin inversio, ajoitusanalyysi sekä muistinhallinta.
Esimerkit ajetaan omalla pienellä opetusytimellä (*Kide*), jonka
rajapinta jäljittelee FreeRTOSia. Valmiit dokumentit:
[rtos.pdf](https://saperant.github.io/tutoriaalit/materiaalit/rtos.pdf)
ja pikaopas
[rtos-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/rtos-pikaopas.pdf).

## Sisältö

1. Johdanto – miksi RTOS, Kide-ydin, laboratorio ja ensimmäinen ohjelma
2. Reaaliaikaisuus – määräajat, vasteaika, huojunta, tikki,
   `vTaskDelay` ja `vTaskDelayUntil`
3. Tehtävät ja vuorontaminen – tilat, valmislistat ja bittikartta,
   etuoikeutus, vuorottelu, idle ja tikitön uni
4. Kontekstinvaihto – PSP ja MSP, kehys, PendSV, SVC, portin rajapinta
5. Keskeytykset ja RTOS – FromISR, viivästetty käsittely, BASEPRI
6. Jonot – kopiointi, odotus ja herääminen, tuottaja ja kuluttaja,
   UART-komentotulkki
7. Semaforit, tapahtumaryhmät ja ilmoitukset
8. Mutexit ja prioriteetin inversio – periytys, prioriteettikatto,
   Mars Pathfinder
9. Ajoitusanalyysi – RMS, Liu–Laylandin raja, vasteaika-analyysi, WCET
10. Muistinhallinta – heap_1–heap_5, muistipooli, pinon mitoitus ja
    ylivuoto
11. Testaus isäntäkoneella – isäntäportti ja testitasot
12. FreeRTOS ja Zephyr – vastaavuudet, muut ytimet, sertifiointi
13. Lopuksi – nyrkkisäännöt ja lähteet

## Esimerkit

`esimerkit/kide/` on ydin ja sen Cortex-M3-portti, `esimerkit/isanta/`
isäntäportti (Linux, ucontext) ja `esimerkit/yhteinen/` käynnistyskoodi,
linkkeriskripti ja konsoli taidosta *Mikrokontrollerit*.
`esimerkit/NN-nimi/` ovat esimerkkiohjelmia QEMU:n
`mps2-an385`-kortille. Jokaisen ohjelman tuloste ja paluuarvo verrataan
tiedostoon `esimerkit/testit/<nimi>.odotettu`. QEMU ajetaan
`-icount`-valitsimella, joten ajo on deterministinen. Laitteistoa
käyttämättömät esimerkit käännetään lisäksi isäntäkoneelle
sanitoijien kanssa ja verrataan samaan odotettuun tulosteeseen.

## Rakentaminen

```text
make testaa   # rakenne ja esimerkit (esimerkit/Makefile)
make pdf      # tutoriaali ja pikaopas
```

Tarvitaan `gcc-arm-none-eabi`, `libnewlib-arm-none-eabi`,
`qemu-system-arm` ja isäntäkoneen C-kääntäjä; kehityskontissa
(`.devcontainer/rtos`) ne ovat valmiina.
