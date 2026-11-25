// Viiveen jakauma ja häntä: kaksi palvelua, joilla on sama keskiarvo
// ja sama läpäisy, mutta eri prosenttipisteet.
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>

#include "mittari.h"
#include "satunnainen.h"

enum { PYYNTOJA = 10000 };

// @alku prosenttipiste
// Prosenttipiste järjestetystä taulukosta (lähimmän arvon menetelmä):
// p99 on arvo, jonka alle jää 99 % pyynnöistä.
static double prosenttipiste(const double *jarjestetty, size_t n, double p)
{
    size_t i = (size_t)(p / 100.0 * (double)n + 0.5);
    return jarjestetty[i == 0 ? 0 : (i > n ? n : i) - 1];
}
// @loppu prosenttipiste

// @alku palvelut
// Tasainen palvelu: jokainen pyyntö kestää 1,1–1,3 ms.
static double tasainen(Satunnainen *s)
{
    return 1.1 + (double)satunnainen_alle(s, 2001) / 10000.0;
}

// Hännällinen palvelu: 98 % pyynnöistä kestää 0,8–1,0 ms, mutta joka
// viideskymmenes osuu hitaaseen polkuun (esimerkiksi välimuistihuti
// levylle asti) ja kestää 16 ms.
static double hannallinen(Satunnainen *s)
{
    if (satunnainen_alle(s, 50) == 0) {
        return 16.0;
    }
    return 0.8 + (double)satunnainen_alle(s, 2001) / 10000.0;
}
// @loppu palvelut

static void raportti(const char *nimi, double (*palvelu)(Satunnainen *))
{
    static double ms[PYYNTOJA];
    Satunnainen s = {2026};
    double summa = 0;
    for (int i = 0; i < PYYNTOJA; i++) {
        ms[i] = palvelu(&s);
        summa += ms[i];
    }
    qsort(ms, PYYNTOJA, sizeof *ms, vertaa_double);
    // Yksi säie käsittelee pyynnöt peräkkäin: läpäisy on määrä / aika.
    printf("%-12s %9.2f %7.2f %7.2f %7.2f %7.2f %10.0f\n", nimi,
           summa / PYYNTOJA, prosenttipiste(ms, PYYNTOJA, 50),
           prosenttipiste(ms, PYYNTOJA, 95),
           prosenttipiste(ms, PYYNTOJA, 99), ms[PYYNTOJA - 1],
           PYYNTOJA / (summa / 1000.0));
}

int main(void)
{
    printf("%-12s %9s %7s %7s %7s %7s %10s\n", "palvelu", "keskiarvo",
           "p50", "p95", "p99", "suurin", "pyyntoa/s");
    raportti("tasainen", tasainen);
    raportti("hannallinen", hannallinen);
    return 0;
}
