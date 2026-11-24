/* Kide-ytimen asetukset. Nimet ovat samat kuin FreeRTOSin
 * FreeRTOSConfig.h-tiedostossa, jotta vastaavuus näkyy suoraan.
 * Esimerkki voi ohittaa asetuksen käännösvalitsimella, esimerkiksi
 * -DconfigUSE_TIME_SLICING=0. */
#ifndef KIDE_ASETUKSET_H
#define KIDE_ASETUKSET_H

// @alku asetukset
/* Tikin taajuus: 1000 Hz eli yksi tikki millisekunnissa. */
#define configTICK_RATE_HZ        1000u

/* Prioriteetit 0..7; suurempi luku on tärkeämpi (kuten FreeRTOSissa,
 * mutta päinvastoin kuin NVIC:n keskeytysprioriteetit). */
#define configMAX_PRIORITIES      8u

/* Saman prioriteetin tehtävät vuorottelevat tikin välein. */
#ifndef configUSE_TIME_SLICING
#define configUSE_TIME_SLICING    1
#endif

/* Mutex perii odottajan prioriteetin (luku 8). */
#ifndef configUSE_PRIORITY_INHERITANCE
#define configUSE_PRIORITY_INHERITANCE 1
#endif

/* Pinon ylivuodon tarkistus jokaisessa tehtävänvaihdossa (luku 10). */
#define configCHECK_FOR_STACK_OVERFLOW 1

/* Idle-tehtävän pino sanoina (4 tavua). */
#define configMINIMAL_STACK_SIZE  128u

/* Ytimen omat keskeytykset (SysTick, PendSV) heikoimmalla
 * prioriteetilla. Keskeytykset, joiden NVIC-prioriteetti on luku-
 * arvoltaan vähintään configMAX_SYSCALL_INTERRUPT_PRIORITY, saavat
 * kutsua FromISR-funktioita; kiireellisempiä ydin ei koskaan peitä.
 * Arvot ovat 8-bittisiä kenttiä: Cortex-M3:ssa 3 ylintä bittiä. */
#define configKERNEL_INTERRUPT_PRIORITY      (7u << 5)
#define configMAX_SYSCALL_INTERRUPT_PRIORITY (5u << 5)

/* Dynaamisen muistin (heap_1) koko tavuina (luku 10). */
#define configTOTAL_HEAP_SIZE     4096u
// @loppu asetukset

#endif
