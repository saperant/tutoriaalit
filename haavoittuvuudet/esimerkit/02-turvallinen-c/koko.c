/* Taulukon koon laskenta: naiivi kertolasku ja tarkistettu versio.
 * Käyttö: koko N  (alkioiden määrä) */
#include <errno.h>
#include <inttypes.h>
#include <stdckdint.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

struct mittaus {
    double arvo;
    uint32_t anturi;
    uint32_t aikaleima;
};

// @alku koko
/* Naiivi: kertolasku voi kiertää ympäri, jolloin varaus jää pieneksi. */
static size_t koko_naiivi(size_t n)
{
    return n * sizeof(struct mittaus);
}

/* Tarkistettu: C23:n ckd_mul ilmoittaa ylivuodosta. */
static bool koko_tarkistettu(size_t n, size_t *koko)
{
    return !ckd_mul(koko, n, sizeof(struct mittaus));
}
// @loppu koko

// @alku luku
/* Lukee etumerkittömän luvun: koko merkkijonon on oltava numeroita ja
 * arvon mahduttava tyyppiin. atoi ei tarkistaisi kumpaakaan. */
static bool lue_maara(const char *teksti, size_t *maara)
{
    char *loppu = NULL;
    errno = 0;
    uintmax_t arvo = strtoumax(teksti, &loppu, 10);
    if (errno != 0 || loppu == teksti || *loppu != '\0'
        || teksti[0] == '-' || arvo > SIZE_MAX) {
        return false;
    }
    *maara = (size_t)arvo;
    return true;
}
// @loppu luku

int main(int argc, char *argv[])
{
    size_t n = 0;
    if (argc != 2 || !lue_maara(argv[1], &n)) {
        fprintf(stderr, "käyttö: koko N\n");
        return 2;
    }
    size_t koko = 0;
    printf("n = %zu\n", n);
    printf("  naiivi:      %zu tavua\n", koko_naiivi(n));
    if (koko_tarkistettu(n, &koko)) {
        printf("  tarkistettu: %zu tavua\n", koko);
    } else {
        printf("  tarkistettu: ylivuoto, varaus hylätään\n");
    }
    return 0;
}
