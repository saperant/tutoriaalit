// Kohdeohjelma x86-64-assemblyn lukemiseen: argumenttien välitys,
// pinokehys, paluuarvot ja tavallisimmat käskyt.
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>

// @alku summa
// Taulukon alkioiden summa. Silmukka, osoitin ja kerääjä.
int64_t summa(const int32_t *taulu, size_t n)
{
    int64_t tulos = 0;
    for (size_t i = 0; i < n; i++) {
        tulos += taulu[i];
    }
    return tulos;
}
// @loppu summa

// @alku painotettu
// Kahdeksan argumenttia: kuusi ensimmäistä rekistereissä, loput pinossa.
long painotettu(long a, long b, long c, long d, long e, long f, long g,
                long h)
{
    return a + 2 * b + 3 * c + 4 * d + 5 * e + 6 * f + 7 * g + 8 * h;
}
// @loppu painotettu

// @alku piste
struct piste {
    double x;
    double y;
};

// Pieni rakenne palautetaan rekistereissä xmm0 ja xmm1.
struct piste keskipiste(struct piste a, struct piste b)
{
    struct piste k = {(a.x + b.x) / 2.0, (a.y + b.y) / 2.0};
    return k;
}
// @loppu piste

// @alku kehys
// Paikallinen taulukko pinossa: pinokehys ja kanarialintu.
int suurin_numero(const char *teksti)
{
    char puskuri[32];
    int suurin = -1;
    snprintf(puskuri, sizeof puskuri, "%s", teksti);
    for (int i = 0; puskuri[i] != '\0'; i++) {
        int numero = puskuri[i] - '0';
        if (numero >= 0 && numero <= 9 && numero > suurin) {
            suurin = numero;
        }
    }
    return suurin;
}
// @loppu kehys

int main(void)
{
    const int32_t arvot[] = {4, -2, 9, 7};
    struct piste a = {0.0, 0.0};
    struct piste b = {3.0, 5.0};
    struct piste k = keskipiste(a, b);
    printf("summa %lld\n", (long long)summa(arvot, 4));
    printf("painotettu %ld\n", painotettu(1, 1, 1, 1, 1, 1, 1, 1));
    printf("keskipiste %.1f %.1f\n", k.x, k.y);
    printf("suurin numero %d\n", suurin_numero("v2026-k11"));
    return 0;
}
