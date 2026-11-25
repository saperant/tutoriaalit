#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// @alku yhdista
// Palauttaa uuden merkkijonon. Kutsuja omistaa sen ja vapauttaa sen
// free-funktiolla. Palauttaa nullptr, jos muisti loppuu.
char *yhdista(const char *a, const char *erotin, const char *b)
{
    size_t pituus = strlen(a) + strlen(erotin) + strlen(b);
    char *tulos = malloc(pituus + 1);   // +1 nollamerkille
    if (tulos == nullptr) {
        return nullptr;
    }
    snprintf(tulos, pituus + 1, "%s%s%s", a, erotin, b);
    return tulos;
}
// @loppu yhdista

int main(void)
{
    // @alku perusteet
    size_t n = 5;
    int *luvut = malloc(n * sizeof *luvut);
    if (luvut == nullptr) {
        fprintf(stderr, "muisti loppui\n");
        return EXIT_FAILURE;
    }
    for (size_t i = 0; i < n; ++i) {
        luvut[i] = (int)(i * i);
    }
    printf("luvut[4] = %d\n", luvut[4]);
    free(luvut);
    luvut = nullptr;   // estää vahingossa tapahtuvan käytön

    double *nollat = calloc(n, sizeof *nollat);   // alustettu nolliksi
    if (nollat == nullptr) {
        return EXIT_FAILURE;
    }
    printf("nollat[3] = %.1f\n", nollat[3]);
    free(nollat);
    // @loppu perusteet

    // @alku omistus
    char *nimi = yhdista("Dennis", " ", "Ritchie");
    if (nimi != nullptr) {
        printf("%s (%zu merkkiä)\n", nimi, strlen(nimi));
        free(nimi);
    }

    char *kopio = strdup("C23 standardoi strdup-funktion");
    if (kopio != nullptr) {
        printf("%s\n", kopio);
        free(kopio);
    }
    // @loppu omistus
}
