// Mittausviestin binäärikoodaus: versiotavu ja TLV-kentät (tyyppi,
// pituus, arvo). Kokonaisluvut verkon tavujärjestyksessä (big-endian).
#ifndef TLV_H
#define TLV_H

#include <stddef.h>
#include <stdint.h>
#include <string.h>

// @alku tavut
// Tavujärjestys bitinsiirroilla: toimii samoin jokaisella koneella eikä
// vaadi kohdistettua osoitinta.
static inline void kirjoita_u16(uint8_t *b, uint16_t x) {
    b[0] = (uint8_t)(x >> 8);
    b[1] = (uint8_t)x;
}

static inline uint16_t lue_u16(const uint8_t *b) {
    return (uint16_t)(b[0] << 8 | b[1]);
}

static inline void kirjoita_u32(uint8_t *b, uint32_t x) {
    for (int i = 0; i < 4; i++) {
        b[i] = (uint8_t)(x >> (24 - 8 * i));
    }
}

static inline uint32_t lue_u32(const uint8_t *b) {
    return (uint32_t)b[0] << 24 | (uint32_t)b[1] << 16 |
           (uint32_t)b[2] << 8 | b[3];
}
// @loppu tavut

// @alku malli
enum { VERSIO = 1 };
enum { ANTURI = 1, LAMPOTILA = 2, AIKA = 3 };   // kenttien tyypit

typedef struct {
    char anturi[32];                     // pakollinen, 1-31 merkkiä
    int32_t lampotila;                   // sadasosa-asteina
    uint32_t aika;                       // sekunteja vuoden 1970 alusta
} mittaus;

typedef enum {
    PURKU_OK, PURKU_LYHYT, PURKU_VERSIO, PURKU_PITUUS, PURKU_ARVO,
    PURKU_PUUTTUU, PURKU_TULOKSIA
} purkutulos;

static const char *const PURKUTULOS[] = {
    "ok", "lyhyt", "versio", "pituus", "arvo", "puuttuu"};
// @loppu malli

// @alku koodaa
// Kenttä: tyyppi (1 tavu), pituus (2 tavua) ja arvo.
static inline uint8_t *kentta(uint8_t *b, uint8_t tyyppi,
                              const void *arvo, uint16_t pituus) {
    b[0] = tyyppi;
    kirjoita_u16(b + 1, pituus);
    memcpy(b + 3, arvo, pituus);
    return b + 3 + pituus;
}

// Koodaa mittauksen puskuriin, jonka on oltava vähintään 64 tavua.
// Palauttaa viestin pituuden.
static inline size_t koodaa(const mittaus *m, uint8_t *b) {
    uint8_t luku[4];
    uint8_t *p = b;
    *p++ = VERSIO;
    p = kentta(p, ANTURI, m->anturi, (uint16_t)strlen(m->anturi));
    kirjoita_u32(luku, (uint32_t)m->lampotila);
    p = kentta(p, LAMPOTILA, luku, 4);
    kirjoita_u32(luku, m->aika);
    p = kentta(p, AIKA, luku, 4);
    return (size_t)(p - b);
}
// @loppu koodaa

// @alku pura
// Purkaa viestin. Jokainen pituus tarkistetaan jäljellä olevaa dataa
// vastaan ennen lukemista. Tuntemattomat kentät ohitetaan, jotta uudempi
// lähettäjä voi lisätä kenttiä rikkomatta vanhaa vastaanottajaa.
static inline purkutulos pura(const uint8_t *b, size_t n, mittaus *m) {
    if (n < 1) {
        return PURKU_LYHYT;
    }
    if (b[0] != VERSIO) {
        return PURKU_VERSIO;             // eri pääversio: ei arvata
    }
    *m = (mittaus){};
    bool loytyi[4] = {};
    size_t i = 1;
    while (i < n) {
        if (n - i < 3) {
            return PURKU_LYHYT;          // otsake ei mahdu
        }
        uint8_t tyyppi = b[i];
        size_t pituus = lue_u16(b + i + 1);
        i += 3;
        if (pituus > n - i) {
            return PURKU_PITUUS;         // väittää enemmän kuin on
        }
        const uint8_t *arvo = b + i;
        i += pituus;
        if (tyyppi == ANTURI) {
            if (pituus == 0 || pituus >= sizeof m->anturi ||
                memchr(arvo, '\0', pituus) != nullptr) {
                return PURKU_ARVO;
            }
            memcpy(m->anturi, arvo, pituus);
            m->anturi[pituus] = '\0';
        } else if (tyyppi == LAMPOTILA || tyyppi == AIKA) {
            if (pituus != 4) {
                return PURKU_ARVO;
            }
            uint32_t x = lue_u32(arvo);
            if (tyyppi == AIKA) {
                m->aika = x;
            } else {
                m->lampotila = (int32_t)x;
            }
        } else {
            continue;                    // tuntematon kenttä: ohitetaan
        }
        loytyi[tyyppi] = true;
    }
    if (!loytyi[ANTURI] || !loytyi[LAMPOTILA] || !loytyi[AIKA]) {
        return PURKU_PUUTTUU;
    }
    return PURKU_OK;
}
// @loppu pura

#endif
