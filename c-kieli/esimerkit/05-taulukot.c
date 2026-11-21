#include <stddef.h>
#include <stdio.h>

// @alku pituus
#define PITUUS(t) (sizeof(t) / sizeof((t)[0]))
// @loppu pituus

// @alku parametri
// Taulukkoparametri on todellisuudessa osoitin: koko on annettava
// erikseen.
double keskiarvo(const double t[], size_t n)
{
    double summa = 0.0;
    for (size_t i = 0; i < n; ++i) {
        summa += t[i];
    }
    return n > 0 ? summa / n : 0.0;
}
// @loppu parametri

// @alku matriisi
void tulosta_matriisi(size_t rivit, size_t sarakkeet,
                      const int m[rivit][sarakkeet])
{
    for (size_t i = 0; i < rivit; ++i) {
        for (size_t j = 0; j < sarakkeet; ++j) {
            printf("%3d", m[i][j]);
        }
        printf("\n");
    }
}
// @loppu matriisi

int main(void)
{
    // @alku alustus
    int a[5] = {1, 2, 3};              // loput alkiot ovat nollia
    int b[] = {4, 5, 6, 7};            // koko päätellään: 4
    int c[10] = {[2] = 20, [7] = 70};  // nimetyt alustimet
    printf("%d %d %zu %d %d\n", a[1], a[4], PITUUS(b), c[2], c[3]);
    // @loppu alustus

    // @alku kaytto
    double mittaukset[] = {2.5, 3.0, 4.5};
    printf("keskiarvo: %.2f\n",
           keskiarvo(mittaukset, PITUUS(mittaukset)));

    int m[2][3] = {{1, 2, 3}, {4, 5, 6}};
    tulosta_matriisi(2, 3, m);
    // @loppu kaytto
}
