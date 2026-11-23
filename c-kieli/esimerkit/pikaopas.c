// Pikaoppaan koodinpätkät. Jokainen osa käännetään ja ajetaan.
#include <errno.h>
#include <inttypes.h>
#include <stdckdint.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define PITUUS(t) (sizeof(t) / sizeof((t)[0]))

// @alku virhekoodi
typedef enum { OK, VIRHE_SYOTE, VIRHE_MUISTI } Tulos;

// Tulosparametri + virhekoodi: paluuarvo kertoo onnistumisen.
Tulos jasenna_ika(const char *s, int *ika)
{
    char *loppu;
    errno = 0;
    long arvo = strtol(s, &loppu, 10);
    if (loppu == s || *loppu != '\0' || errno == ERANGE ||
        arvo < 0 || arvo > 150) {
        return VIRHE_SYOTE;
    }
    *ika = (int)arvo;
    return OK;
}
// @loppu virhekoodi

// @alku siivous
Tulos kopioi_isoksi(const char *lahde, char **tulos)
{
    Tulos t = OK;
    char *puskuri = malloc(strlen(lahde) + 1);
    if (puskuri == nullptr) {
        t = VIRHE_MUISTI;
        goto siivous;
    }
    for (size_t i = 0; (puskuri[i] = lahde[i]) != '\0'; ++i) {
        if (puskuri[i] >= 'a' && puskuri[i] <= 'z') {
            puskuri[i] -= 'a' - 'A';
        }
    }
    *tulos = puskuri;
    puskuri = nullptr;   // omistus siirtyi kutsujalle
siivous:
    free(puskuri);
    return t;
}
// @loppu siivous

int main(void)
{
    // @alku tyypit
    int32_t a = -5;
    uint64_t b = 18'000'000'000u;
    size_t n = sizeof a;
    printf("%" PRId32 " %" PRIu64 " %zu %.2f %s %c %x %5d|%-5d|\n", a, b,
           n, 3.14159, "teksti", 'x', 255u, 42, 42);
    // @loppu tyypit

    // @alku taulukot
    int t[] = {3, 1, 4, 1, 5};
    int *p = t;              // taulukko muuntuu osoittimeksi
    int *loppu = t + PITUUS(t);
    int summa = 0;
    for (; p != loppu; ++p) {
        summa += *p;
    }
    printf("alkioita %zu, summa %d, t[2] = %d\n", PITUUS(t), summa, t[2]);
    // @loppu taulukot

    // @alku merkkijonot
    const char *lahteet[] = {"Ritchie", "Kernighan"};
    for (size_t i = 0; i < PITUUS(lahteet); ++i) {
        char nimi[8];
        int tarve = snprintf(nimi, sizeof nimi, "%s", lahteet[i]);
        bool katkesi = tarve < 0 || (size_t)tarve >= sizeof nimi;
        printf("'%s' katkesi=%d\n", nimi, katkesi);
    }
    // @loppu merkkijonot

    // @alku muisti
    size_t koko = 4;
    double *arvot = calloc(koko, sizeof *arvot);   // nollattu
    if (arvot == nullptr) {
        return EXIT_FAILURE;
    }
    double *uusi = realloc(arvot, 2 * koko * sizeof *uusi);
    if (uusi == nullptr) {
        free(arvot);   // vanha alue on yhä voimassa
        return EXIT_FAILURE;
    }
    arvot = uusi;
    free(arvot);
    arvot = nullptr;
    // @loppu muisti

    // @alku virheet
    int ika;
    printf("ikä: %d\n", jasenna_ika("42", &ika) == OK ? ika : -1);
    printf("virhe: %d\n", jasenna_ika("4x2", &ika));

    char *iso = nullptr;
    if (kopioi_isoksi("abc", &iso) == OK) {
        printf("%s\n", iso);
        free(iso);
    }

    int tulo;
    if (ckd_mul(&tulo, 100'000, 100'000)) {
        printf("ylivuoto havaittiin\n");
    }
    // @loppu virheet
}
