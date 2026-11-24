// Pikalajittelu: jakoalkion valinta ratkaisee, onko lajittelu
// O(n log n) vai O(n^2). Mitataan vertailut ja rekursion syvyys
// järjestetyllä, satunnaisella ja tasaisella (kaikki samat) datalla.
#include <stdio.h>
#include <stdlib.h>

#include "satunnainen.h"

enum { N = 2000 };

static long vertailuja;
static int syvyys, suurin_syvyys;
static Satunnainen arpa = { 1 };

static void vaihda(int *a, int i, int j)
{
    int t = a[i];
    a[i] = a[j];
    a[j] = t;
}

// @alku lomuto
// Lomuton jako: jakoalkio a[hi]; pienemmät siirretään alkuun. Palauttaa
// jakoalkion lopullisen paikan.
static int jaa(int *a, int lo, int hi)
{
    int p = a[hi], i = lo;
    for (int j = lo; j < hi; j++) {
        vertailuja++;
        if (a[j] < p) {
            vaihda(a, i++, j);
        }
    }
    vaihda(a, i, hi);
    return i;
}

static void pika(int *a, int lo, int hi, bool satunnainen)
{
    if (lo >= hi) {
        return;
    }
    if (++syvyys > suurin_syvyys) {
        suurin_syvyys = syvyys;
    }
    if (satunnainen) {          // satunnainen alkio jakoalkioksi
        int r = lo + (int)satunnainen_alle(&arpa, (uint32_t)(hi - lo + 1));
        vaihda(a, r, hi);
    }
    int m = jaa(a, lo, hi);
    pika(a, lo, m - 1, satunnainen);
    pika(a, m + 1, hi, satunnainen);
    syvyys--;
}
// @loppu lomuto

// @alku kolmijako
// Kolmijako (Dijkstran hollantilainen lippu): < p | == p | > p.
// Yhtä suuret jäävät keskelle eivätkä enää osallistu rekursioon.
static void pika3(int *a, int lo, int hi)
{
    if (lo >= hi) {
        return;
    }
    if (++syvyys > suurin_syvyys) {
        suurin_syvyys = syvyys;
    }
    int r = lo + (int)satunnainen_alle(&arpa, (uint32_t)(hi - lo + 1));
    int p = a[r];
    int lt = lo, i = lo, gt = hi;
    while (i <= gt) {
        vertailuja++;
        if (a[i] < p) {
            vaihda(a, lt++, i++);
        } else if (a[i] > p) {
            vaihda(a, i, gt--);
        } else {
            i++;
        }
    }
    pika3(a, lo, lt - 1);
    pika3(a, gt + 1, hi);
    syvyys--;
}
// @loppu kolmijako

static bool jarjestyksessa(const int *a, int n)
{
    for (int i = 1; i < n; i++) {
        if (a[i - 1] > a[i]) {
            return false;
        }
    }
    return true;
}

static void taytto(int *a, int tyyppi)
{
    Satunnainen s = { 99 };
    for (int i = 0; i < N; i++) {
        a[i] = tyyppi == 0 ? i
             : tyyppi == 1 ? (int)satunnainen_alle(&s, 1000000)
                           : 7;
    }
}

int main(void)
{
    static int a[N];
    const char *data[] = { "järjestetty", "satunnainen", "kaikki samat" };
    const char *tapa[] = { "viimeinen", "satunnainen", "kolmijako" };
    printf("%9s %8s  %-12s %s\n", "vertailut", "syvyys", "jakoalkio",
           "data");
    for (int t = 0; t < 3; t++) {
        for (int d = 0; d < 3; d++) {
            taytto(a, d);
            vertailuja = 0;
            suurin_syvyys = 0;
            if (t < 2) {
                pika(a, 0, N - 1, t == 1);
            } else {
                pika3(a, 0, N - 1);
            }
            if (!jarjestyksessa(a, N)) {
                return EXIT_FAILURE;
            }
            printf("%9ld %8d  %-12s %s\n", vertailuja, suurin_syvyys,
                   tapa[t], data[d]);
        }
    }
    return EXIT_SUCCESS;
}
