// huffman.h: Huffman-koodin rakentaminen tavujen frekvensseistä.
#ifndef HUFFMAN_H
#define HUFFMAN_H

#include <stdint.h>

enum { MERKKEJA = 256 };

typedef struct {
    uint64_t bitit;     // koodi, ensimmäinen bitti eniten merkitsevänä
    int pituus;         // 0, jos merkkiä ei esiinny
} Koodi;

typedef struct {
    int vasen, oikea;   // lapsien indeksit tai -1 lehdessä
    int merkki;         // lehden merkki
} Solmu;

typedef struct {
    Solmu solmut[2 * MERKKEJA];
    int juuri;          // -1, jos syöte on tyhjä
    Koodi koodi[MERKKEJA];
} Puu;

// Rakentaa puun ja koodit. Saman painon solmuista valitaan ensin se,
// jonka pienin merkki on pienin, joten tulos on deterministinen.
void huffman_rakenna(Puu *p, const long frekvenssi[MERKKEJA]);

#endif
