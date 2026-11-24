// Kohdeohjelma dynaamiseen analyysiin: tilauksen hinnoittelu.
#include <stdio.h>
#include <string.h>

struct rivi {
    int tuote;
    int maara;
    int yksikkohinta; // senteissä
};

long myynti_yhteensa;

// @alku funktiot
[[gnu::noinline]] int tarkista_koodi(const char *koodi)
{
    // Alennuskoodin tarkiste: merkkien summa modulo 97.
    unsigned summa = 0;
    for (size_t i = 0; i < strlen(koodi); i++) {
        summa += (unsigned char)koodi[i];
    }
    return strlen(koodi) == 8 && summa % 97 == 13;
}

[[gnu::noinline]] long alennus(int asiakasluokka, long summa)
{
    long prosentti = asiakasluokka >= 2 ? 10 : 0;
    if (summa > 10000) {
        prosentti += 5;
    }
    return summa * prosentti / 100;
}

[[gnu::noinline]] long laske_hinta(const struct rivi *rivit, int n,
                                   int asiakasluokka)
{
    long summa = 0;
    for (int i = 0; i < n; i++) {
        summa += (long)rivit[i].maara * rivit[i].yksikkohinta;
    }
    summa -= alennus(asiakasluokka, summa);
    myynti_yhteensa += summa;
    return summa;
}
// @loppu funktiot

int main(int argc, char **argv)
{
    const struct rivi pieni[] = {{101, 2, 450}, {205, 1, 1290}};
    const struct rivi iso[] = {{101, 20, 450}, {310, 3, 2500}};
    printf("pieni tilaus: %ld\n", laske_hinta(pieni, 2, 1));
    printf("iso tilaus: %ld\n", laske_hinta(iso, 2, 2));
    const char *koodi = argc > 1 ? argv[1] : "KEVAT-26";
    if (tarkista_koodi(koodi)) {
        puts("alennuskoodi hyväksytty");
    } else {
        puts("alennuskoodi hylätty");
    }
    printf("myynti yhteensä: %ld\n", myynti_yhteensa);
    return 0;
}
