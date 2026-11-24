// Ahne vaihtorahan antaminen: otetaan aina suurin kolikko, joka mahtuu.
// Euron kolikoilla ahneus on optimaalinen, mutta keksityllä kolikko-
// sarjalla {1, 3, 4} ei. Optimi lasketaan dynaamisella ohjelmoinnilla
// (luku 9): pienin kolikkomäärä summalle s on 1 + min(pienin[s - c]).
#include <stdio.h>
#include <stdlib.h>

// @alku ahne
static int ahne(const int *kolikot, int k, int summa)  // kolikot laskevasti
{
    int maara = 0;
    for (int i = 0; i < k; i++) {
        maara += summa / kolikot[i];
        summa %= kolikot[i];
    }
    return maara;
}
// @loppu ahne

static int optimi(const int *kolikot, int k, int summa)
{
    int pienin[1001];
    pienin[0] = 0;
    for (int s = 1; s <= summa; s++) {
        pienin[s] = 1 << 20;
        for (int i = 0; i < k; i++) {
            if (kolikot[i] <= s && pienin[s - kolikot[i]] + 1 < pienin[s]) {
                pienin[s] = pienin[s - kolikot[i]] + 1;
            }
        }
    }
    return pienin[summa];
}

static void vertaa(const char *nimi, const int *kolikot, int k)
{
    int huonoja = 0, ensimmainen = 0;
    for (int s = 1; s <= 1000; s++) {
        if (ahne(kolikot, k, s) != optimi(kolikot, k, s)) {
            if (huonoja++ == 0) {
                ensimmainen = s;
            }
        }
    }
    printf("%s: ahne huonompi %d summalla 1..1000", nimi, huonoja);
    if (huonoja > 0) {
        printf(", pienin %d: ahne %d, optimi %d", ensimmainen,
               ahne(kolikot, k, ensimmainen),
               optimi(kolikot, k, ensimmainen));
    }
    printf("\n");
}

int main(void)
{
    const int euro[] = { 200, 100, 50, 20, 10, 5, 2, 1 };   // sentteinä
    const int outo[] = { 4, 3, 1 };
    vertaa("euro", euro, 8);
    vertaa("{1, 3, 4}", outo, 3);
    return EXIT_SUCCESS;
}
