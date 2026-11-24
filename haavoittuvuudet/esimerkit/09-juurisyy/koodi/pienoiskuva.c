/* Pienoiskuvan varaus: neljä tavua pikseliä kohden (RGBA). */
#include <stdlib.h>

unsigned char *varaa_pienoiskuva(int leveys, int korkeus)
{
    return malloc(leveys * korkeus * 4);
}
