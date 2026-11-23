#include <stdio.h>
#include <string.h>

int main(void)
{
    // @alku rivit
    char rivi[256];
    int rivinro = 0;
    double summa = 0.0;

    while (fgets(rivi, sizeof rivi, stdin) != nullptr) {
        ++rivinro;
        rivi[strcspn(rivi, "\n")] = '\0';   // poistetaan rivinvaihto

        char nimi[64];
        double hinta;
        int maara;
        if (sscanf(rivi, "%63s %lf %d", nimi, &hinta, &maara) != 3) {
            printf("rivi %d ohitettu: '%s'\n", rivinro, rivi);
            continue;
        }
        printf("%-10s %3d x %6.2f = %7.2f\n", nimi, maara, hinta,
               hinta * maara);
        summa += hinta * maara;
    }
    printf("yhteensä %.2f\n", summa);
    // @loppu rivit
}
