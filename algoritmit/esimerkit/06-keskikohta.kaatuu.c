// Klassinen binäärihaun virhe: keskikohta (lo + hi) / 2. Taulukoissa
// indeksit ovat yleensä pieniä, mutta kun haetaan koko int-arvoalueelta,
// summa lo + hi ylivuotaa. Tässä haetaan kokonaislukuneliöjuurta.
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>

// @alku vaarin
// Suurin r, jolla r * r <= x. Väli [lo, hi] kattaa koko int-alueen.
static int neliojuuri(int x)
{
    int lo = 0, hi = INT_MAX;
    while (lo < hi) {
        int keski = (lo + hi + 1) / 2;     // VIRHE: ylivuoto heti alussa
        if ((long long)keski * keski <= x) {
            lo = keski;
        } else {
            hi = keski - 1;
        }
    }
    return lo;
}
// @loppu vaarin

int main(void)
{
    printf("%d\n", neliojuuri(1000000));
    return EXIT_SUCCESS;
}
