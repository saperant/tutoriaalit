/* Käynnistyskoodi: vektoritaulu ja Reset_Handler (ks. Mikrokontrollerit
 * ja bare-metal-ohjelmointi, luku 3). Sama tiedosto käännetään
 * mps2-an385:lle ja makrolla AN505 mps2-an505:lle. */
#include <stdint.h>

#include "konsoli.h"
#include "mps2.h"
#include "semihost.h"

extern uint32_t _data_alku[], _data_loppu[], _data_lataus[];
extern uint32_t _bss_alku[], _bss_loppu[];
extern uint32_t _pinon_huippu[];

int main(void);
void Reset_Handler(void);
void Oletus_Handler(void);

#define OLETUS __attribute__((weak, alias("Oletus_Handler")))
void NMI_Handler(void) OLETUS;
void HardFault_Handler(void) OLETUS;
void SVC_Handler(void) OLETUS;
void PendSV_Handler(void) OLETUS;
void SysTick_Handler(void) OLETUS;
void UART0RX_IRQHandler(void) OLETUS;
void UART0TX_IRQHandler(void) OLETUS;
void UART1RX_IRQHandler(void) OLETUS;
void UART1TX_IRQHandler(void) OLETUS;

typedef void (*kasittelija_t)(void);

__attribute__((section(".vektorit"), used))
static const kasittelija_t vektorit[16 + 32] = {
    (kasittelija_t)_pinon_huippu, /* 0: pinon alkuarvo (MSP) */
    Reset_Handler,                /* 1 */
    NMI_Handler,                  /* 2 */
    HardFault_Handler,            /* 3 */
    [4 ... 10] = Oletus_Handler,  /* viat; 7..10 varattu */
    SVC_Handler,                  /* 11 */
    Oletus_Handler,               /* 12 */
    0,                            /* 13 varattu */
    PendSV_Handler,               /* 14 */
    SysTick_Handler,              /* 15 */
    /* Ulkoiset keskeytykset: mps2-an385:n UARTit. DMA-esimerkki
     * (mps2-an505) ei käytä keskeytyksiä. */
    [16 + 0] = UART0RX_IRQHandler,
    [16 + 1] = UART0TX_IRQHandler,
    [16 + 2] = UART1RX_IRQHandler,
    [16 + 3] = UART1TX_IRQHandler,
    [16 + 4 ... 16 + 31] = Oletus_Handler,
};

void Reset_Handler(void) {
    const uint32_t *lahde = _data_lataus;
    for (uint32_t *kohde = _data_alku; kohde < _data_loppu;) {
        *kohde++ = *lahde++;
    }
    for (uint32_t *kohde = _bss_alku; kohde < _bss_loppu;) {
        *kohde++ = 0;
    }
    int koodi = main();
    lopeta(koodi);
}

/* Odottamaton poikkeus: tulostetaan numero ja lopetetaan ajo. */
void Oletus_Handler(void) {
    uint32_t ipsr;
    __asm__ volatile("mrs %0, ipsr" : "=r"(ipsr));
    tulosta("odottamaton poikkeus %u\n", (unsigned)ipsr);
    lopeta(99);
}
