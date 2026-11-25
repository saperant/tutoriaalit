// SIMD-versio tarkistetaan skalaariversiota vastaan kaikilla
// pituuksilla 0–300 ja kaikilla alkukohdilla 0–15, jotta myös
// tasaamattomat osoitteet ja silmukan loppuosat tulevat testatuiksi.
#include <stdio.h>

#include "laske.h"

int main(void) {
    static uint8_t puskuri[320];
    uint32_t s = 12345; // kiinteä siemen: sama data joka kerta
    for (size_t i = 0; i < sizeof puskuri; i++) {
        s = s * 1103515245u + 12345u;
        puskuri[i] = (uint8_t)(s >> 16) % 4; // tavuja 0–3
    }
    // @alku vertailu
    int tapauksia = 0, eroja = 0;
    for (size_t alku = 0; alku < 16; alku++) {
        for (size_t n = 0; n <= 300; n++) {
            for (uint8_t c = 0; c < 4; c++) {
                size_t a = laske_skalaari(puskuri + alku, n, c);
                size_t b = laske_simd(puskuri + alku, n, c);
                tapauksia++;
                eroja += a != b;
            }
        }
    }
    printf("%d tapausta, eroja %d\n", tapauksia, eroja);
    // @loppu vertailu
    printf("nollia 300 tavussa: %zu\n", laske_simd(puskuri, 300, 0));
    return eroja != 0;
}
