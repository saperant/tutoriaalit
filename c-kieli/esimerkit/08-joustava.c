#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// @alku tyyppi
typedef struct {
    size_t pituus;
    char merkit[];   // joustava taulukkojäsen: koko määrätään varattaessa
} Viesti;

Viesti *viesti_luo(const char *teksti)
{
    size_t pituus = strlen(teksti);
    Viesti *v = malloc(sizeof *v + pituus + 1);
    if (v == nullptr) {
        return nullptr;
    }
    v->pituus = pituus;
    memcpy(v->merkit, teksti, pituus + 1);
    return v;
}
// @loppu tyyppi

int main(void)
{
    // @alku kaytto
    Viesti *v = viesti_luo("yksi varaus, yksi vapautus");
    if (v == nullptr) {
        return EXIT_FAILURE;
    }
    printf("%zu: %s\n", v->pituus, v->merkit);
    free(v);
    // @loppu kaytto
}
