#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// @alku laskin
static int plus(int a, int b) { return a + b; }
static int miinus(int a, int b) { return a - b; }
static int kerto(int a, int b) { return a * b; }

struct operaatio {
    char merkki;
    int (*funktio)(int, int);   // osoitin funktioon
};

static const struct operaatio operaatiot[] = {
    {'+', plus}, {'-', miinus}, {'*', kerto},
};
// @loppu laskin

// @alku vertailu
// qsort antaa alkioiden osoitteet void-osoittimina.
static int vertaa_laskevasti(const void *a, const void *b)
{
    int x = *(const int *)a;
    int y = *(const int *)b;
    return (x < y) - (x > y);   // ei ylivuotoa, toisin kuin y - x
}

static int vertaa_merkkijonoja(const void *a, const void *b)
{
    const char *const *s = a;
    const char *const *t = b;
    return strcmp(*s, *t);
}
// @loppu vertailu

int main(void)
{
    // @alku kaytto
    for (size_t i = 0; i < sizeof operaatiot / sizeof operaatiot[0]; ++i) {
        const struct operaatio *op = &operaatiot[i];
        printf("6 %c 3 = %d\n", op->merkki, op->funktio(6, 3));
    }

    int luvut[] = {3, 1, 4, 1, 5, 9, 2, 6};
    size_t n = sizeof luvut / sizeof luvut[0];
    qsort(luvut, n, sizeof luvut[0], vertaa_laskevasti);
    for (size_t i = 0; i < n; ++i) {
        printf("%d ", luvut[i]);
    }
    printf("\n");

    const char *nimet[] = {"Ritchie", "Kernighan", "Thompson"};
    qsort(nimet, 3, sizeof nimet[0], vertaa_merkkijonoja);
    printf("%s %s %s\n", nimet[0], nimet[1], nimet[2]);
    // @loppu kaytto
}
