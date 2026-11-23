#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// @alku kirjoita
bool kirjoita_raportti(const char *polku)
{
    FILE *f = fopen(polku, "w");
    if (f == nullptr) {
        perror(polku);   // tulostaa virheen syyn stderr-virtaan
        return false;
    }
    for (int i = 1; i <= 3; ++i) {
        fprintf(f, "rivi %d: %d\n", i, i * i);
    }
    // fclose voi epäonnistua, jos puskuroidun datan kirjoitus epäonnistuu.
    return fclose(f) == 0;
}
// @loppu kirjoita

// @alku lue
long laske_rivit(const char *polku)
{
    FILE *f = fopen(polku, "r");
    if (f == nullptr) {
        return -1;
    }
    long rivit = 0;
    int merkki;
    while ((merkki = fgetc(f)) != EOF) {   // merkki on int, ei char
        if (merkki == '\n') {
            ++rivit;
        }
    }
    bool virhe = ferror(f);
    fclose(f);
    return virhe ? -1 : rivit;
}
// @loppu lue

int main(void)
{
    // @alku kaytto
    if (!kirjoita_raportti("raportti.txt")) {
        return EXIT_FAILURE;
    }

    FILE *f = fopen("raportti.txt", "r");
    if (f == nullptr) {
        return EXIT_FAILURE;
    }
    char rivi[64];
    while (fgets(rivi, sizeof rivi, f) != nullptr) {
        printf("luettiin: %s", rivi);
    }
    fclose(f);

    printf("rivejä: %ld\n", laske_rivit("raportti.txt"));

    errno = 0;
    if (laske_rivit("puuttuu.txt") < 0) {
        printf("virhe: %s\n", strerror(errno));
    }
    remove("raportti.txt");
    // @loppu kaytto
}
