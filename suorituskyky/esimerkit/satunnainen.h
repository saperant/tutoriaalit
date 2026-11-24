// satunnainen.h: pieni toistettava satunnaislukugeneraattori.
//
// SplitMix64 (Steele, Lea ja Flood 2014). Sama siemen antaa saman sarjan
// joka koneella, joten testien tulosteet ovat toistettavia.
#ifndef SATUNNAINEN_H
#define SATUNNAINEN_H

#include <stdint.h>

typedef struct {
    uint64_t tila;
} Satunnainen;

static inline uint64_t satunnainen_seuraava(Satunnainen *s)
{
    uint64_t z = (s->tila += 0x9E3779B97F4A7C15u);
    z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9u;
    z = (z ^ (z >> 27)) * 0x94D049BB133111EBu;
    return z ^ (z >> 31);
}

// Tasajakautunut luku väliltä [0, raja); pieni vinouma ei haittaa.
static inline uint32_t satunnainen_alle(Satunnainen *s, uint32_t raja)
{
    return (uint32_t)(satunnainen_seuraava(s) % raja);
}

#endif
