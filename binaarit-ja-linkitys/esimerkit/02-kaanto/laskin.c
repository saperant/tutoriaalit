#include "laskin.h"

// @alku laskin
static long alenna(long summa, int prosentti)
{
    return summa - summa * prosentti / 100;
}

long loppusumma(long kappalehinta, int maara, int alennus)
{
    return alenna(kappalehinta * maara, alennus);
}
// @loppu laskin
