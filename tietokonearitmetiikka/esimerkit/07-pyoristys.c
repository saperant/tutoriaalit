// Pyöristystilat ja pyöristysfunktiot.
#include <fenv.h>
#include <math.h>
#include <stdio.h>

int main(void)
{
    volatile double yksi = 1.0, kolme = 3.0;   // ei käännösaikana
    // @alku tilat
    const int tilat[] = {FE_TONEAREST, FE_UPWARD, FE_DOWNWARD,
                         FE_TOWARDZERO};
    const char *nimet[] = {"FE_TONEAREST", "FE_UPWARD", "FE_DOWNWARD",
                           "FE_TOWARDZERO"};
    for (int i = 0; i < 4; i++) {
        fesetround(tilat[i]);
        double x = yksi / kolme;
        printf("%-13s %.20f\n", nimet[i], x);
    }
    fesetround(FE_TONEAREST);
    // @loppu tilat
    // @alku funktiot
    const double arvot[] = {2.5, 3.5, -2.5, 2.4999999999999996};
    for (int i = 0; i < 4; i++) {
        double x = arvot[i];
        printf("%-19.17g round %4g  rint %4g  floor %4g  trunc %4g\n", x,
               round(x), rint(x), floor(x), trunc(x));
    }
    // @loppu funktiot
    return 0;
}
