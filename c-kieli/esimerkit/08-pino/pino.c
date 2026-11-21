// pino.c: pinon toteutus.
#include "pino.h"

#include <stdlib.h>

struct pino {
    int *alkiot;
    size_t koko;
    size_t kapasiteetti;
};

// static: näkyy vain tässä tiedostossa.
static bool kasvata(Pino *p)
{
    size_t uusi = p->kapasiteetti == 0 ? 8 : 2 * p->kapasiteetti;
    int *alkiot = realloc(p->alkiot, uusi * sizeof *alkiot);
    if (alkiot == nullptr) {
        return false;
    }
    p->alkiot = alkiot;
    p->kapasiteetti = uusi;
    return true;
}

Pino *pino_luo(void)
{
    return calloc(1, sizeof(Pino));
}

void pino_tuhoa(Pino *p)
{
    if (p != nullptr) {
        free(p->alkiot);
        free(p);
    }
}

bool pino_lisaa(Pino *p, int arvo)
{
    if (p->koko == p->kapasiteetti && !kasvata(p)) {
        return false;
    }
    p->alkiot[p->koko++] = arvo;
    return true;
}

bool pino_ota(Pino *p, int *arvo)
{
    if (p->koko == 0) {
        return false;
    }
    *arvo = p->alkiot[--p->koko];
    return true;
}

size_t pino_koko(const Pino *p)
{
    return p->koko;
}
