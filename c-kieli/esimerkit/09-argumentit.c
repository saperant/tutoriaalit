#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char *argv[])
{
    // @alku argumentit
    bool tarkka = false;
    double summa = 0.0;
    int lukuja = 0;

    for (int i = 1; i < argc; ++i) {   // argv[0] on ohjelman nimi
        if (strcmp(argv[i], "--tarkka") == 0) {
            tarkka = true;
            continue;
        }
        char *loppu;
        double arvo = strtod(argv[i], &loppu);
        if (loppu == argv[i] || *loppu != '\0') {
            fprintf(stderr, "ohitetaan virheellinen luku: %s\n", argv[i]);
            continue;
        }
        summa += arvo;
        ++lukuja;
    }

    if (lukuja == 0) {
        fprintf(stderr, "käyttö: %s [--tarkka] luku...\n", argv[0]);
        return EXIT_FAILURE;
    }
    printf("%d lukua, summa %.*f\n", lukuja, tarkka ? 4 : 1, summa);
    // @loppu argumentit
}
