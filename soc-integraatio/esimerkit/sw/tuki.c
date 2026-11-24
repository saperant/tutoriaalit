/* Tukikirjasto: MMIO-ajurit UARTille ja SYSCONille sekä ansojen jako. */
#include "tuki.h"

#include <stddef.h>

#include "soc.h"

/* @alku uart */
static void uart_merkki(char c)
{
    while (UART->TILA & 1u) {
        /* odota edellisen merkin lähetystä */
    }
    UART->DATA = (uint8_t)c;
}
/* @loppu uart */

void tulosta(const char *teksti)
{
    while (*teksti) uart_merkki(*teksti++);
}

void tulosta_hex(uint32_t arvo)
{
    static const char numerot[] = "0123456789abcdef";
    uart_merkki('0');
    uart_merkki('x');
    for (int i = 28; i >= 0; i -= 4) uart_merkki(numerot[(arvo >> i) & 15u]);
}

void tulosta_luku(uint32_t arvo)
{
    char puskuri[11];
    int i = 0;
    do {
        puskuri[i++] = (char)('0' + arvo % 10u);   /* libgcc: __umodsi3 */
        arvo /= 10u;
    } while (arvo != 0u);
    while (i > 0) uart_merkki(puskuri[--i]);
}

_Noreturn void lopeta(int koodi)
{
    while (UART->TILA & 1u) {
        /* viimeinen merkki ulos ennen lopetusta */
    }
    SYSCON->LOPETA = (uint32_t)koodi;
    for (;;) {
    }
}

/* @alku ansa */
__attribute__((weak)) void ajastin_keskeytys(void)
{
    tulosta("odottamaton ajastinkeskeytys\n");
    lopeta(2);
}

__attribute__((weak)) void ulkoinen_keskeytys(void)
{
    tulosta("odottamaton ulkoinen keskeytys\n");
    lopeta(2);
}

__attribute__((weak)) uint32_t poikkeus(uint32_t syy, uint32_t mepc,
                                        uint32_t mtval)
{
    tulosta("poikkeus mcause=");
    tulosta_hex(syy);
    tulosta(" mepc=");
    tulosta_hex(mepc);
    tulosta(" mtval=");
    tulosta_hex(mtval);
    tulosta("\n");
    lopeta(3);
}

uint32_t ansa(uint32_t mcause, uint32_t mepc, uint32_t mtval)
{
    if (mcause & 0x80000000u) {             /* keskeytys */
        switch (mcause & 0x7fffffffu) {
        case 7:  ajastin_keskeytys();  break;
        case 11: ulkoinen_keskeytys(); break;
        default: lopeta(4);
        }
        return mepc;                        /* jatka keskeytettyä käskyä */
    }
    return poikkeus(mcause, mepc, mtval);
}
/* @loppu ansa */

/* GCC voi kutsua näitä silmukoiden sijaan myös ilman C-kirjastoa. */
void *memset(void *kohde, int arvo, size_t n)
{
    unsigned char *p = kohde;
    while (n--) *p++ = (unsigned char)arvo;
    return kohde;
}

void *memcpy(void *kohde, const void *lahde, size_t n)
{
    unsigned char *p = kohde;
    const unsigned char *q = lahde;
    while (n--) *p++ = *q++;
    return kohde;
}
