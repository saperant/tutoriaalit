/* Rengaspuskuri yhdelle tuottajalle ja yhdelle kuluttajalle, esim.
 * keskeytyskäsittelijä tuottaa ja pääsilmukka kuluttaa. Lukkoja ei
 * tarvita, koska kumpikin osapuoli muuttaa vain omaa indeksiään. */
#ifndef RENGAS_H
#define RENGAS_H

#include <stdatomic.h>
#include <stdint.h>

// @alku rengas
#define RENGAS_KOKO 64u   /* kahden potenssi: % on pelkkä maskaus */

typedef struct {
    uint8_t data[RENGAS_KOKO];
    volatile uint32_t kirjoitus;   /* vain tuottaja muuttaa */
    volatile uint32_t luku;        /* vain kuluttaja muuttaa */
    volatile uint32_t ylivuotoja;
} rengas_t;

/* Indeksit kasvavat vapaasti ja pyörähtävät ympäri; täyttöaste on
 * aina kirjoitus - luku (modulo 2^32). */
static inline int rengas_lisaa(rengas_t *r, uint8_t tavu) {
    if (r->kirjoitus - r->luku == RENGAS_KOKO) {
        r->ylivuotoja++;
        return 0;
    }
    r->data[r->kirjoitus % RENGAS_KOKO] = tavu;
    /* Data ensin, sitten indeksi: kääntäjä ei saa vaihtaa järjestystä. */
    atomic_signal_fence(memory_order_release);
    r->kirjoitus++;
    return 1;
}

static inline int rengas_ota(rengas_t *r, uint8_t *tavu) {
    if (r->kirjoitus == r->luku) {
        return 0;
    }
    atomic_signal_fence(memory_order_acquire);
    *tavu = r->data[r->luku % RENGAS_KOKO];
    atomic_signal_fence(memory_order_release);
    r->luku++;
    return 1;
}
// @loppu rengas

#endif
