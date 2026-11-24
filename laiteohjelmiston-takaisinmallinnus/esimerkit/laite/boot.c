/* LT-100:n käynnistyslatain: tarkistaa sovelluksen otsakkeen ja
 * tarkisteen ja hyppää sovellukseen. */
#include <stdint.h>

#include "konsoli.h"
#include "kuva.h"
#include "mps2.h"
#include "semihost.h"
#include "tarkiste.h"

extern uint32_t _data_alku[], _data_loppu[], _data_lataus[];
extern uint32_t _bss_alku[], _bss_loppu[];
extern uint32_t _pinon_huippu[];

void Reset_Handler(void);
void Vika_Handler(void);

typedef void (*kasittelija_t)(void);

__attribute__((section(".vektorit"), used))
static const kasittelija_t vektorit[16] = {
    (kasittelija_t)_pinon_huippu,
    Reset_Handler,
    Vika_Handler, /* NMI */
    Vika_Handler, /* HardFault */
};

int kuva_kelpaa(const sovellus_otsake_t *otsake) {
    if (otsake->taikaluku != OTSAKE_TAIKALUKU) {
        return KUVA_TAIKALUKU;
    }
    if (otsake->laitetunnus != LAITETUNNUS) {
        return KUVA_LAITE;
    }
    if (otsake->pituus == 0 || otsake->pituus > SOVELLUS_MAKS) {
        return KUVA_PITUUS;
    }
    const void *sovellus = (const void *)SOVELLUS_ALKU;
    if (crc32(sovellus, otsake->pituus) != otsake->crc32) {
        return KUVA_TARKISTE;
    }
#ifdef KORJATTU
    /* Korjattu versio: allekirjoituksettomaan kuvaan ei hypätä.
     * Allekirjoituksen tarkistus: ks. Sulautettujen järjestelmien
     * tietoturva. */
    if (otsake->allekirjoitus == 0) {
        return KUVA_ALLEKIRJOITUS;
    }
#endif
    return KUVA_OK;
}

static void hyppaa(uint32_t osoite) {
    const uint32_t *taulu = (const uint32_t *)osoite;
    SCB_VTOR = osoite;
    __asm__ volatile("msr msp, %0\n\tbx %1"
                     :
                     : "r"(taulu[0]), "r"(taulu[1])
                     : "memory");
}

void Reset_Handler(void) {
    const uint32_t *lahde = _data_lataus;
    for (uint32_t *kohde = _data_alku; kohde < _data_loppu;) {
        *kohde++ = *lahde++;
    }
    for (uint32_t *kohde = _bss_alku; kohde < _bss_loppu;) {
        *kohde++ = 0;
    }
    konsoli_alusta();
    konsoli_kirjoita("LT-100 boot 1.2\n");
    const sovellus_otsake_t *otsake =
        (const sovellus_otsake_t *)SOVELLUS_OTSAKE;
    int tulos = kuva_kelpaa(otsake);
    if (tulos != KUVA_OK) {
        tulosta("boot: sovellus hylatty (%d)\n", tulos);
        lopeta(10 + tulos);
    }
    tulosta("boot: sovellus %u.%u.%u ok\n",
            (unsigned)(otsake->versio >> 16) & 0xFFu,
            (unsigned)(otsake->versio >> 8) & 0xFFu,
            (unsigned)otsake->versio & 0xFFu);
    hyppaa(SOVELLUS_ALKU);
    lopeta(20);
}

void Vika_Handler(void) {
    konsoli_kirjoita("boot: vika\n");
    lopeta(99);
}
