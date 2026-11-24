// Seinäkello ja prosessiaika: mitä kumpikin mittaa.
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <time.h>

#include "mittari.h"

static const char *kylla(bool ehto)
{
    return ehto ? "kylla" : "ei";
}

// @alku laskenta
// Laskee, kunnes prosessiaikaa on kulunut vähintään `ms` millisekuntia.
static uint64_t laske(int64_t ms)
{
    int64_t loppu = prosessiaika_ns() + ms * 1000000;
    uint64_t x = 1;
    while (prosessiaika_ns() < loppu) {
        for (int i = 0; i < 1000; i++) {
            x = x * 6364136223846793005u + 1442695040888963407u;
        }
    }
    return x;
}
// @loppu laskenta

static void tulosta_tarkkuus(const char *nimi, clockid_t kello)
{
    struct timespec t;
    clock_getres(kello, &t);
    printf("  %-26s %ld ns\n", nimi, t.tv_sec * 1000000000L + t.tv_nsec);
}

static void kutsu_kelloa(void *p)
{
    int64_t *summa = p;
    for (int i = 0; i < 1000; i++) {
        *summa += seinakello_ns();
    }
}

static void mittaa_kaikki(void)
{
    printf("kellojen tarkkuus (clock_getres)\n");
    tulosta_tarkkuus("CLOCK_MONOTONIC", CLOCK_MONOTONIC);
    tulosta_tarkkuus("CLOCK_PROCESS_CPUTIME_ID", CLOCK_PROCESS_CPUTIME_ID);
    int64_t summa = 0;
    Tilasto t = mittaa(kutsu_kelloa, &summa, 101);
    kayta(&summa);
    printf("clock_gettime-kutsun hinta: %.1f ns\n", t.mediaani * 1e3);
}

int main(int argc, char **argv)
{
    if (mittaustila(argc, argv)) {
        mittaa_kaikki();
        return 0;
    }
    // @alku testi
    int64_t s0 = seinakello_ns();
    int64_t p0 = prosessiaika_ns();
    struct timespec uni = {0, 50 * 1000000};    // 50 ms
    nanosleep(&uni, NULL);
    int64_t s1 = seinakello_ns();
    int64_t p1 = prosessiaika_ns();
    uint64_t x = laske(30);
    int64_t s2 = seinakello_ns();
    int64_t p2 = prosessiaika_ns();
    kayta(&x);

    printf("nukkuminen 50 ms\n");
    printf("  seinakello >= 50 ms: %s\n", kylla(s1 - s0 >= 50000000));
    printf("  prosessiaika < 10 ms: %s\n", kylla(p1 - p0 < 10000000));
    printf("laskenta 30 ms\n");
    printf("  prosessiaika >= 30 ms: %s\n", kylla(p2 - p1 >= 30000000));
    printf("  seinakello >= prosessiaika: %s\n",
           kylla(s2 - s1 + 1000000 >= p2 - p1));
    // @loppu testi
    return 0;
}
