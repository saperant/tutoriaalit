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
unsigned long kymmenesosa(unsigned long x);
long kahdeksasosa(long x);
long valita(long x);

// valita() kutsuu tätä häntäkutsuna.
long tarkista(long x) {
    return x < 0 ? -x : x;
}

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
    printf("kymmenesosa(1234567) = %lu\n", kymmenesosa(1234567));
    printf("kahdeksasosa(-17) = %ld, kahdeksasosa(17) = %ld\n",
           kahdeksasosa(-17), kahdeksasosa(17));
    printf("valita(-20) = %ld\n", valita(-20));
    return 0;
}
