#include <stdio.h>
#include <string.h>

#include "komento.h"

// @alku rajat
extern const struct komento __start_komennot[], __stop_komennot[];

static const struct komento *etsi(const char *nimi)
{
    for (const struct komento *k = __start_komennot; k < __stop_komennot;
         ++k)
        if (strcmp(k->nimi, nimi) == 0)
            return k;
    return NULL;
}
// @loppu rajat

int main(int argc, char **argv)
{
    if (argc < 2) {
        printf("komennot (%d):",
               (int)(__stop_komennot - __start_komennot));
        for (const struct komento *k = __start_komennot;
             k < __stop_komennot; ++k)
            printf(" %s", k->nimi);
        printf("\n");
        return 0;
    }
    const struct komento *k = etsi(argv[1]);
    if (!k) {
        fprintf(stderr, "tuntematon komento: %s\n", argv[1]);
        return 2;
    }
    return k->aja();
}
