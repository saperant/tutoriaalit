// Amdahlin laki: kokonaisnopeutus, kun osa työstä nopeutuu.
#include <stdio.h>

// @alku amdahl
// Osuus p ajasta nopeutuu kertoimella s; loput 1 - p ei nopeudu.
static double amdahl(double p, double s)
{
    return 1.0 / ((1.0 - p) + p / s);
}
// @loppu amdahl

// @alku tarvittava
// Kuinka suuri osuus on nopeutettava kertoimella s, jotta
// kokonaisnopeutus olisi tavoite? Ratkaistaan p Amdahlin kaavasta.
static double tarvittava_osuus(double tavoite, double s)
{
    return (1.0 - 1.0 / tavoite) / (1.0 - 1.0 / s);
}
// @loppu tarvittava

int main(void)
{
    // @alku taulukko
    const double osuudet[] = {0.50, 0.80, 0.90, 0.95, 0.99};
    const double kertoimet[] = {2, 4, 16, 64, 1e12};
    printf("   p |    s=2    s=4   s=16   s=64  s=inf\n");
    printf("-----+-----------------------------------\n");
    for (int i = 0; i < 5; i++) {
        printf("%.2f |", osuudet[i]);
        for (int j = 0; j < 5; j++) {
            printf(" %6.2f", amdahl(osuudet[i], kertoimet[j]));
        }
        printf("\n");
    }
    // @loppu taulukko
    printf("\nkokonaisnopeutus 2, kun osa nopeutuu kertoimella s:\n");
    for (int j = 0; j < 3; j++) {
        double s = kertoimet[j + 1];
        printf("  s = %2.0f: osuuden oltava vahintaan %.3f\n", s,
               tarvittava_osuus(2.0, s));
    }
    return 0;
}
