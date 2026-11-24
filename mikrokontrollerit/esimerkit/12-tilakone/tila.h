/* Laitteesta riippumaton logiikka: painikkeen värähtelysuodin ja
 * valon tilakone. Ei rekistereitä eikä keskeytyksiä, joten sama koodi
 * käännetään sekä Cortex-M3:lle että isäntäkoneen testeihin. */
#ifndef TILA_H
#define TILA_H

#include <stdint.h>

// @alku suodin
/* Raakanäyte otetaan 10 ms välein; tila hyväksytään, kun kolme
 * peräkkäistä näytettä ovat samat (30 ms). */
#define SUOTIMEN_NAYTTEET 3

typedef struct {
    uint8_t vakaa;      /* hyväksytty tila */
    uint8_t ehdokas;    /* viimeisin raakanäyte */
    uint8_t sama;       /* montako kertaa ehdokas on toistunut */
} suodin_t;

/* Palauttaa 1, kun hyväksytty tila vaihtui. */
int suodin_nayte(suodin_t *s, int raaka);
// @loppu suodin

// @alku valo
typedef enum { T_TIKKI, T_PAINETTU, T_VAPAUTETTU } tapahtuma_t;
typedef enum { POIS, PAALLA, VILKKU } valotila_t;

#define PITKA_PAINALLUS_MS 1000u
#define VILKKUJAKSO_MS 250u

typedef struct {
    valotila_t tila;
    int led;
    int pohjassa;
    int pitka_kasitelty;
    uint32_t painettu;        /* painalluksen alkuhetki, ms */
    uint32_t vaihdettu;       /* edellinen vilkkumuutos, ms */
} valo_t;

void valo_alusta(valo_t *v);
/* Käsittelee tapahtuman hetkellä nyt (ms). Palauttaa 1, jos tila
 * vaihtui. */
int valo_kasittele(valo_t *v, tapahtuma_t t, uint32_t nyt);
const char *valo_nimi(valotila_t tila);
// @loppu valo

#endif
