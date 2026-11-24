// Kekolajittelu: taulukko kekoutetaan maksimikeoksi, ja suurin alkio
// vaihdetaan kerrallaan loppuun. O(n log n) myös pahimmassa
// tapauksessa ja ilman lisämuistia. Tulos tarkistetaan qsortilla.
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "satunnainen.h"

static long vertailuja;

// @alku keko
// Laskee alkiota i alaspäin, kunnes kumpikaan lapsi ei ole suurempi.
// Keko on a[0..n); solmun i lapset ovat 2i + 1 ja 2i + 2.
static void laske(int *a, int n, int i)
{
    for (;;) {
        int suurin = i, v = 2 * i + 1, o = v + 1;
        if (v < n && (vertailuja++, a[v] > a[suurin])) {
            suurin = v;
        }
        if (o < n && (vertailuja++, a[o] > a[suurin])) {
            suurin = o;
        }
        if (suurin == i) {
            return;
        }
        int t = a[i];
        a[i] = a[suurin];
        a[suurin] = t;
        i = suurin;
    }
}

static void kekolajittelu(int *a, int n)
{
    for (int i = n / 2 - 1; i >= 0; i--) {     // kekoutus O(n)
        laske(a, n, i);
    }
    for (int loppu = n - 1; loppu > 0; loppu--) {
        int t = a[0];                          // suurin loppuun
        a[0] = a[loppu];
        a[loppu] = t;
        laske(a, loppu, 0);
    }
}
// @loppu keko

static int vertaa(const void *x, const void *y)
{
    int a = *(const int *)x, b = *(const int *)y;
    return (a > b) - (a < b);
}

int main(void)
{
    enum { N = 2000 };
    static int a[N], b[N];
    const char *data[] = { "järjestetty", "satunnainen", "käänteinen" };
    Satunnainen s = { 5 };
    for (int d = 0; d < 3; d++) {
        for (int i = 0; i < N; i++) {
            a[i] = d == 0 ? i
                 : d == 1 ? (int)satunnainen_alle(&s, 1000000) : N - i;
        }
        vertailuja = 0;
        kekolajittelu(a, N);
        printf("%7ld vertailua  %s\n", vertailuja, data[d]);
    }

    // Vertailutesti qsortia vastaan satunnaisilla taulukoilla.
    int virheita = 0;
    for (int t = 0; t < 300; t++) {
        int n = (int)satunnainen_alle(&s, 200);
        for (int i = 0; i < n; i++) {
            a[i] = b[i] = (int)satunnainen_alle(&s, 50) - 25;
        }
        kekolajittelu(a, n);
        qsort(b, (size_t)n, sizeof *b, vertaa);
        virheita += memcmp(a, b, (size_t)n * sizeof *a) != 0;
    }
    printf("vertailutesti: 300 taulukkoa, %d virhettä\n", virheita);
    return EXIT_SUCCESS;
}
