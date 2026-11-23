#include <stdio.h>

// @alku vaihda
void vaihda(int *a, int *b)
{
    int apu = *a;
    *a = *b;
    *b = apu;
}
// @loppu vaihda

// @alku jako
// Palauttaa kaksi tulosta tulosparametrien kautta.
bool jaa(int jaettava, int jakaja, int *osamaara, int *jaannos)
{
    if (jakaja == 0) {
        return false;
    }
    *osamaara = jaettava / jakaja;
    *jaannos = jaettava % jakaja;
    return true;
}
// @loppu jako

int main(void)
{
    // @alku perusteet
    int luku = 42;
    int *p = &luku;       // p osoittaa muuttujaan luku
    printf("luku = %d, *p = %d\n", luku, *p);

    *p = 7;               // muutetaan luku-muuttujaa p:n kautta
    printf("luku = %d\n", luku);

    int *tyhja = nullptr; // C23; aiemmin NULL
    if (tyhja == nullptr) {
        printf("tyhjä osoitin\n");
    }
    // @loppu perusteet

    // @alku kaytto
    int x = 1;
    int y = 2;
    vaihda(&x, &y);
    printf("x = %d, y = %d\n", x, y);

    int q;
    int r;
    if (jaa(17, 5, &q, &r)) {
        printf("17 = %d * 5 + %d\n", q, r);
    }
    if (!jaa(1, 0, &q, &r)) {
        printf("nollalla ei voi jakaa\n");
    }
    // @loppu kaytto
}
