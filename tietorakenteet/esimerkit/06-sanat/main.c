// Sanojen esiintymät tekstissä: hajautustaulu laskee, lajittelu
// järjestää tuloksen. Teksti luetaan syötteestä.
#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "kartta.h"

static int useimmat_ensin(const void *a, const void *b)
{
    const Pari *x = a, *y = b;
    if (x->arvo != y->arvo) {
        return x->arvo < y->arvo ? 1 : -1;
    }
    return strcmp(x->avain, y->avain);  // tasapelit aakkosjärjestykseen
}

// @alku paa
int main(void)
{
    Kartta *k = kartta_luo();
    if (k == nullptr) {
        return EXIT_FAILURE;
    }
    char sana[64];
    size_t pituus = 0;
    int c;
    long sanoja = 0;
    do {
        c = getchar();
        // UTF-8:n monitavuiset merkit (ä, ö) kuuluvat sanaan.
        if (c != EOF && (isalpha(c) || c >= 0x80)) {
            if (pituus + 1 < sizeof sana) {
                sana[pituus++] = (char)tolower(c);
            }
        } else if (pituus > 0) {
            sana[pituus] = '\0';
            pituus = 0;
            sanoja++;
            if (!kartta_kasvata(k, sana)) {
                kartta_tuhoa(k);
                return EXIT_FAILURE;
            }
        }
    } while (c != EOF);

    size_t n = kartta_koko(k);
    Pari *parit = malloc(n * sizeof *parit);
    if (parit == nullptr) {
        kartta_tuhoa(k);
        return EXIT_FAILURE;
    }
    kartta_parit(k, parit);
    qsort(parit, n, sizeof *parit, useimmat_ensin);
    for (size_t i = 0; i < 5 && i < n; i++) {
        printf("%3ld  %s\n", parit[i].arvo, parit[i].avain);
    }
    printf("sanoja %ld, eri sanoja %zu, ämpäreitä %zu, "
           "uudelleenhajautuksia %d\n", sanoja, n, kartta_ampareita(k),
           kartta_uudelleenhajautuksia(k));
    printf("'tieto' esiintyy %ld kertaa\n", kartta_arvo(k, "tieto"));
    free(parit);
    kartta_tuhoa(k);
    return EXIT_SUCCESS;
}
// @loppu paa
