// main.c: pinon käyttäjä. Ei tiedä, miten pino on toteutettu.
#include <stdio.h>
#include <stdlib.h>

#include "pino.h"

int main(void)
{
    Pino *p = pino_luo();
    if (p == nullptr) {
        return EXIT_FAILURE;
    }
    for (int i = 1; i <= 20; ++i) {
        if (!pino_lisaa(p, i * i)) {
            pino_tuhoa(p);
            return EXIT_FAILURE;
        }
    }
    printf("pinossa %zu alkiota\n", pino_koko(p));

    int arvo;
    while (pino_koko(p) > 17 && pino_ota(p, &arvo)) {
        printf("otettiin %d\n", arvo);
    }
    pino_tuhoa(p);
}
