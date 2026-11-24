// Binäärihaun kaksi rajaa: alaraja (ensimmäinen alkio >= x) ja
// yläraja (ensimmäinen alkio > x). Niiden erotus on x:n esiintymien
// määrä. Tulos tarkistetaan lineaarisella haulla satunnaisilla
// taulukoilla.
#include <stdio.h>
#include <stdlib.h>

#include "satunnainen.h"

// @alku alaraja
// Puoliavoin väli [lo, hi): invariantti on, että a[0..lo) < x ja
// a[hi..n) >= x. Kun väli on tyhjä, lo on vastaus. Keskikohta
// lasketaan muodossa lo + (hi - lo) / 2, joka ei voi ylivuotaa.
static int alaraja(const int *a, int n, int x)
{
    int lo = 0, hi = n;
    while (lo < hi) {
        int keski = lo + (hi - lo) / 2;
        if (a[keski] < x) {
            lo = keski + 1;
        } else {
            hi = keski;
        }
    }
    return lo;
}

// Ainoa ero: ehto on <= eikä <.
static int ylaraja(const int *a, int n, int x)
{
    int lo = 0, hi = n;
    while (lo < hi) {
        int keski = lo + (hi - lo) / 2;
        if (a[keski] <= x) {
            lo = keski + 1;
        } else {
            hi = keski;
        }
    }
    return lo;
}
// @loppu alaraja

static int lineaarinen(const int *a, int n, int x, bool tiukka)
{
    int i = 0;
    while (i < n && (tiukka ? a[i] <= x : a[i] < x)) {
        i++;
    }
    return i;
}

int main(void)
{
    // @alku esimerkki
    const int a[] = { 2, 3, 3, 3, 7, 9, 9, 12 };
    const int n = sizeof a / sizeof a[0];
    for (int x = 1; x <= 13; x += 2) {
        int al = alaraja(a, n, x), yl = ylaraja(a, n, x);
        printf("x = %2d: alaraja %d, yläraja %d, esiintymiä %d\n",
               x, al, yl, yl - al);
    }
    // @loppu esimerkki

    Satunnainen s = { 3 };
    int virheita = 0;
    for (int kierros = 0; kierros < 1000; kierros++) {
        int m = (int)satunnainen_alle(&s, 50);
        int b[50];
        int arvo = 0;
        for (int i = 0; i < m; i++) {
            arvo += (int)satunnainen_alle(&s, 3);   // kasvava, toistoja
            b[i] = arvo;
        }
        for (int x = -1; x <= arvo + 1; x++) {
            if (alaraja(b, m, x) != lineaarinen(b, m, x, false) ||
                ylaraja(b, m, x) != lineaarinen(b, m, x, true)) {
                virheita++;
            }
        }
    }
    printf("satunnaistesti: 1000 taulukkoa, %d virhettä\n", virheita);
    return EXIT_SUCCESS;
}
