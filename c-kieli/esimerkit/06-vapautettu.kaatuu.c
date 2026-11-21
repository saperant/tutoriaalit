#include <stdio.h>
#include <stdlib.h>

typedef struct {
    int *arvot;
} Taulu;

void taulu_vapauta(Taulu *t)
{
    free(t->arvot);   // vapauttaa muistin, mutta ei nollaa osoitinta
}

int main(void)
{
    Taulu a = {.arvot = malloc(4 * sizeof(int))};
    if (a.arvot == nullptr) {
        return EXIT_FAILURE;
    }
    a.arvot[0] = 42;
    Taulu b = a;           // kopio: molemmat osoittavat samaan muistiin
    taulu_vapauta(&a);
    printf("%d\n", b.arvot[0]);   // käyttö vapautuksen jälkeen
}
