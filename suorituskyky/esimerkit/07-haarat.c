// Haarautumisen ennustus: lajiteltu ja lajittelematon data.
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>

#include "mittari.h"
#include "satunnainen.h"

// @alku haarautuva
// Laskee vähintään 128:n suuruisten tavujen summan haaralla.
[[gnu::noinline]] static long summa_haarautuva(const unsigned char *a,
                                               size_t n)
{
    long s = 0;
    for (size_t i = 0; i < n; i++) {
        if (a[i] >= 128) {
            s += a[i];
        }
    }
    return s;
}
// @loppu haarautuva

// @alku haaraton
// Sama ilman haaraa: vertailun tulos 0 tai 1 muutetaan maskiksi
// 0 tai -1 (kaikki bitit), jolla arvo joko säilyy tai nollautuu.
[[gnu::noinline]] static long summa_haaraton(const unsigned char *a,
                                             size_t n)
{
    long s = 0;
    for (size_t i = 0; i < n; i++) {
        long maski = -(long)(a[i] >= 128);
        s += a[i] & maski;
    }
    return s;
}
// @loppu haaraton

// Tavujen lajittelu laskemalla (ks. Algoritmit, luku 5).
static void lajittele(const unsigned char *a, unsigned char *tulos,
                      size_t n)
{
    size_t maarat[256] = {0};
    for (size_t i = 0; i < n; i++) {
        maarat[a[i]]++;
    }
    for (size_t arvo = 0, k = 0; arvo < 256; arvo++) {
        memset(tulos + k, (int)arvo, maarat[arvo]);
        k += maarat[arvo];
    }
}

typedef struct {
    const unsigned char *a;
    size_t n;
    long tulos;
    long (*summa)(const unsigned char *, size_t);
} Tila;

static void aja(void *p)
{
    Tila *t = p;
    t->tulos = t->summa(t->a, t->n);
    kayta(&t->tulos);
}

int main(int argc, char **argv)
{
    size_t n = mittaustila(argc, argv) ? 1u << 24 : 100000;
    // --kerran N sekaisin|lajiteltu: yksi summa (Cachegrindia varten)
    bool kerran = argc == 4 && strcmp(argv[1], "--kerran") == 0;
    if (kerran) {
        n = strtoul(argv[2], NULL, 10);
    }
    unsigned char *sekainen = malloc(n), *lajiteltu = malloc(n);
    if (sekainen == NULL || lajiteltu == NULL) {
        return EXIT_FAILURE;
    }
    Satunnainen r = {3};
    for (size_t i = 0; i < n; i++) {
        sekainen[i] = (unsigned char)satunnainen_alle(&r, 256);
    }
    lajittele(sekainen, lajiteltu, n);

    if (kerran) {
        bool sekaisin = strcmp(argv[3], "sekaisin") == 0;
        printf("%ld\n", summa_haarautuva(sekaisin ? sekainen : lajiteltu,
                                         n));
    } else if (mittaustila(argc, argv)) {
        Tila t[] = {{sekainen, n, 0, summa_haarautuva},
                    {lajiteltu, n, 0, summa_haarautuva},
                    {sekainen, n, 0, summa_haaraton},
                    {lajiteltu, n, 0, summa_haaraton}};
        const char *nimet[] = {"haara, sekaisin", "haara, lajiteltu",
                               "haaraton, sekaisin", "haaraton, lajiteltu"};
        printf("ehdollinen summa, %zu tavua\n", n);
        double vertailu = 0;
        for (int i = 0; i < 4; i++) {
            Tilasto s = mittaa(aja, &t[i], 11);
            tulosta_mittaus(nimet[i], s, vertailu);
            vertailu = i == 0 ? s.mediaani : vertailu;
        }
    } else {
        long s1 = summa_haarautuva(sekainen, n);
        long s2 = summa_haarautuva(lajiteltu, n);
        long s3 = summa_haaraton(sekainen, n);
        printf("summat %ld %ld %ld\n", s1, s2, s3);
        printf("samat: %s\n", s1 == s2 && s2 == s3 ? "kylla" : "ei");
    }
    free(sekainen);
    free(lajiteltu);
    return 0;
}
