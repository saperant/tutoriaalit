// Lisäyslajittelu: paras, keskimääräinen ja pahin tapaus. Vertailujen
// määrä riippuu syötteen järjestyksestä: lähes järjestetty data on
// halpa, käänteinen kallis.
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>

#include "satunnainen.h"

enum { N = 2000 };

static long vertailuja;

// @alku lisays
// Invariantti: ennen kierrosta i osa a[0..i) on järjestyksessä.
// Alkio x siirtyy vasemmalle niin kauan kuin edellinen on suurempi.
// Yhtä suuria ei ohiteta, joten lajittelu on vakaa.
static void lisayslajittelu(int *a, int n)
{
    for (int i = 1; i < n; i++) {
        int x = a[i];
        int j = i;
        while (j > 0 && (vertailuja++, a[j - 1] > x)) {
            a[j] = a[j - 1];
            j--;
        }
        a[j] = x;
    }
}
// @loppu lisays

static bool jarjestyksessa(const int *a, int n)
{
    for (int i = 1; i < n; i++) {
        if (a[i - 1] > a[i]) {
            return false;
        }
    }
    return true;
}

static void kokeile(const char *nimi, int *a)
{
    vertailuja = 0;
    lisayslajittelu(a, N);
    assert(jarjestyksessa(a, N));
    printf("%9ld vertailua  %s\n", vertailuja, nimi);
}

int main(void)
{
    static int a[N];
    Satunnainen s = { 7 };

    for (int i = 0; i < N; i++) {
        a[i] = i;
    }
    kokeile("järjestetty", a);                  // paras: n - 1

    for (int i = 0; i < N; i++) {
        a[i] = i;
    }
    for (int k = 0; k < 20; k++) {               // 20 vaihtoa
        int i = (int)satunnainen_alle(&s, N);
        int j = (int)satunnainen_alle(&s, N);
        int t = a[i];
        a[i] = a[j];
        a[j] = t;
    }
    kokeile("lähes järjestetty", a);

    for (int i = 0; i < N; i++) {
        a[i] = (int)satunnainen_alle(&s, 1000000);
    }
    kokeile("satunnainen", a);                  // noin n^2 / 4

    for (int i = 0; i < N; i++) {
        a[i] = N - i;
    }
    kokeile("käänteinen", a);                   // pahin: n(n-1)/2
    return EXIT_SUCCESS;
}
