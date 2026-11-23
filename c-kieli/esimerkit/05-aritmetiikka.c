#include <stddef.h>
#include <stdio.h>

int main(void)
{
    // @alku aritmetiikka
    int t[5] = {10, 20, 30, 40, 50};
    int *p = t;            // taulukon nimi muuntuu osoittimeksi alkuun

    printf("*p = %d, *(p + 2) = %d, p[2] = %d\n", *p, *(p + 2), p[2]);

    int *loppu = t + 5;    // osoitin viimeisen alkion ohi
    ptrdiff_t etaisyys = loppu - p;
    printf("alkioita: %td\n", etaisyys);

    for (int *q = t; q != loppu; ++q) {
        *q += 1;
    }
    printf("%d %d %d %d %d\n", t[0], t[1], t[2], t[3], t[4]);
    // @loppu aritmetiikka

    // @alku koko
    double d[3] = {};
    double *dp = d;
    printf("sizeof(d) = %zu, sizeof(dp) = %zu\n", sizeof(d), sizeof(dp));
    printf("dp + 1 siirtyy %td tavua\n",
           (char *)(dp + 1) - (char *)dp);
    // @loppu koko
}
