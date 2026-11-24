// Kohdeohjelma optimointien tunnistamiseen: upotus, häntäkutsu,
// silmukan avaus ja vektorointi sekä jakolasku vakiolla.
#include <stdio.h>

// @alku upotus
static int nelio(int x)
{
    return x * x;
}

int etaisyys2(int dx, int dy)
{
    return nelio(dx) + nelio(dy);
}
// @loppu upotus

// @alku hanta
// Rekursiivinen Eukleideen algoritmi: rekursio on häntäkutsu.
unsigned syt(unsigned a, unsigned b)
{
    if (b == 0) {
        return a;
    }
    return syt(b, a % b);
}

int ilmoita(const char *viesti)
{
    return puts(viesti);
}
// @loppu hanta

// @alku silmukat
void skaalaa(int *restrict taulu, const int *restrict lahde, int n,
             int kerroin)
{
    for (int i = 0; i < n; i++) {
        taulu[i] = lahde[i] * kerroin;
    }
}

int summa8(const int taulu[8])
{
    int s = 0;
    for (int i = 0; i < 8; i++) {
        s += taulu[i];
    }
    return s;
}
// @loppu silmukat

// @alku jako
unsigned jaa7(unsigned x) { return x / 7; }
int jaa10(int x) { return x / 10; }
unsigned jaa8(unsigned x) { return x / 8; }
int jaannos10(int x) { return x % 10; }
// @loppu jako

int main(void)
{
    int a[8] = {1, 2, 3, 4, 5, 6, 7, 8};
    int b[8];
    skaalaa(b, a, 8, 3);
    printf("%d %u %d\n", etaisyys2(3, 4), syt(84, 36), summa8(b));
    printf("%u %d %u %d\n", jaa7(100), jaa10(-95), jaa8(100),
           jaannos10(-95));
    return ilmoita("valmis") < 0;
}
