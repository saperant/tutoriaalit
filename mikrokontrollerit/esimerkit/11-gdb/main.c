/* Debugattava ohjelma: keskiarvossa on virhe, joka etsitään gdb:llä
 * (ks. istunto.gdb). Käännetään -Og-lipulla: optimoitu mutta
 * debuggaukseen sopiva. */
#include <stdint.h>

#include "konsoli.h"

/* Globaaleja, jotta ne näkyvät gdb:lle muistissa eivätkä katoa
 * optimoinnissa vakioiksi. */
uint16_t raja = 5000;
uint16_t naytteet[8] = {100, 102, 98, 101, 99, 100, 103, 97};
uint32_t viimeisin;

// @alku keskiarvo
static uint32_t keskiarvo(const uint16_t *taulukko, unsigned n) {
    uint32_t summa = 0;
    for (unsigned i = 0; i <= n; i++) {   /* VIRHE: pitäisi olla < */
        summa += taulukko[i];
    }
    return summa / n;
}
// @loppu keskiarvo

int main(void) {
    konsoli_alusta();
    uint32_t tulos = keskiarvo(naytteet, 8);
    viimeisin = tulos;
    tulosta("keskiarvo %u, raja %u\n", (unsigned)tulos, (unsigned)raja);
    return tulos < raja ? 0 : 1;
}
