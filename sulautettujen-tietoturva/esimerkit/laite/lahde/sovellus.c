/* Sovellus: kertoo versionsa ja paikkansa ja lopettaa. */
#include <stdint.h>

#include "semihost.h"

#ifndef VERSIO
#error "VERSIO puuttuu"
#endif

#define SCB_VTOR (*(volatile uint32_t *)0xE000ED08u)

void sovellus(void) {
    tulosta("Sovellus versio ");
    tulosta_luku(VERSIO);
    tulosta(SCB_VTOR < 0x00180000u ? " käynnissä paikasta A\n"
                                   : " käynnissä paikasta B\n");
    lopeta(0);
}

extern uint32_t _pino;
__attribute__((section(".vektorit"), used))
static const void *const vektorit[2] = {&_pino, sovellus};
