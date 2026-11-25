#include "puskuri.h"

void puskuri_alusta(struct puskuri *p)
{
    p->alku = 0;
    p->maara = 0;
}

bool puskuri_lisaa(struct puskuri *p, float arvo)
{
    if (p->maara < PUSKURI_KOKO) {
        p->arvot[(p->alku + p->maara) % PUSKURI_KOKO] = arvo;
        p->maara++;
        return false;
    }
    p->arvot[p->alku] = arvo;
    p->alku = (p->alku + 1) % PUSKURI_KOKO;
    return true;
}

bool puskuri_keskiarvo(const struct puskuri *p, float *keskiarvo)
{
    if (p->maara == 0) {
        return false;
    }
    float summa = 0.0f;
    for (size_t i = 0; i < p->maara; i++) {
        summa += p->arvot[(p->alku + i) % PUSKURI_KOKO];
    }
    *keskiarvo = summa / (float)p->maara;
    return true;
}
