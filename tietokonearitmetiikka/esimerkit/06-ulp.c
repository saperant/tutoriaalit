// Peräkkäisten liukulukujen väli (ulp) kasvaa luvun mukana.
#include <math.h>
#include <stdio.h>

int main(void)
{
    // @alku ulp
    const double arvot[] = {1.0, 1000.0, 1e6, 9007199254740992.0};
    for (int i = 0; i < 4; i++) {
        double x = arvot[i];
        printf("double %-18.17g ulp %g\n", x, nextafter(x, INFINITY) - x);
    }
    const float f_arvot[] = {1.0f, 1000.0f, 16777216.0f};
    for (int i = 0; i < 3; i++) {
        float x = f_arvot[i];
        printf("float  %-18.9g ulp %g\n", (double)x,
               (double)(nextafterf(x, INFINITY) - x));
    }
    // @loppu ulp
    // @alku aikaleima
    // Anturin aikaleima sekunteina float-muuttujassa, 1 ms askelin.
    float aika = 0.0f;
    double tarkka = 0.0;
    for (long i = 0; i < 24L * 3600 * 1000; i++) {
        aika += 0.001f;
        tarkka += 0.001;
    }
    printf("float: %.3f s, double: %.3f s\n", (double)aika, tarkka);
    // @loppu aikaleima
    return 0;
}
