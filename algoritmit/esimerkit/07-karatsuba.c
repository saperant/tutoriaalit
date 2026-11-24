// Karatsuban kertolasku: kaksi n-numeroista lukua kerrotaan kolmella
// n/2-numeroisella kertolaskulla neljän sijaan. Rekursioyhtälö
// T(n) = 3 T(n/2) + O(n) antaa T(n) = O(n^log2(3)) = O(n^1.585).
// Lasketaan numeroiden kertolaskut ja verrataan koulumenetelmään.
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "satunnainen.h"

static long kertolaskuja;

// Yksinkertaistus: muistin loppuminen lopettaa ohjelman.
static long *varaa(int n)
{
    long *p = malloc((size_t)n * sizeof *p);
    if (p == nullptr) {
        fprintf(stderr, "muisti loppui\n");
        exit(EXIT_FAILURE);
    }
    return p;
}

// Luvut ovat numerotaulukoita, vähiten merkitsevä numero ensin.
// Välivaiheissa "numerot" voivat kasvaa yli 9:n tai olla negatiivisia;
// siirtonumerot käsitellään vasta lopuksi.
static void koulu(const long *a, const long *b, int n, long *tulos)
{
    memset(tulos, 0, (size_t)(2 * n) * sizeof *tulos);
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            tulos[i + j] += a[i] * b[j];
            kertolaskuja++;
        }
    }
}

// @alku karatsuba
// a = a1 * 10^m + a0 ja b = b1 * 10^m + b0, missä m = n/2
// (n on kahden potenssi). Silloin
// a * b = z2 * 10^(2m) + z1 * 10^m + z0, missä
//   z0 = a0 * b0,  z2 = a1 * b1,
//   z1 = (a0 + a1)(b0 + b1) - z0 - z2.
static void karatsuba(const long *a, const long *b, int n, long *tulos)
{
    if (n <= 4) {                       // pienet luvut koulumenetelmällä
        koulu(a, b, n, tulos);
        return;
    }
    int m = n / 2;
    long *summa_a = varaa(m), *summa_b = varaa(m), *z1 = varaa(2 * m);
    for (int i = 0; i < m; i++) {
        summa_a[i] = a[i] + a[m + i];
        summa_b[i] = b[i] + b[m + i];
    }
    long *z0 = tulos, *z2 = tulos + 2 * m;    // tulos[0..2m), [2m..4m)
    karatsuba(a, b, m, z0);
    karatsuba(a + m, b + m, m, z2);
    karatsuba(summa_a, summa_b, m, z1);
    for (int i = 0; i < 2 * m; i++) {
        z1[i] -= z0[i] + z2[i];
    }
    for (int i = 0; i < 2 * m; i++) {
        tulos[m + i] += z1[i];
    }
    free(summa_a);
    free(summa_b);
    free(z1);
}
// @loppu karatsuba

// Siirtonumerot: palauttaa tavallisen numeroesityksen paikallaan.
static void normalisoi(long *x, int n)
{
    long siirto = 0;
    for (int i = 0; i < n; i++) {
        long arvo = x[i] + siirto;
        x[i] = arvo % 10;
        siirto = arvo / 10;
    }
}

int main(void)
{
    Satunnainen s = { 21 };
    printf("%6s %10s %10s %7s %s\n",
           "n", "koulu", "karatsuba", "suhde", "sama tulos");
    for (int n = 16; n <= 4096; n *= 4) {
        long *a = varaa(n), *b = varaa(n);
        long *t1 = varaa(2 * n), *t2 = varaa(2 * n);
        for (int i = 0; i < n; i++) {
            a[i] = satunnainen_alle(&s, 10);
            b[i] = satunnainen_alle(&s, 10);
        }
        kertolaskuja = 0;
        koulu(a, b, n, t1);
        long k1 = kertolaskuja;
        kertolaskuja = 0;
        karatsuba(a, b, n, t2);
        long k2 = kertolaskuja;
        normalisoi(t1, 2 * n);
        normalisoi(t2, 2 * n);
        bool sama = memcmp(t1, t2, (size_t)(2 * n) * sizeof *t1) == 0;
        printf("%6d %10ld %10ld %7.2f %s\n", n, k1, k2,
               (double)k1 / (double)k2, sama ? "kyllä" : "ei");
        free(a);
        free(b);
        free(t1);
        free(t2);
    }
    return EXIT_SUCCESS;
}
