// Kohdeohjelma kääntäjän rakenteiden tunnistamiseen: ehtolauseet,
// silmukat, switch, rakenteet ja taulukot.
#include <stdio.h>

// @alku luokka
int luokka(int pisteet)
{
    if (pisteet >= 90) {
        return 5;
    } else if (pisteet >= 75) {
        return 4;
    } else if (pisteet >= 50) {
        return 3;
    }
    return 0;
}
// @loppu luokka

// @alku hinnoittele
// Tiheä switch: kääntäjä tekee hyppytaulun.
int hinnoittele(int asiakasluokka, int hinta)
{
    switch (asiakasluokka) {
    case 0: return hinta;
    case 1: return hinta - hinta / 20;
    case 2: return hinta - hinta / 10;
    case 3: return hinta - hinta / 5;
    case 4: return hinta / 2;
    case 5: return 0;
    default: return -1;
    }
}
// @loppu hinnoittele

// @alku tuote
struct tuote {
    int tunnus;
    int saldo;
    double hinta;
};

double varaston_arvo(const struct tuote *tuotteet, int n)
{
    double arvo = 0.0;
    for (int i = 0; i < n; i++) {
        arvo += tuotteet[i].saldo * tuotteet[i].hinta;
    }
    return arvo;
}
// @loppu tuote

// @alku ruudukko
int lavan_paino(const int ruudukko[4][5], int rivi)
{
    int summa = 0;
    for (int s = 0; s < 5; s++) {
        summa += ruudukko[rivi][s];
    }
    return summa;
}
// @loppu ruudukko

// @alku pituus
unsigned pituus(const char *s)
{
    unsigned n = 0;
    while (s[n] != '\0') {
        n++;
    }
    return n;
}
// @loppu pituus

int main(void)
{
    const struct tuote t[] = {{1, 3, 2.5}, {2, 10, 0.75}};
    const int lava[4][5] = {{1, 2, 3, 4, 5}, {6, 7, 8, 9, 10}};
    printf("%d %d %d\n", luokka(80), hinnoittele(2, 200),
           hinnoittele(9, 200));
    printf("%.2f %d %u\n", varaston_arvo(t, 2), lavan_paino(lava, 1),
           pituus("varasto"));
    return 0;
}
