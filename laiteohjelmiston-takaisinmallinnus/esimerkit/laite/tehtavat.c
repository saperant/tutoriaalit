/* Tehtävätaulu ja yksinkertainen ajoittaja: jokainen tehtävä ajetaan,
 * kun simuloitu kello on sen jakson monikerta. Oikeassa laitteessa
 * kello etenisi SysTick-keskeytyksestä. */
#include "tehtavat.h"
#include "asetukset.h"
#include "loki.h"
#include "mps2.h"
#include "suodatin.h"

typedef struct {
    const char *nimi;
    uint32_t jakso_ms;
    void (*aja)(uint32_t aika_ms);
} tehtava_t;

#define NAYTTEITA 8u

static int16_t naytteet[NAYTTEITA];
static unsigned naytteita;
static uint32_t kello_ms;
static uint8_t tila;

/* Anturin simuloitu raaka-arvo: hidas saha 20,00..20,75 astetta. */
static int32_t lue_anturi(uint32_t aika_ms) {
    return 2000 + (int32_t)((aika_ms / TIKKI_MS) % 16u) * 5;
}

static void mittaa(uint32_t aika_ms) {
    const asetukset_t *a = asetukset();
    int32_t raaka = lue_anturi(aika_ms);
    int32_t arvo = (int32_t)(((int64_t)raaka * a->kerroin) >> 16) +
                   a->siirto;
    naytteet[naytteita % NAYTTEITA] = (int16_t)arvo;
    naytteita++;
}

static void kirjaa(uint32_t aika_ms) {
    int16_t tulos[NAYTTEITA];
    unsigned n = naytteita < NAYTTEITA ? naytteita : NAYTTEITA;
    int16_t keskiarvo = suodata(naytteet, n, 4, tulos);
    loki_kirjaa(aika_ms, keskiarvo, tila);
}

static void vahti(uint32_t aika_ms) {
    tila ^= 1u;
    FPGAIO_LED = tila | (aika_ms >= 60000u ? 2u : 0u);
}

static const tehtava_t tehtavat[] = {
    {"mittaus", 100, mittaa},
    {"kirjaus", 800, kirjaa},
    {"vahti", 500, vahti},
};

void ajoita(uint32_t kesto_ms) {
    uint32_t loppu = kello_ms + kesto_ms;
    while (kello_ms < loppu) {
        kello_ms += TIKKI_MS;
        for (unsigned i = 0; i < sizeof tehtavat / sizeof tehtavat[0];
             i++) {
            if (kello_ms % tehtavat[i].jakso_ms == 0) {
                tehtavat[i].aja(kello_ms);
            }
        }
    }
}

uint32_t ajoaika_ms(void) {
    return kello_ms;
}
