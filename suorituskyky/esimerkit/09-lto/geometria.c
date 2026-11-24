// geometria.c: erillinen käännösyksikkö.
#include "geometria.h"

// @alku etaisyys
double etaisyys2(Piste a, Piste b)
{
    double dx = a.x - b.x;
    double dy = a.y - b.y;
    return dx * dx + dy * dy;
}
// @loppu etaisyys
