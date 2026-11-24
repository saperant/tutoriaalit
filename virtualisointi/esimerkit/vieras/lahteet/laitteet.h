/* Vieraan "ajurit": I/O-portit, sarjaportti ja QEMU:n
 * isa-debug-exit-laite. Jokainen in- ja out-käsky on virtuaalikoneessa
 * VM exit: hypervisor emuloi laitteen. */
#ifndef LAITTEET_H
#define LAITTEET_H
#include <stdint.h>

#define COM1      0x3f8   /* sarjaportin datarekisteri */
#define COM1_LSR  0x3fd   /* linjan tilarekisteri */
#define LOPETUS   0xf4    /* isa-debug-exit */

static inline void outb(uint16_t portti, uint8_t arvo)
{
    __asm__ volatile("outb %0, %1" : : "a"(arvo), "Nd"(portti));
}

static inline uint8_t inb(uint16_t portti)
{
    uint8_t arvo;
    __asm__ volatile("inb %1, %0" : "=a"(arvo) : "Nd"(portti));
    return arvo;
}

static inline void tulosta(const char *s)
{
    while (*s)
        outb(COM1, (uint8_t)*s++);
}

/* QEMU päättyy paluuarvolla (koodi << 1) | 1. */
static inline void lopeta(uint8_t koodi)
{
    outb(LOPETUS, koodi);
}
#endif
