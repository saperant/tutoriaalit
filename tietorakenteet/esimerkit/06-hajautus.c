// Hajautusfunktion laatu ratkaisee hajautustaulun nopeuden. Viedään
// 10 000 käyttäjätunnusta 1024 ämpäriin kahdella funktiolla ja
// mitataan, kuinka tasaisesti ne jakautuvat.
#include <stdint.h>
#include <stdio.h>
#include <string.h>

enum { AVAIMIA = 10000, AMPAREITA = 1024 };

// @alku funktiot
// Huono: tavujen summa. Anagrammit ja lähes samat merkkijonot
// päätyvät samaan tai viereisiin ämpäreihin, ja arvoalue on pieni.
static uint32_t summa(const char *s)
{
    uint32_t h = 0;
    while (*s != '\0') {
        h += (unsigned char)*s++;
    }
    return h;
}

// FNV-1a (Fowler–Noll–Vo): XOR ja kertolasku alkuluvulla tavu
// kerrallaan. Yksinkertainen, nopea ja hyvin sekoittava lyhyille
// avaimille.
static uint32_t fnv1a(const char *s)
{
    uint32_t h = 2166136261u;           // FNV-siirtymä
    while (*s != '\0') {
        h ^= (unsigned char)*s++;
        h *= 16777619u;                 // FNV-alkuluku
    }
    return h;
}
// @loppu funktiot

// @alku mittaus
static void mittaa(const char *nimi, uint32_t (*hajauta)(const char *))
{
    static int ketju[AMPAREITA];
    memset(ketju, 0, sizeof ketju);
    char avain[32];
    for (int i = 0; i < AVAIMIA; i++) {
        snprintf(avain, sizeof avain, "kayttaja%d", i);
        ketju[hajauta(avain) % AMPAREITA]++;
    }
    int tyhjia = 0, pisin = 0;
    long vertailuja = 0;        // onnistuneet haut, kaikki avaimet
    for (int a = 0; a < AMPAREITA; a++) {
        tyhjia += ketju[a] == 0;
        pisin = ketju[a] > pisin ? ketju[a] : pisin;
        vertailuja += (long)ketju[a] * (ketju[a] + 1) / 2;
    }
    printf("%-6s tyhjiä %4d  pisin ketju %4d  vertailuja/haku %6.2f\n",
           nimi, tyhjia, pisin, (double)vertailuja / AVAIMIA);
}
// @loppu mittaus

int main(void)
{
    double alfa = (double)AVAIMIA / AMPAREITA;
    printf("kuormituskerroin %.2f, tasaisella jakaumalla "
           "vertailuja/haku noin %.2f\n", alfa, 1.0 + alfa / 2.0);
    mittaa("summa", summa);
    mittaa("FNV-1a", fnv1a);
    return 0;
}
