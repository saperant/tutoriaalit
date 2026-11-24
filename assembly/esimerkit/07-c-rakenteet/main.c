// Ajaa näytefunktiot, jotta niiden toiminta tulee testatuksi.
#include <stdio.h>

struct tilaus {
    char tila;
    int maara;
    double hinta;
    long asiakas;
};
struct solmu {
    long arvo;
    struct solmu *seuraava;
};

long taulukon_summa(const long *t, long n);
double tilauksen_arvo(const struct tilaus *t);
long tilauksen_asiakas(const struct tilaus *t);
long laske(int op, long a, long b);
long listan_summa(const struct solmu *s);

int main(void) {
    const long t[] = {5, 7, -2, 10};
    printf("taulukon_summa: %ld\n", taulukon_summa(t, 4));
    struct tilaus tilaus = {'A', 3, 12.5, 4021};
    printf("tilauksen_arvo: %.2f, asiakas %ld\n", tilauksen_arvo(&tilaus),
           tilauksen_asiakas(&tilaus));
    for (int op = 0; op <= 7; op++) {
        printf("laske(%d, 12, 5) = %ld\n", op, laske(op, 12, 5));
    }
    struct solmu c = {30, 0}, b = {20, &c}, a = {10, &b};
    printf("listan_summa: %ld\n", listan_summa(&a));
    return 0;
}
