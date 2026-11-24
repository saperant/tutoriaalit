/* Liukuva keskiarvo kokonaisluvuin: tulos[i] on ikkunan näytteiden
 * keskiarvo. Palauttaa viimeisen tuloksen. */
#include "suodatin.h"

#if !defined(VERSIO_240) && !defined(KORJATTU)
/* Virheenjäljitystä varten; poista ennen julkaisua. */
__attribute__((optimize("O0")))
#endif
int16_t suodata(const int16_t *naytteet, size_t n, size_t ikkuna,
                int16_t *tulos) {
    int16_t viimeinen = 0;
    for (size_t i = 0; i < n; i++) {
        size_t alku = i + 1 >= ikkuna ? i + 1 - ikkuna : 0;
        int32_t summa = 0;
        for (size_t j = alku; j <= i; j++) {
            summa += naytteet[j];
        }
        viimeinen = (int16_t)(summa / (int32_t)(i + 1 - alku));
        tulos[i] = viimeinen;
    }
    return viimeinen;
}
