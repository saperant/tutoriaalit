---
title: Reaaliaikakäyttöjärjestelmät
subtitle: Pikaopas · tehtävät, keskeytykset, synkronointi, ajoitusanalyysi
---

# Rajapinta

Kide ja FreeRTOS: samat nimet. Paluuarvo `pdPASS`/`pdFAIL`,
aikaraja tikkeinä (`pdMS_TO_TICKS(ms)`), `portMAX_DELAY` = ikuisesti,
0 = ei odotusta.

```{.c tiedosto="esimerkit/kide/kide.h" osa="tehtavat"}
```

```{.c tiedosto="esimerkit/kide/kide.h" osa="jonot"}
```

```{.c tiedosto="esimerkit/kide/kide.h" osa="semaforit"}
```

```{.c tiedosto="esimerkit/kide/kide.h" osa="tapahtumat"}
```

```{.c tiedosto="esimerkit/kide/kide.h" osa="ilmoitukset"}
```

# Prioriteetit

| Mikä | Suunta | Huomio |
|------|--------|--------|
| FreeRTOS, Kide | suurempi tärkeämpi | 0 = idle |
| Zephyr | pienempi tärkeämpi | negatiivinen = ei keskeytetä |
| NVIC | pienempi kiireellisempi | arvo kentän yläbiteissä, oletus 0 |

Cortex-M3: PendSV ja SysTick heikoimmalle (`0xE0`).
FromISR-kutsut sallittu, kun NVIC-prioriteetti ≥
`configMAX_SYSCALL_INTERRUPT_PRIORITY` (`0xA0`); kiireellisemmät eivät
kutsu ydintä, ja BASEPRI ei peitä niitä koskaan.

# Keskeytyskäsittelijä

```{.c tiedosto="esimerkit/06-keskeytys/main.c" osa="isr"}
```

- Kuittaus ensin, data talteen, herätys, `portYIELD_FROM_ISR`.
- Vain FromISR-funktiot: eivät odota, eivät vaihda itse.
- Ei mutexia keskeytyksessä.

# Asetukset

```{.c tiedosto="esimerkit/kide/kide_asetukset.h" osa="asetukset"}
```

FreeRTOSissa lisäksi `configASSERT`, `configUSE_TICKLESS_IDLE`,
`configGENERATE_RUN_TIME_STATS`, `configSUPPORT_STATIC_ALLOCATION`.

# Kontekstinvaihto

| Osa | Sanat | Tallentaja |
|-----|-------|------------|
| r0–r3, r12, lr, pc, xPSR | 8 | laitteisto, poikkeukseen mentäessä |
| r4–r11 | 8 | PendSV ohjelmallisesti |
| s0–s15, FPSCR (M4F) | 18 | laitteisto, laiskasti |
| s16–s31 (M4F) | 16 | PendSV, jos EXC_RETURN:n bitti 4 = 0 |

Tehtävät PSP:llä (CONTROL.SPSEL = 1), keskeytykset MSP:llä.
EXC_RETURN `0xFFFFFFFD` = Thread ja PSP. Uusi tehtävä: valmis kehys,
xPSR = `0x01000000` (Thumb), PC = funktio, LR = virheansa, r0 =
parametri.

# Välineen valinta

| Tarve | Väline |
|-------|--------|
| data tehtävien välillä | jono (kopioi) tai osoitin + pooli |
| ISR herättää yhden tehtävän | tehtäväilmoitus |
| tapahtumien laskenta | laskeva semafori, ilmoitus `pdFALSE` |
| N samanlaista resurssia | laskeva semafori |
| useita ehtoja | tapahtumaryhmä |
| yhteinen resurssi | mutex (periytys) tai vartijatehtävä |

# Ajoitusanalyysi

- Käyttöaste $U = \sum C_i/T_i$. RMS pitää aikarajat varmasti, jos
  $U \le n(2^{1/n}-1)$: 1,000; 0,828; 0,780; 0,757; …; ln 2 ≈ 0,693.
  Harmoniset jaksot: 1,0. EDF: $U \le 1$.
- Vasteaika: $R_i = C_i + B_i + \sum_{j \in hp(i)} \lceil R_i/T_j \rceil C_j$,
  iteroi $R_i = C_i$:stä, kunnes ei muutu tai $R_i > D_i$.
- $B_i$ = pisin mutexin pito vähemmän tärkeällä tehtävällä.
  Huojunta: $\lceil (R_i + J_j)/T_j \rceil$.
- Prioriteetit: lyhin jakso (RMS) tai määräaika (DMS) korkeimmalle.

# Muisti

| Keko | Vapautus | Pirstoutuu | Käyttö |
|------|----------|------------|--------|
| heap_1 | ei | ei | kaikki luodaan käynnistyksessä |
| heap_4 | kyllä, yhdistää | vähän | yleiskäyttöinen |
| heap_5 | kuten heap_4 | vähän | useita muistialueita |
| pooli | kyllä | ei | ajonaikaiset viestit |

Pino: vesiraja `uxTaskGetStackHighWaterMark` (sanoina), varaa
20–50 %, `-fstack-usage`, `-Wstack-usage=N`. Ylivuoto: tarkistus
vaihdossa (`configCHECK_FOR_STACK_OVERFLOW` 1 ja 2), parempi MPU tai
PSPLIM (ARMv8-M).

# Sudenkuopat

- `vTaskDelay` jaksollisessa tehtävässä: ajelehtii.
- Puuttuva `portYIELD_FROM_ISR`: vaste tikin pidempi.
- Keskeytyksen oletusprioriteetti 0 ja FromISR-kutsu: rikkoo ytimen.
- Binäärisemafori resurssin suojana: rajaton inversio.
- Ikuinen odotus: lukkiutuminen näkyy vain jumiutumisena.
- Iso taulukko pinossa: pino kasvaa pysyvästi.
- Väärä portti (M4F-piirissä `ARM_CM3`): liukuluvut sotkeutuvat.
- Tehtäväfunktio palaa: virhe, käytä `vTaskDelete(NULL)`.

# Työkalut

```text
make                       # kaikki esimerkit QEMU:ssa ja isännällä
make aja E=13-inversio     # yksi esimerkki QEMU:ssa
qemu-system-arm -M mps2-an385 -nographic -icount shift=3,sleep=off
```
