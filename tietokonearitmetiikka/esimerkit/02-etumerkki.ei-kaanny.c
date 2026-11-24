// Puskurin sijainnin tarkistus: etumerkillinen ja etumerkitön vertailu.
#include <stddef.h>
#include <stdio.h>

// Palauttaa, osuuko siirtymä puskurin sisään.
static int sisalla(int siirtyma, size_t koko)
{
    // @alku vertailu
#ifndef KORJATTU
    return siirtyma < koko;      // -1 muuttuu luvuksi 2^64 - 1
#else
    return siirtyma >= 0 && (size_t)siirtyma < koko;
#endif
    // @loppu vertailu
}

int main(void)
{
    printf("%d %d %d\n", sisalla(3, 10), sisalla(10, 10), sisalla(-1, 10));
    return 0;
}
