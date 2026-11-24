#include "raportti.h"

#include <stdlib.h>
#include <string.h>

#include "kello.h"
#include "tilasto.h"

int kirjoita_raportti(FILE *ulos, const double *x, size_t n)
{
    // Mediaani lajittelee, joten se lasketaan kopiosta.
    double *kopio = malloc(n * sizeof *kopio);
    if (kopio == NULL)
        return -1;
    memcpy(kopio, x, n * sizeof *kopio);

    char aika[32];
    time_t nyt = kello_nyt();
    strftime(aika, sizeof aika, "%Y-%m-%d %H:%M", gmtime(&nyt));
    fprintf(ulos, "raportti %s UTC: n=%zu ka=%.2f md=%.2f\n", aika, n,
            keskiarvo(x, n), mediaani(kopio, n));
    free(kopio);
    return 0;
}
