#include "loki.h"

#include <stdio.h>

// @alku loki
static unsigned rivinro;              // paikallinen: ei näy muille

__attribute__((noipa))   // ei upoteta eikä erikoisteta
static void muotoile(char *ulos, size_t koko, const char *viesti)
{
    snprintf(ulos, koko, "[%03u] %s", ++rivinro, viesti);
}

// Heikko oletustoteutus: linkkeri käyttää vahvaa määrittelyä, jos
// jokin muu objektitiedosto antaa sellaisen.
__attribute__((weak)) void loki_kohde(const char *rivi)
{
    printf("oletus: %s\n", rivi);
}

void loki(const char *viesti)
{
    char rivi[128];
    muotoile(rivi, sizeof rivi, viesti);
    loki_kohde(rivi);
}
// @loppu loki
