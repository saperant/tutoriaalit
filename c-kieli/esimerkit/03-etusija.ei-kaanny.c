#include <stdio.h>

constexpr unsigned VALMIS = 1u << 2;

int main(void)
{
    unsigned liput = 0b0011;
#ifndef KORJATTU
    if (liput & VALMIS == 0) {     // virhe: liput & (VALMIS == 0)
#else
    if ((liput & VALMIS) == 0) {   // sulkeet: ensin maski, sitten vertailu
#endif
        printf("ei valmis\n");
    }
}
