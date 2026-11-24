// Kasvunopeus mitattuna: kuinka monta vertailua neljä algoritmia tekee,
// kun syöte kaksinkertaistuu? Suhde T(2n) / T(n) paljastaa
// kertaluokan: 2 on lineaarinen, 4 neliöllinen, hieman yli 2 n log n.
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "satunnainen.h"

static long vertailuja;

static int lineaarinen_haku(const int *a, int n, int x)
{
    for (int i = 0; i < n; i++) {
        vertailuja++;
        if (a[i] == x) {
            return i;
        }
    }
    return -1;
}

static int binaarihaku(const int *a, int n, int x)
{
    int lo = 0, hi = n;                 // vastaus on välillä [lo, hi)
    while (lo < hi) {
        int m = lo + (hi - lo) / 2;
        vertailuja++;
        if (a[m] < x) {
            lo = m + 1;
        } else {
            hi = m;
        }
    }
    return lo;
}

static void lisayslajittelu(int *a, int n)
{
    for (int i = 1; i < n; i++) {
        int x = a[i], j = i;
        while (j > 0 && (vertailuja++, a[j - 1] > x)) {
            a[j] = a[j - 1];
            j--;
        }
        a[j] = x;
    }
}

static void lomitus(int *a, int *apu, int n)
{
    if (n < 2) {
        return;
    }
    int m = n / 2;
    lomitus(a, apu, m);
    lomitus(a + m, apu, n - m);
    int i = 0, j = m, k = 0;
    while (i < m && j < n) {
        vertailuja++;
        apu[k++] = a[j] < a[i] ? a[j++] : a[i++];
    }
    while (i < m) {
        apu[k++] = a[i++];
    }
    while (j < n) {
        apu[k++] = a[j++];
    }
    memcpy(a, apu, (size_t)n * sizeof *a);
}

enum { KOKOJA = 4, ALGORITMEJA = 4 };

// @alku mittaus
// Vertailujen määrä algoritmille a syötekoolla n. Satunnainen data on
// sama joka ajolla, joten luvut ovat toistettavia.
static long mittaa(int a, int n)
{
    int *x = malloc((size_t)n * sizeof *x);
    int *apu = malloc((size_t)n * sizeof *apu);
    if (x == nullptr || apu == nullptr) {
        exit(EXIT_FAILURE);
    }
    Satunnainen s = { (uint64_t)n };
    for (int i = 0; i < n; i++) {
        x[i] = (int)satunnainen_alle(&s, 1000000);
    }
    vertailuja = 0;
    switch (a) {
    case 0: lineaarinen_haku(x, n, -1); break;        // pahin tapaus
    case 1: lomitus(x, apu, n);
            vertailuja = 0;
            for (int i = 0; i < n; i++) {             // n hakua
                binaarihaku(x, n, x[i]);
            }
            vertailuja /= n;                          // yhtä kohden
            break;
    case 2: lomitus(x, apu, n); break;
    default: lisayslajittelu(x, n); break;
    }
    free(x);
    free(apu);
    return vertailuja;
}
// @loppu mittaus

int main(void)
{
    const char *nimi[ALGORITMEJA] = {
        "lineaarihaku", "binäärihaku", "lomitus", "lisäys",
    };
    const int koko[KOKOJA] = { 1000, 2000, 4000, 8000 };
    printf("%10s%10s%10s%10s  suhde  algoritmi\n",
           "n = 1000", "2000", "4000", "8000");
    for (int a = 0; a < ALGORITMEJA; a++) {
        long t[KOKOJA];
        for (int k = 0; k < KOKOJA; k++) {
            t[k] = mittaa(a, koko[k]);
            printf("%10ld", t[k]);
        }
        printf("  %5.2f  %s\n", (double)t[3] / (double)t[2], nimi[a]);
    }
    return EXIT_SUCCESS;
}
