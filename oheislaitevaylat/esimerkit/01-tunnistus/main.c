/* Laboratorion tarkistus: luetaan oheislaitteiden tunnisterekisterit.
 *
 * ARM:n oheislaitteiden osoitealueen lopussa (0xFE0..0xFFC) on
 * tunnistelohko: osanumero, valmistaja ja versio. Ajuri voi lukea
 * sen ennen kuin koskee muihin rekistereihin ja kieltäytyä, jos
 * osoitteessa on väärä laite. */
#include <stdint.h>

#include "konsoli.h"
#include "mps2.h"

// @alku tunniste
typedef struct {
    unsigned osa;        /* osanumero, 12 bittiä */
    unsigned valmistaja; /* JEP106-tunnus, 7 bittiä */
    unsigned versio;
} tunniste_t;

static uint32_t sana(uintptr_t perusosoite, unsigned siirtyma) {
    return *(volatile const uint32_t *)(perusosoite + siirtyma) & 0xFFu;
}

static tunniste_t lue_tunniste(uintptr_t perusosoite) {
    uint32_t id0 = sana(perusosoite, 0xFE0);
    uint32_t id1 = sana(perusosoite, 0xFE4);
    uint32_t id2 = sana(perusosoite, 0xFE8);
    return (tunniste_t){
        .osa = id0 | (id1 & 0xFu) << 8,
        .valmistaja = id1 >> 4 | (id2 & 0x7u) << 4,
        .versio = id2 >> 4,
    };
}
// @loppu tunniste

// @alku main
typedef struct {
    const char *nimi;
    uintptr_t osoite;
    unsigned odotettu_osa;
} laite_t;

static const laite_t laitteet[] = {
    {"UART0 (konsoli)", 0x40004000u, 0x821},
    {"UART1 (kehykset)", 0x40005000u, 0x821},
    {"SPI (A/D-muunnin)", (uintptr_t)SPI_ADC, 0x022},
};

int main(void) {
    konsoli_alusta();
    int virheita = 0;
    for (unsigned i = 0; i < sizeof laitteet / sizeof laitteet[0]; i++) {
        const laite_t *l = &laitteet[i];
        tunniste_t t = lue_tunniste(l->osoite);
        int oikea = t.osa == l->odotettu_osa;
        tulosta("%08x %s: osa %03x valmistaja %02x versio %u %s\n",
                (unsigned)l->osoite, l->nimi, t.osa, t.valmistaja,
                t.versio, oikea ? "ok" : "VAARA LAITE");
        virheita += !oikea;
    }
    return virheita;
}
// @loppu main
