/* Käynnistyskoodin työ näkyviin: .data, .bss ja .noinit
 * ohjelmallisen resetin yli. Sama ohjelma käännetään myös ilman
 * alustusta (ILMAN_ALUSTUSTA), jolloin ero näkyy tulosteessa. */
#include <stdint.h>

#include "konsoli.h"
#include "mps2.h"

extern uint32_t _data_alku[], _data_loppu[], _data_lataus[];
extern uint32_t _bss_alku[], _bss_loppu[];
extern uint32_t _pinon_pohja[], _pinon_huippu[];

// @alku muuttujat
static uint32_t alustettu = 42;     /* .data: arvo flashista RAMiin */
static uint32_t nollattu;           /* .bss: nollataan */
static const uint32_t vakio = 7;    /* .rodata: jää flashiin */

/* .noinit: käynnistyskoodi ei koske, joten arvo säilyy resetin yli. */
#define TAIKA 0x4B414E54u
__attribute__((section(".noinit"))) static uint32_t taika;
__attribute__((section(".noinit"))) static uint32_t kaynnistyksia;
// @loppu muuttujat

static const char *alue(const volatile void *osoite) {
    return (uint32_t)osoite < 0x20000000u ? "flash" : "RAM";
}

// @alku main
int main(void) {
    konsoli_alusta();
    if (taika != TAIKA) {          /* RAMissa ei vielä ole merkkiä */
        taika = TAIKA;
        kaynnistyksia = 0;
    }
    kaynnistyksia++;
    tulosta("käynnistys %u (%s)\n", (unsigned)kaynnistyksia,
            kaynnistyksia == 1 ? "virrankytkentä" : "ohjelmallinen reset");
    tulosta("  alustettu = %u, nollattu = %u, vakio = %u\n",
            (unsigned)alustettu, (unsigned)nollattu, (unsigned)vakio);
    if (kaynnistyksia > 1) {
        return 0;
    }
    tulosta("  alustettu: %s 0x%08x, alkuarvo: %s, vakio: %s\n",
            alue(&alustettu), (unsigned)&alustettu, alue(_data_lataus),
            alue(&vakio));
    tulosta("  .data %u tavua, .bss %u tavua, pino %u tavua\n",
            (unsigned)((_data_loppu - _data_alku) * 4),
            (unsigned)((_bss_loppu - _bss_alku) * 4),
            (unsigned)((_pinon_huippu - _pinon_pohja) * 4));
    alustettu = 43;
    nollattu = 7;
    tulosta("  muutetaan: alustettu = 43, nollattu = 7; reset\n");
    /* AIRCR hyväksyy kirjoituksen vain avaimen 0x05FA kanssa. */
    SCB->AIRCR = SCB_AIRCR_AVAIMET | SCB_AIRCR_SYSRESETREQ;
    muistiaita();
    for (;;) {
    }
}
// @loppu main
