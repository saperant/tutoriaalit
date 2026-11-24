// tilasto: lukee mittausarvot syötteestä (yksi rivillä) ja tulostaa
// tunnusluvut. Virheellinen rivi on virhe, ei hiljaa ohitettava.
#include "tilasto.h"

#include <errno.h>
#include <stdio.h>
#include <stdlib.h>

#define MAKSIMI 10000

int main(void)
{
    static double arvot[MAKSIMI];
    size_t n = 0;
    char rivi[128];
    for (long nro = 1; fgets(rivi, sizeof rivi, stdin); nro++) {
        char *loppu;
        errno = 0;
        double arvo = strtod(rivi, &loppu);
        if (loppu == rivi || errno != 0 || n == MAKSIMI) {
            fprintf(stderr, "tilasto: rivi %ld ei kelpaa\n", nro);
            return 1;
        }
        arvot[n++] = arvo;
    }
    if (n == 0) {
        fprintf(stderr, "tilasto: ei arvoja\n");
        return 1;
    }
    printf("n            %zu\n", n);
    printf("keskiarvo    %.3f\n", keskiarvo(arvot, n));
    printf("keskihajonta %.3f\n", keskihajonta(arvot, n));
    printf("mediaani     %.3f\n", mediaani(arvot, n));
    return 0;
}
