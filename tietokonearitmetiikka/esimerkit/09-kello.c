// Luvun 6 pysähtyvä kello uudelleen: sama float-kertymä, mutta summa
// pyöristetään stokastisesti.
#include <math.h>
#include <stdint.h>
#include <stdio.h>

// @alku satunnainen
// xorshift64*: pieni näennäissatunnaislukugeneraattori. Alkutila on
// kiinteä, joten ajo on toistettava.
static uint64_t tila = 0x9e3779b97f4a7c15u;

static double tasainen(void)            // tasajakauma välillä [0, 1)
{
    tila ^= tila >> 12;
    tila ^= tila << 25;
    tila ^= tila >> 27;
    return (double)((tila * 0x2545f4914f6cdd1du) >> 11) * 0x1p-53;
}
// @loppu satunnainen

// @alku pyoristys
// Pyöristää double-arvon float-arvoksi stokastisesti.
static float stokastinen(double x)
{
    float lahin = (float)x;             // tavallinen pyöristys
    if ((double)lahin == x) {
        return lahin;                   // esitettävissä tarkasti
    }
    float ala = (double)lahin < x ? lahin : nextafterf(lahin, -INFINITY);
    float yla = nextafterf(ala, INFINITY);
    double osuus = (x - (double)ala) / ((double)yla - (double)ala);
    return tasainen() < osuus ? yla : ala;
}
// @loppu pyoristys

int main(void)
{
    // @alku kello
    // Vuorokausi millisekunnin askelin, kuten luvussa 6.
    float lahimpaan = 0.0f, stok = 0.0f;
    for (long i = 0; i < 24L * 3600 * 1000; i++) {
        lahimpaan += 0.001f;
        stok = stokastinen((double)stok + (double)0.001f);
    }
    // @loppu kello
    printf("lähimpään:   %8.0f s\n", (double)lahimpaan);
    printf("stokastinen: %8.0f s, virhe %.2f %%\n", (double)stok,
           100.0 * fabs((double)stok - 86400.0) / 86400.0);
    return 0;
}
