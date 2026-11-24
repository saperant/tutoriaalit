/* Virheet: väylävirheet ja muut poikkeukset ansan kautta. */
#include <stdint.h>

#include "soc.h"
#include "tuki.h"

/* @alku poikkeus */
static const char *syyn_nimi(uint32_t syy)
{
    switch (syy) {
    case 2:  return "laiton käsky";
    case 4:  return "kohdistamaton luku";
    case 5:  return "lukemisen väylävirhe";
    case 6:  return "kohdistamaton kirjoitus";
    case 7:  return "kirjoituksen väylävirhe";
    case 11: return "ecall";
    default: return "muu";
    }
}

uint32_t poikkeus(uint32_t syy, uint32_t mepc, uint32_t mtval)
{
    tulosta("  -> mcause ");
    tulosta_luku(syy);
    tulosta(" (");
    tulosta(syyn_nimi(syy));
    tulosta("), mtval ");
    tulosta_hex(mtval);
    tulosta("\n");
    return mepc + 4;        /* ohita aiheuttanut käsky ja jatka */
}
/* @loppu poikkeus */

static void koe(const char *kuvaus)
{
    tulosta(kuvaus);
    tulosta("\n");
}

int main(void)
{
    /* @alku kokeet */
    koe("luku osoitteesta, jossa ei ole orjaa (kytkin: DECERR)");
    (void)*(volatile uint32_t *)0x20000000u;

    koe("kirjoitus tyhjään APB-ikkunaan (silta: DECERR)");
    *(volatile uint32_t *)0x1000F000u = 1u;

    koe("tavukirjoitus UARTin rekisteriin (UART: SLVERR)");
    *(volatile uint8_t *)UART_KANTA = 'x';

    koe("kirjoitus vain luettavaan TUNNISTE-rekisteriin (SLVERR)");
    *(volatile uint32_t *)SYSCON_KANTA = 0u;

    koe("kohdistamaton sanaluku");
    uint32_t arvo, osoite = RAM_KANTA + 0x102u;
    __asm__ volatile("lw %0, 0(%1)" : "=r"(arvo) : "r"(osoite));
    (void)arvo;

    koe("laiton käsky");
    __asm__ volatile(".word 0x00000000");

    koe("ympäristökutsu");
    __asm__ volatile("ecall");
    /* @loppu kokeet */

    tulosta("kaikki poikkeukset käsitelty\n");
    return 0;
}
