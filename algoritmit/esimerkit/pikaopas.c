// Pikaoppaan idiomit yhdessä ohjelmassa.
#include <stdio.h>
#include <stdlib.h>

// @alku vertailija
// qsortin vertailija ilman ylivuotoa: (a > b) - (a < b).
static int vertaa_int(const void *x, const void *y)
{
    int a = *(const int *)x, b = *(const int *)y;
    return (a > b) - (a < b);
}
// @loppu vertailija

// @alku alaraja
// Ensimmäinen i, jolla a[i] >= x; [lo, hi) puoliavoin.
static int alaraja(const int *a, int n, int x)
{
    int lo = 0, hi = n;
    while (lo < hi) {
        int keski = lo + (hi - lo) / 2;     // ei ylivuotoa
        if (a[keski] < x) {
            lo = keski + 1;
        } else {
            hi = keski;
        }
    }
    return lo;
}
// @loppu alaraja

// @alku reppu
// 0/1-reppu yhdellä rivillä: w laskevasti, jotta tavara käytetään
// enintään kerran (nousevasti se olisi rajoittamaton reppu).
static int reppu(const int *paino, const int *arvo, int n, int raja)
{
    int paras[101] = { 0 };
    for (int i = 0; i < n; i++) {
        for (int w = raja; w >= paino[i]; w--) {
            int uusi = paras[w - paino[i]] + arvo[i];
            paras[w] = uusi > paras[w] ? uusi : paras[w];
        }
    }
    return paras[raja];
}
// @loppu reppu

// @alku etsi
// Union-find: etsi polun puolituksella.
static int etsi(int *vanhempi, int x)
{
    while (vanhempi[x] != x) {
        vanhempi[x] = vanhempi[vanhempi[x]];
        x = vanhempi[x];
    }
    return x;
}
// @loppu etsi

int main(void)
{
    int a[] = { 9, -3, 7, 7, 0, 2147483647, -2147483647 - 1 };
    qsort(a, 7, sizeof a[0], vertaa_int);
    printf("lajiteltu:");
    for (int i = 0; i < 7; i++) {
        printf(" %d", a[i]);
    }
    printf("\nalaraja(7) = %d\n", alaraja(a, 7, 7));

    const int paino[] = { 5, 4, 6, 3 }, arvo[] = { 10, 40, 30, 50 };
    printf("reppu(10) = %d\n", reppu(paino, arvo, 4, 10));

    int vanhempi[] = { 0, 0, 1, 2, 4 };     // 3 -> 2 -> 1 -> 0, 4 erikseen
    printf("etsi(3) = %d, etsi(4) = %d\n", etsi(vanhempi, 3),
           etsi(vanhempi, 4));
    return EXIT_SUCCESS;
}
