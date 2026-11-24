#include <stdalign.h>
#include <stdio.h>

#include "viesti.h"

#define KENTTA(T, k) \
    printf("  %-10s siirtymä %2zu, koko %zu\n", #k, offsetof(T, k), \
           sizeof(((T *)0)->k))

int main(void)
{
    // @alku tulostus
    printf("perustyypit: long %zu, pointer %zu, long double %zu "
           "(tasaus %zu)\n", sizeof(long), sizeof(void *),
           sizeof(long double), alignof(long double));

    printf("viesti_huono: koko %zu, tasaus %zu\n",
           sizeof(struct viesti_huono), alignof(struct viesti_huono));
    KENTTA(struct viesti_huono, tyyppi);
    KENTTA(struct viesti_huono, aikaleima);
    KENTTA(struct viesti_huono, pituus);
    KENTTA(struct viesti_huono, tarkiste);
    // @loppu tulostus
    printf("viesti: koko %zu, tasaus %zu\n", sizeof(struct viesti),
           alignof(struct viesti));
    KENTTA(struct viesti, aikaleima);
    KENTTA(struct viesti, tarkiste);
    KENTTA(struct viesti, pituus);
    KENTTA(struct viesti, tyyppi);
    printf("viesti_levy: koko %zu, tasaus %zu\n",
           sizeof(struct viesti_levy), alignof(struct viesti_levy));
    return 0;
}
