/* LT-100-lämpötilaloggerin sovellus: komentotulkki sarjakonsolissa. */
#include "asetukset.h"
#include "komennot.h"
#include "konsoli.h"

int main(void) {
    char rivi[192];
    konsoli_alusta();
    if (!asetukset_kelpaa()) {
        konsoli_kirjoita("asetukset puuttuvat, oletukset kaytossa\n");
    }
    for (;;) {
        konsoli_kirjoita("> ");
        konsoli_lue_rivi(rivi, sizeof rivi);
        if (suorita_rivi(rivi) == LOPETA) {
            return 0;
        }
    }
}
