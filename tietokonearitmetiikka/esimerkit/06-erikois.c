// Ääretön, NaN ja negatiivinen nolla.
#include <math.h>
#include <stdio.h>

// Lukee arvot ajonaikaisesti, ettei kääntäjä laske tuloksia valmiiksi.
static double nolla(void) { volatile double z = 0.0; return z; }

int main(void)
{
    double z = nolla();
    // @alku erikois
    double ylivuoto = 1e308 * 10.0;
    double ei_luku = z / z;                // 0/0
    double miinus_nolla = -1.0 * z;
    printf("%g %g %g %g\n", ylivuoto, -ylivuoto, ei_luku, miinus_nolla);
    printf("NaN == NaN: %d, isnan: %d\n", ei_luku == ei_luku,
           isnan(ei_luku));
    printf("-0 == 0: %d, signbit: %d, 1/-0 = %g\n", miinus_nolla == 0.0,
           signbit(miinus_nolla) != 0, 1.0 / miinus_nolla);
    printf("NaN < 1: %d, NaN > 1: %d, fmax(NaN, 1) = %g\n",
           ei_luku < 1.0, ei_luku > 1.0, fmax(ei_luku, 1.0));
    // @loppu erikois
    // @alku keskiarvo
    // Puuttuva mittaus NaN:na myrkyttää keskiarvon.
    const double mittaukset[] = {21.5, 22.0, NAN, 21.0};
    double summa = 0.0, ohitettu = 0.0;
    int n = 0;
    for (int i = 0; i < 4; i++) {
        summa += mittaukset[i];
        if (!isnan(mittaukset[i])) {
            ohitettu += mittaukset[i];
            n++;
        }
    }
    printf("keskiarvo %g, puuttuvat ohittaen %g\n", summa / 4,
           ohitettu / n);
    // @loppu keskiarvo
    return 0;
}
