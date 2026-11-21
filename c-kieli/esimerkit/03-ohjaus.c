#include <stdio.h>

// @alku collatz
// Laskee, montako askelta Collatzin jonossa kestää päästä ykköseen.
int collatz_askeleet(long long n)
{
    int askeleet = 0;
    while (n != 1) {
        if (n % 2 == 0) {
            n /= 2;
        } else {
            n = 3 * n + 1;
        }
        ++askeleet;
    }
    return askeleet;
}
// @loppu collatz

// @alku switch
const char *viikonpaiva(int paiva)
{
    switch (paiva) {
    case 1: return "maanantai";
    case 2: return "tiistai";
    case 3: return "keskiviikko";
    case 4: return "torstai";
    case 5: return "perjantai";
    case 6:
    case 7: return "viikonloppu";
    default: return "virheellinen";
    }
}
// @loppu switch

int main(void)
{
    // @alku for
    for (int n = 1; n <= 7; ++n) {
        if (n == 4) {
            continue;   // ohitetaan 4
        }
        printf("%d: %d askelta\n", n, collatz_askeleet(n));
    }
    // @loppu for

    // @alku dowhile
    int i = 10;
    do {
        printf("suoritetaan vähintään kerran, i = %d\n", i);
    } while (i < 5);
    // @loppu dowhile

    printf("%s %s %s\n", viikonpaiva(1), viikonpaiva(7), viikonpaiva(9));
}
