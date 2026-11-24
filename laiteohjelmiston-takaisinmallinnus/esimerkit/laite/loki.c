/* Mittausloki: rengaspuskuri, joka siirretään kehyksinä:
 *
 *   7E tyyppi pituus data... crc16(hi) crc16(lo) 7E
 *
 * Tarkiste (CRC-16/CCITT) lasketaan tyypistä datan loppuun. Raja- ja
 * ESC-tavut koodataan kehyksen sisällä muodossa 7D (tavu ^ 0x20). */
#include "loki.h"
#include "konsoli.h"
#include "tarkiste.h"

typedef struct {
    uint32_t aika_ms;
    int16_t lampo;   /* sadasosa-asteina */
    uint8_t tila;
    uint8_t varattu;
} tietue_t;

#define LOKIN_KOKO 32u

static tietue_t loki[LOKIN_KOKO];
static unsigned kirjoitettu;

void loki_kirjaa(uint32_t aika_ms, int16_t lampo, uint8_t tila) {
    loki[kirjoitettu % LOKIN_KOKO] = (tietue_t){aika_ms, lampo, tila, 0};
    kirjoitettu++;
}

void loki_nollaa(void) {
    kirjoitettu = 0;
}

unsigned loki_maara(void) {
    return kirjoitettu < LOKIN_KOKO ? kirjoitettu : LOKIN_KOKO;
}

static void laheta_tavu(uint8_t tavu) {
    if (tavu == KEHYS_RAJA || tavu == KEHYS_ESC) {
        konsoli_merkki((char)KEHYS_ESC);
        tavu ^= 0x20u;
    }
    konsoli_merkki((char)tavu);
}

void laheta_kehys(uint8_t tyyppi, const uint8_t *data, size_t pituus) {
    uint8_t sisalto[2 + 16];
    sisalto[0] = tyyppi;
    sisalto[1] = (uint8_t)pituus;
    for (size_t i = 0; i < pituus && i < 16; i++) {
        sisalto[2 + i] = data[i];
    }
    uint16_t crc = crc16_ccitt(sisalto, 2 + pituus);
    konsoli_merkki((char)KEHYS_RAJA);
    for (size_t i = 0; i < 2 + pituus; i++) {
        laheta_tavu(sisalto[i]);
    }
    laheta_tavu((uint8_t)(crc >> 8));
    laheta_tavu((uint8_t)crc);
    konsoli_merkki((char)KEHYS_RAJA);
}

void loki_siirra(void) {
    unsigned maara = loki_maara();
    unsigned alku = kirjoitettu - maara;
    for (unsigned i = 0; i < maara; i++) {
        const tietue_t *t = &loki[(alku + i) % LOKIN_KOKO];
        uint8_t data[7] = {
            (uint8_t)t->aika_ms, (uint8_t)(t->aika_ms >> 8),
            (uint8_t)(t->aika_ms >> 16), (uint8_t)(t->aika_ms >> 24),
            (uint8_t)t->lampo, (uint8_t)((uint16_t)t->lampo >> 8),
            t->tila,
        };
        laheta_kehys(KEHYS_TIETUE, data, sizeof data);
    }
    uint8_t loppu[2] = {(uint8_t)maara, (uint8_t)(maara >> 8)};
    laheta_kehys(KEHYS_LOPPU, loppu, sizeof loppu);
    konsoli_merkki('\n');
}
