// Rengaspuskurin testi: samat tapaukset, jotka otsakkeen kommentit
// lupaavat.
#include <assert.h>
#include <stdio.h>

#include "puskuri.h"

int main(void)
{
    struct puskuri p;
    float keskiarvo = -1.0f;
    puskuri_alusta(&p);
    assert(!puskuri_keskiarvo(&p, &keskiarvo));
    assert(keskiarvo == -1.0f);   // tyhjä puskuri ei muuta tulosta

    for (int i = 1; i <= PUSKURI_KOKO; i++) {
        assert(!puskuri_lisaa(&p, (float)i));
    }
    assert(puskuri_keskiarvo(&p, &keskiarvo));
    printf("täysi puskuri: keskiarvo %.2f\n", (double)keskiarvo);

    assert(puskuri_lisaa(&p, 17.0f));   // korvaa arvon 1
    assert(puskuri_keskiarvo(&p, &keskiarvo));
    printf("vanhin korvattu: keskiarvo %.2f\n", (double)keskiarvo);
    return 0;
}
