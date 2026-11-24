// Automaattinen vektorointi: aliasing, restrict ja liukulukusummat.
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>

#include "mittari.h"

// @alku saxpy
// y = a*x + y. Kääntäjä ei tiedä, osuvatko x ja y päällekkäin, joten se
// joko tarkistaa sen ajon aikana tai jättää silmukan vektoroimatta.
[[gnu::noinline]] static void saxpy(float *y, const float *x, float a,
                                    size_t n)
{
    for (size_t i = 0; i < n; i++) {
        y[i] = a * x[i] + y[i];
    }
}

// restrict lupaa, että taulukot eivät ole päällekkäin.
[[gnu::noinline]] static void saxpy_restrict(float *restrict y,
                                             const float *restrict x,
                                             float a, size_t n)
{
    for (size_t i = 0; i < n; i++) {
        y[i] = a * x[i] + y[i];
    }
}
// @loppu saxpy

// @alku summat
// Kokonaislukujen yhteenlasku on liitännäinen: vektoroituu.
[[gnu::noinline]] static int64_t summa_int(const int32_t *a, size_t n)
{
    int64_t s = 0;
    for (size_t i = 0; i < n; i++) {
        s += a[i];
    }
    return s;
}

// Liukulukujen yhteenlasku ei ole liitännäinen: järjestyksen
// muuttaminen voi muuttaa tulosta, joten kääntäjä ei vektoroi ilman
// lupaa (-ffast-math tai -fassociative-math).
[[gnu::noinline]] static float summa_float(const float *a, size_t n)
{
    float s = 0;
    for (size_t i = 0; i < n; i++) {
        s += a[i];
    }
    return s;
}

// Sama summa kahdeksana osasummana, kuten vektoroitu koodi laskisi.
[[gnu::noinline]] static float summa_float_8(const float *a, size_t n)
{
    float osa[8] = {0};
    size_t i = 0;
    for (; i + 8 <= n; i += 8) {
        for (size_t k = 0; k < 8; k++) {
            osa[k] += a[i + k];
        }
    }
    float s = 0;
    for (size_t k = 0; k < 8; k++) {
        s += osa[k];
    }
    for (; i < n; i++) {
        s += a[i];
    }
    return s;
}
// @loppu summat

typedef struct {
    float *y;
    const float *x;
    size_t n;
    void (*f)(float *, const float *, float, size_t);
} Saxpy;

static void aja_saxpy(void *p)
{
    Saxpy *t = p;
    for (int k = 0; k < 1000; k++) {
        t->f(t->y, t->x, 1.0001f, t->n);
        kayta(t->y);
    }
}

typedef struct {
    const float *a;
    size_t n;
    float tulos;
    float (*f)(const float *, size_t);
} Summa;

static void aja_summa(void *p)
{
    Summa *t = p;
    for (int k = 0; k < 1000; k++) {
        t->tulos = t->f(t->a, t->n);
        kayta(&t->tulos);
    }
}

static void mittaa_kaikki(void)
{
    enum { N = 4096 };          // 16 KiB / taulukko: L1-välimuistissa
    static float x[N], y[N];
    for (size_t i = 0; i < N; i++) {
        x[i] = (float)(i % 100);
    }
    Saxpy s1 = {y, x, N, saxpy}, s2 = {y, x, N, saxpy_restrict};
    printf("saxpy, %d alkiota (aika = 1000 kutsua)\n", N);
    Tilasto t1 = mittaa(aja_saxpy, &s1, 21);
    Tilasto t2 = mittaa(aja_saxpy, &s2, 21);
    tulosta_mittaus("ilman restrict", t1, 0);
    tulosta_mittaus("restrict", t2, t1.mediaani);
    Summa u1 = {x, N, 0, summa_float}, u2 = {x, N, 0, summa_float_8};
    printf("float-summa, %d alkiota (aika = 1000 kutsua)\n", N);
    Tilasto t3 = mittaa(aja_summa, &u1, 21);
    Tilasto t4 = mittaa(aja_summa, &u2, 21);
    tulosta_mittaus("yksi summa", t3, 0);
    tulosta_mittaus("kahdeksan osasummaa", t4, t3.mediaani);
}

int main(int argc, char **argv)
{
    if (mittaustila(argc, argv)) {
        mittaa_kaikki();
        return 0;
    }
    // @alku paallekkain
    // Päällekkäiset taulukot: y alkaa yhden alkion x:n jälkeen. Jokainen
    // kierros lukee edellisen kierroksen tuloksen, joten tulos poikkeaa
    // erillisten taulukoiden tuloksesta. Kääntäjän on säilytettävä tämä.
    float t[9] = {1, 1, 1, 1, 1, 1, 1, 1, 1};
    saxpy(t + 1, t, 1.0f, 8);
    printf("paallekkain:");
    for (int i = 0; i < 9; i++) {
        printf(" %.0f", t[i]);
    }
    printf("\n");
    // @loppu paallekkain

    float x[1000], y[1000], z[1000];
    int32_t k[1000];
    for (int i = 0; i < 1000; i++) {
        x[i] = (float)(i % 10);
        y[i] = z[i] = 1;
        k[i] = i;
    }
    saxpy(y, x, 2.0f, 1000);
    saxpy_restrict(z, x, 2.0f, 1000);
    printf("saxpy samat: %s\n",
           memcmp(y, z, sizeof y) == 0 ? "kylla" : "ei");
    printf("summa_int %lld\n", (long long)summa_int(k, 1000));

    // @alku jarjestys
    float a[1000];
    for (int i = 0; i < 1000; i++) {
        a[i] = 1.0f / (float)(i + 1);       // harmoninen sarja
    }
    printf("float-summa jarjestyksessa  %.9g\n", summa_float(a, 1000));
    printf("float-summa 8 osasummana    %.9g\n", summa_float_8(a, 1000));
    // @loppu jarjestys
    return 0;
}
