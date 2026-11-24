// Ohi-yhdellä-virhe: silmukka kirjoittaa yhden alkion liikaa.
#include <stdio.h>
#include <stdlib.h>

static double *kopioi(const double *x, size_t n)
{
    double *kopio = malloc(n * sizeof *kopio);
    for (size_t i = 0; i <= n; i++) // pitäisi olla i < n
        kopio[i] = i < n ? x[i] : 0.0;
    return kopio;
}

int main(void)
{
    double x[] = {21.5, 22.0, 21.8, 23.1, 22.4};
    double *k = kopioi(x, 5);
    printf("ensimmäinen %.1f\n", k[0]);
    free(k);
    return 0;
}
