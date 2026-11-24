// Askelpituus: kuinka monta välimuistiriviä silmukka koskettaa.
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>

#include "mittari.h"

// @alku paivita
// Kertoo joka askel:nnen alkion kolmella. Työ (kertolaskuja) vähenee
// askeleen kasvaessa, mutta koskettu muisti vähenee vasta, kun askel on
// suurempi kuin välimuistirivi (64 tavua = 16 int-lukua).
[[gnu::noinline]] static void paivita(int *a, size_t n, size_t askel)
{
    for (size_t i = 0; i < n; i += askel) {
        a[i] *= 3;
    }
}
// @loppu paivita

enum { N = 64 << 20 };      // 64 Mi alkiota = 256 MiB

typedef struct {
    int *a;
    size_t askel;
} Tila;

static void aja(void *p)
{
    Tila *t = p;
    paivita(t->a, N, t->askel);
    kayta(t->a);
}

int main(int argc, char **argv)
{
    if (mittaustila(argc, argv)) {
        int *a = calloc(N, sizeof *a);
        if (a == NULL) {
            return EXIT_FAILURE;
        }
        printf("joka k:nnen alkion paivitys, 256 MiB taulukko\n");
        printf("   k  ms/kierros  ns/paivitys\n");
        for (size_t k = 1; k <= 1024; k *= 2) {
            Tila t = {a, k};
            Tilasto s = mittaa(aja, &t, 5);
            printf("%4zu  %10.2f  %11.2f\n", k, s.mediaani,
                   s.mediaani * 1e6 / (double)(N / k));
        }
        free(a);
        return 0;
    }
    // Toiminnallinen testi: oikeat alkiot muuttuvat.
    int a[64];
    for (int i = 0; i < 64; i++) {
        a[i] = 1;
    }
    paivita(a, 64, 16);
    paivita(a, 64, 32);
    int summa = 0;
    for (int i = 0; i < 64; i++) {
        summa += a[i];
    }
    printf("a[0]=%d a[16]=%d a[32]=%d a[1]=%d summa=%d\n", a[0], a[16],
           a[32], a[1], summa);
    return 0;
}
