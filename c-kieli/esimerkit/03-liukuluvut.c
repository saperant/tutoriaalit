#include <math.h>
#include <stdio.h>

int main(void)
{
    // @alku tarkkuus
    double a = 0.1 + 0.2;
    printf("0.1 + 0.2 = %.17g\n", a);
    printf("yhtä suuri kuin 0.3: %d\n", a == 0.3);
    printf("lähes yhtä suuri: %d\n", fabs(a - 0.3) < 1e-9);
    // @loppu tarkkuus

    // @alku math
    printf("sqrt(2) = %.6f\n", sqrt(2.0));
    printf("pow(2, 10) = %.0f\n", pow(2.0, 10.0));
    printf("floor(-2.5) = %.1f, round(-2.5) = %.1f\n",
           floor(-2.5), round(-2.5));
    // @loppu math
}
