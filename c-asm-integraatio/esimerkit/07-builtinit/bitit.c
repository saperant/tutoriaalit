// Kääntäjän sisäiset funktiot, joille on yksi tai useampi konekäsky
// joillain prosessoreilla. Kääntäjä valitsee toteutuksen kohde-
// arkkitehtuurin mukaan; tarkistus.sh näyttää, minkä.
#include <stdint.h>

#include "bitit.h"

// @alku bitit
int ykkosia(uint64_t x) { return __builtin_popcountll(x); }

// Nollabittien määrä alhaalta. Arvolla 0 tulos on määrittelemätön,
// joten se käsitellään erikseen.
int nollia_lopussa(uint64_t x) { return x ? __builtin_ctzll(x) : 64; }

// Tavujärjestyksen kääntö: big-endian <-> little-endian.
uint64_t kaanna(uint64_t x) { return __builtin_bswap64(x); }
// @loppu bitit

// @alku odotus
// __builtin_expect kertoo, kumpi haara on todennäköinen. Se ei muuta
// tulosta, vain koodin järjestystä: harvinainen haara siirretään pois
// kuumasta polusta.
#define HARVOIN(e) __builtin_expect(!!(e), 0)

int jaa_turvallisesti(int a, int b, int *tulos) {
    if (HARVOIN(b == 0)) {
        return -1;
    }
    *tulos = a / b;
    return 0;
}
// @loppu odotus
