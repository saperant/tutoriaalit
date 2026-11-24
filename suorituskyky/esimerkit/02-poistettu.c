// Kääntäjä poistaa laskennan, jonka tulosta ei käytetä.
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>

#include "mittari.h"

enum { N = 1 << 22 };

typedef struct {
    const int *a;
    long tulos;
} Tila;

static long summa(const int *a, size_t n)
{
    long s = 0;
    for (size_t i = 0; i < n; i++) {
        s += a[i];
    }
    return s;
}

// @alku vaarin
// Väärin: tulos hylätään, joten -O2 poistaa koko silmukan.
static void mittaa_hylaten(void *p)
{
    Tila *t = p;
    long s = summa(t->a, N);
    (void)s;
}
// @loppu vaarin

// @alku oikein
// Oikein: tulos tallennetaan ja kayta() kertoo, että sitä luetaan.
static void mittaa_kayttaen(void *p)
{
    Tila *t = p;
    t->tulos = summa(t->a, N);
    kayta(&t->tulos);
}
// @loppu oikein

int main(int argc, char **argv)
{
    int *a = malloc(N * sizeof *a);
    if (a == NULL) {
        return EXIT_FAILURE;
    }
    for (size_t i = 0; i < N; i++) {
        a[i] = (int)(i & 7);
    }
    Tila t = {a, 0};
    if (mittaustila(argc, argv)) {
        printf("summa 16 MiB taulukosta\n");
        Tilasto oikein = mittaa(mittaa_kayttaen, &t, 21);
        Tilasto hylatty = mittaa(mittaa_hylaten, &t, 21);
        tulosta_mittaus("tulos kaytetaan", oikein, 0);
        tulosta_mittaus("tulos hylataan", hylatty, 0);
    } else {
        mittaa_hylaten(&t);
        mittaa_kayttaen(&t);
        printf("summa %ld\n", t.tulos);
    }
    free(a);
    return 0;
}
