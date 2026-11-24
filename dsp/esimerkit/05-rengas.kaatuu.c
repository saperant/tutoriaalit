// Yleinen virhe: rengaspuskurin indeksi ilman kiertoa.
#include <stddef.h>
#include <stdio.h>

#define LKM 4

static const double h[LKM] = {0.25, 0.25, 0.25, 0.25};
static double viive[LKM];       // tavallinen rengas ilman kaksoiskopiota
static size_t paikka;

// @alku virhe
static double suodata(double x)
{
    viive[paikka] = x;
    double summa = 0.0;
    for (size_t k = 0; k < LKM; k++) {
        summa += h[k] * viive[paikka + k];   // VIRHE: (paikka + k) % LKM
    }
    paikka = (paikka + 1) % LKM;
    return summa;
}
// @loppu virhe

int main(void)
{
    for (int i = 0; i < 8; i++) {
        printf("%.2f\n", suodata(1.0));
    }
    return 0;
}
