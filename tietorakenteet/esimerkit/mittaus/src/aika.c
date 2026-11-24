// Ajoitusmittaus optimoidulla käännöksellä: sama summa taulukosta ja
// satunnaisessa järjestyksessä linkitetystä listasta. Tulostetaan vain
// vertailun tulos väljällä rajalla, jotta mittaus ei ole herkkä
// koneen kuormalle.
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#include "../../satunnainen.h"

enum { N = 1 << 21, TOISTOJA = 5 };

typedef struct solmu {
    long arvo;
    struct solmu *seuraava;
} Solmu;

static double sekunnit(void)
{
    struct timespec t;
    timespec_get(&t, TIME_UTC);
    return (double)t.tv_sec + (double)t.tv_nsec * 1e-9;
}

// @alku mittaus
int main(void)
{
    long *taulukko = malloc(N * sizeof *taulukko);
    Solmu *solmut = malloc(N * sizeof *solmut);
    uint32_t *jarjestys = malloc(N * sizeof *jarjestys);
    if (taulukko == nullptr || solmut == nullptr || jarjestys == nullptr) {
        return EXIT_FAILURE;
    }
    Satunnainen s = {1};
    for (uint32_t i = 0; i < N; i++) {
        jarjestys[i] = i;
    }
    for (uint32_t i = N - 1; i > 0; i--) {
        uint32_t j = satunnainen_alle(&s, i + 1), apu = jarjestys[i];
        jarjestys[i] = jarjestys[j];
        jarjestys[j] = apu;
    }
    for (uint32_t i = 0; i < N; i++) {
        taulukko[i] = i;
        solmut[jarjestys[i]] = (Solmu){
            i, i + 1 < N ? &solmut[jarjestys[i + 1]] : nullptr};
    }
    double paras_t = 1e9, paras_l = 1e9;
    long summa_t = 0, summa_l = 0;
    for (int k = 0; k < TOISTOJA; k++) {       // paras viidestä
        double alku = sekunnit();
        summa_t = 0;
        for (uint32_t i = 0; i < N; i++) {
            summa_t += taulukko[i];
        }
        double keski = sekunnit();
        summa_l = 0;
        for (const Solmu *p = &solmut[jarjestys[0]]; p; p = p->seuraava) {
            summa_l += p->arvo;
        }
        double loppu = sekunnit();
        paras_t = keski - alku < paras_t ? keski - alku : paras_t;
        paras_l = loppu - keski < paras_l ? loppu - keski : paras_l;
    }
    printf("summat samat: %s\n", summa_t == summa_l ? "kyllä" : "EI");
    printf("lista vähintään 3 kertaa hitaampi kuin taulukko: %s\n",
           paras_l > 3 * paras_t ? "kyllä" : "ei");
    fprintf(stderr, "taulukko %.2f ms, lista %.2f ms (%.0f-kertainen)\n",
            paras_t * 1e3, paras_l * 1e3, paras_l / paras_t);
    free(taulukko);
    free(solmut);
    free(jarjestys);
    return EXIT_SUCCESS;
}
// @loppu mittaus
