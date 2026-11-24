/* Dynaaminen muisti: FreeRTOSin heap_1 eli kasvava osoitin.
 * Muistia voi vain varata, ei vapauttaa, joten pirstoutumista ei
 * synny ja varauksen kesto on vakio. Sopii järjestelmiin, joissa
 * kaikki oliot luodaan käynnistyksessä. */
#include "kide_sisainen.h"

// @alku keko
static uint8_t keko[configTOTAL_HEAP_SIZE] __attribute__((aligned(8)));
static size_t kaytetty;

void *pvPortMalloc(size_t koko) {
    koko = (koko + 7u) & ~(size_t)7u;   /* 8 tavun tasaus (AAPCS) */
    void *osoite = NULL;
    portti_kriittinen_alku();
    if (koko <= sizeof keko - kaytetty) {
        osoite = &keko[kaytetty];
        kaytetty += koko;
    }
    portti_kriittinen_loppu();
    return osoite;
}

size_t xPortGetFreeHeapSize(void) {
    return sizeof keko - kaytetty;
}
// @loppu keko
