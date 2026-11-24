/* Sovelluksen vektoritaulu ja Reset_Handler. Käynnistyslatain asettaa
 * VTOR:n ja pinon ja hyppää Reset_Handleriin. */
#include <stdint.h>

#include "konsoli.h"
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

typedef void (*kasittelija_t)(void);

__attribute__((section(".vektorit"), used))
static const kasittelija_t vektorit[16 + 16] = {
    (kasittelija_t)_pinon_huippu,
    Reset_Handler,
    NMI_Handler,
    HardFault_Handler,
    [4 ... 10] = Oletus_Handler,
    SVC_Handler,
    Oletus_Handler,
    0,
    PendSV_Handler,
    SysTick_Handler,
    UART0RX_IRQHandler,
    [17 ... 31] = Oletus_Handler,
};

void Reset_Handler(void) {
    const uint32_t *lahde = _data_lataus;
    for (uint32_t *kohde = _data_alku; kohde < _data_loppu;) {
        *kohde++ = *lahde++;
    }
    for (uint32_t *kohde = _bss_alku; kohde < _bss_loppu;) {
        *kohde++ = 0;
    }
    lopeta(main());
}

void Oletus_Handler(void) {
    uint32_t ipsr;
    __asm__ volatile("mrs %0, ipsr" : "=r"(ipsr));
    tulosta("VIKA: poikkeus %u\n", (unsigned)ipsr);
    lopeta(99);
}

/* Pinon suojaus (-fstack-protector-strong). Laitteessa ei ole
 * satunnaislukulähdettä, joten vartija on vakio. */
uint32_t __stack_chk_guard = 0x4C54A55Au;

_Noreturn void __stack_chk_fail(void) {
    konsoli_kirjoita("VIKA: pinon suojaus laukesi\n");
    lopeta(98);
}
