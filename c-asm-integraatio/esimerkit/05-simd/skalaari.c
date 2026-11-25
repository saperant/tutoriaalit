#include "laske.h"

// Vertailuversio. noipa estää yhdistämästä sitä kutsujaan.
__attribute__((noipa)) size_t laske_skalaari(const uint8_t *t, size_t n,
                                             uint8_t c) {
    size_t m = 0;
    for (size_t i = 0; i < n; i++) {
        m += t[i] == c;
    }
    return m;
}
