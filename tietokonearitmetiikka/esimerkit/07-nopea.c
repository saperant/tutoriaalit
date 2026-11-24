// Mitä -ffast-math lupaa kääntäjälle. Normaalisti käännettynä ohjelma
// laskee IEEE 754:n mukaan; esimerkkien Makefile kääntää sen myös
// valitsimilla -O2 -ffast-math ja näyttää eron.
#include <math.h>
#include <stdio.h>

// @alku nopea
// Kahanin korjaustermi on algebrallisesti nolla: (t - s) - y.
static double kahan(const double *x, int n)
{
    double s = 0.0, c = 0.0;
    for (int i = 0; i < n; i++) {
        double y = x[i] - c;
        double t = s + y;
        c = (t - s) - y;
        s = t;
    }
    return s;
}

// Puuttuvat mittaukset on merkitty NaN:lla.
static int puuttuvia(const double *x, int n)
{
    int k = 0;
    for (int i = 0; i < n; i++) {
        k += isnan(x[i]);
    }
    return k;
}
// @loppu nopea

int main(void)
{
    static double x[1001];
    volatile double iso = 1e16, yksi = 1.0, puuttuu = NAN;
    x[0] = iso;
    for (int i = 1; i < 1001; i++) {
        x[i] = yksi;
    }
    printf("summa %.17g\n", kahan(x, 1001) - iso);
    double m[3] = {21.5, puuttuu, 22.0};
    printf("puuttuvia %d\n", puuttuvia(m, 3));
    return 0;
}
