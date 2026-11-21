#include <stdio.h>

// Lupaa, ettei funktio muuta osoitettua dataa.
int summa(const int *t, int n)
{
    int s = 0;
    for (int i = 0; i < n; ++i) {
        s += t[i];
    }
#ifndef KORJATTU
    t[0] = 0;   // virhe: data on const
#endif
    return s;
}

int main(void)
{
    int luvut[] = {1, 2, 3};
    printf("%d\n", summa(luvut, 3));

    int a = 1;
    int b = 2;
    int *const kiintea = &a;        // osoitinta ei voi siirtää
    const int *vain_luku = &a;      // dataa ei voi muuttaa osoittimen kautta
    *kiintea = 10;                  // sallittu
    vain_luku = &b;                 // sallittu
    printf("%d %d\n", a, *vain_luku);
}
