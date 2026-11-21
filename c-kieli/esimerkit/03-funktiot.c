#include <stdio.h>

// @alku prototyypit
int syt(int a, int b);            // prototyyppi: esittely ilman runkoa
static void vaihda(int a, int b);
static int seuraava_tunnus(void);
// @loppu prototyypit

int main(void)
{
    // @alku kaytto
    printf("syt(84, 36) = %d\n", syt(84, 36));

    int x = 1;
    int y = 2;
    vaihda(x, y);
    printf("x = %d, y = %d\n", x, y);   // ennallaan!

    int a = seuraava_tunnus();
    int b = seuraava_tunnus();
    int c = seuraava_tunnus();
    printf("tunnukset: %d %d %d\n", a, b, c);
    // @loppu kaytto
}

// @alku maaritelmat
// Suurin yhteinen tekijä Eukleideen algoritmilla (rekursiivisesti).
int syt(int a, int b)
{
    return b == 0 ? a : syt(b, a % b);
}

// Parametrit ovat kopioita: vaihto ei näy kutsujalle.
static void vaihda(int a, int b)
{
    int apu = a;
    a = b;
    b = apu;
    printf("funktion sisällä: a = %d, b = %d\n", a, b);
}

// Staattinen paikallinen muuttuja säilyttää arvonsa kutsujen välillä.
static int seuraava_tunnus(void)
{
    static int laskuri = 0;
    return ++laskuri;
}
// @loppu maaritelmat
