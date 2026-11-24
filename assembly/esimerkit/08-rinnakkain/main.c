// Sama algoritmi kahdella käskykannalla: tulos ja koodin koko.
#include <stdio.h>

void lajittele(long *t, long n);
extern const char lajittele_loppu[];

static void tulosta(const char *nimi, const long *t, long n) {
    printf("%s:", nimi);
    for (long i = 0; i < n; i++) {
        printf(" %ld", t[i]);
    }
    printf("\n");
}

int main(void) {
    long t[] = {42, -7, 19, 0, 19, 3, -50, 8};
    long n = sizeof t / sizeof t[0];
    tulosta("ennen", t, n);
    lajittele(t, n);
    tulosta("jälkeen", t, n);
    long yksi[] = {5};
    lajittele(yksi, 1);
    lajittele(t, 0);
    // Funktion koko: loppumerkin ja alun osoitteiden erotus.
    printf("lajittele: %td tavua\n",
           lajittele_loppu - (const char *)lajittele);
    return 0;
}
