#include <limits.h>
#include <stdckdint.h>
#include <stdio.h>

// @alku tarkistettu
// Laskee n! ja palauttaa false, jos tulos ei mahdu int-tyyppiin.
bool kertoma(int n, int *tulos)
{
    int t = 1;
    for (int i = 2; i <= n; ++i) {
        if (ckd_mul(&t, t, i)) {   // true = ylivuoto
            return false;
        }
    }
    *tulos = t;
    return true;
}
// @loppu tarkistettu

int main(void)
{
    // @alku kaytto
    for (int n = 11; n <= 14; ++n) {
        int k;
        if (kertoma(n, &k)) {
            printf("%d! = %d\n", n, k);
        } else {
            printf("%d! ei mahdu int-tyyppiin\n", n);
        }
    }

    int summa;
    bool ylivuoto = ckd_add(&summa, INT_MAX, 1);
    printf("INT_MAX + 1: ylivuoto %d\n", ylivuoto);
    // @loppu kaytto
}
