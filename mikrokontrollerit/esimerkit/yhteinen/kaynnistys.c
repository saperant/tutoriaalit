/* Käynnistyskoodi: vektoritaulu ja Reset_Handler.
 *
 * Kaikki tässä on tavallista C:tä. Cortex-M lukee pinon alkuarvon ja
 * Reset_Handlerin osoitteen vektoritaulusta itse, joten C-koodi voi
 * alkaa heti ensimmäisestä käskystä. */
#include <stdint.h>

#include "konsoli.h"
#include "mps2.h"
#include "semihost.h"

// @alku symbolit
/* Linkkeriskriptin symbolit: vain osoitteella on merkitystä. */
extern uint32_t _data_alku[], _data_loppu[], _data_lataus[];
extern uint32_t _bss_alku[], _bss_loppu[];
extern uint32_t _pinon_huippu[];
// @loppu symbolit

int main(void);
void Reset_Handler(void);
void Oletus_Handler(void);

// @alku heikot
/* Käsittelijät ovat heikkoja aliaksia: ohjelma korvaa haluamansa
 * määrittelemällä samannimisen funktion. */
#define OLETUS __attribute__((weak, alias("Oletus_Handler")))
void NMI_Handler(void) OLETUS;
void HardFault_Handler(void) OLETUS;
void MemManage_Handler(void) OLETUS;
void BusFault_Handler(void) OLETUS;
void UsageFault_Handler(void) OLETUS;
void SVC_Handler(void) OLETUS;
void DebugMon_Handler(void) OLETUS;
void PendSV_Handler(void) OLETUS;
void SysTick_Handler(void) OLETUS;
void UART0RX_IRQHandler(void) OLETUS;
void UART0TX_IRQHandler(void) OLETUS;
void TIMER0_IRQHandler(void) OLETUS;
void TIMER1_IRQHandler(void) OLETUS;
void VAPAA0_IRQHandler(void) OLETUS;
void VAPAA1_IRQHandler(void) OLETUS;
void VAPAA2_IRQHandler(void) OLETUS;
// @loppu heikot

// @alku vektorit
typedef void (*kasittelija_t)(void);

__attribute__((section(".vektorit"), used))
static const kasittelija_t vektorit[16 + 16] = {
    (kasittelija_t)_pinon_huippu, /* 0: pinon alkuarvo (MSP) */
    Reset_Handler,                /* 1 */
    NMI_Handler,                  /* 2 */
    HardFault_Handler,            /* 3 */
    MemManage_Handler,            /* 4 */
    BusFault_Handler,             /* 5 */
    UsageFault_Handler,           /* 6 */
    0, 0, 0, 0,                   /* 7..10 varattu */
    SVC_Handler,                  /* 11 */
    DebugMon_Handler,             /* 12 */
    0,                            /* 13 varattu */
    PendSV_Handler,               /* 14 */
    SysTick_Handler,              /* 15 */
    /* Ulkoiset keskeytykset: poikkeus 16 + IRQ-numero. */
    [16 + UART0RX_IRQn] = UART0RX_IRQHandler,
    [16 + UART0TX_IRQn] = UART0TX_IRQHandler,
    [16 + 2 ... 16 + 7] = Oletus_Handler,
    [16 + TIMER0_IRQn] = TIMER0_IRQHandler,
    [16 + TIMER1_IRQn] = TIMER1_IRQHandler,
    [16 + 10 ... 16 + 12] = Oletus_Handler,
    [16 + VAPAA0_IRQn] = VAPAA0_IRQHandler,
    [16 + VAPAA1_IRQn] = VAPAA1_IRQHandler,
    [16 + VAPAA2_IRQn] = VAPAA2_IRQHandler,
};
// @loppu vektorit

// @alku reset
void Reset_Handler(void) {
#ifndef ILMAN_ALUSTUSTA
    /* .data: alkuarvot flashista (LMA) RAMiin (VMA). */
    const uint32_t *lahde = _data_lataus;
    for (uint32_t *kohde = _data_alku; kohde < _data_loppu;) {
        *kohde++ = *lahde++;
    }
    /* .bss: C-standardin mukaan staattiset muuttujat alkavat nollina. */
    for (uint32_t *kohde = _bss_alku; kohde < _bss_loppu;) {
        *kohde++ = 0;
    }
#endif
    /* Tähän kuuluisivat myös kellojen ja FPU:n alustus. */
    int koodi = main();
    lopeta(koodi);
}
// @loppu reset

// @alku oletus
/* Odottamaton poikkeus. Tuotantolaitteessa tässä kirjattaisiin syy ja
 * käynnistettäisiin laite uudelleen; testeissä ajo lopetetaan. */
void Oletus_Handler(void) {
    uint32_t ipsr;
    __asm__ volatile("mrs %0, ipsr" : "=r"(ipsr));
    tulosta("odottamaton poikkeus %u\n", (unsigned)ipsr);
    lopeta(99);
}
// @loppu oletus
