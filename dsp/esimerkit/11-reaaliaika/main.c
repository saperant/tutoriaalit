// Reaaliaikasilmukan simulaatio: ADC-keskeytys, lohkokasittely, DAC.
#include <math.h>
#include <stdbool.h>
#include <stdio.h>

#include "jono.h"
#include "prosessori.h"

#define FS 48000
#define TIKKI 48          // naytetta 1 ms:n keskeytysta kohti
#define LOHKO 32          // kasittelyn lohko
#define ESITAYTTO 64      // DAC kaynnistyy, kun ulos-jonossa on 64
#define TIKKEJA 200
#define PITUUS (TIKKI * TIKKEJA)
#define LKM 15
#define VIRHE ((unsigned long)-1)

// Sama Q1.15-alipaasto kuin taidossa Kiintea pilkku (summa noin 1,0).
static const int16_t h[LKM] = {37, -128, -525, -667, 687, 4080, 8012,
                               9779, 8012, 4080, 687, -667, -525, -128,
                               37};

static int16_t adc[PITUUS], dac[PITUUS];

static int16_t adc_nayte(size_t n)          // 1 kHz:n sini + kohina
{
    static unsigned tila = 7;
    tila = tila * 1103515245u + 12345u;
    double kohina = ((double)(tila >> 16) / 65536.0 - 0.5) * 0.1;
    return (int16_t)lround(16384.0 * (sin(2.0 * 3.14159265358979 * 1000.0
                                          * (double)n / FS) + kohina));
}

// @alku silmukka
static unsigned long simuloi(int32_t vahvistus, size_t *aloitus,
                             unsigned long *alivuodot)
{
    static int16_t sisaan_data[256], ulos_data[256], viive[2 * LKM];
    jono_t sisaan, ulos;
    prosessori_t p;
    if (jono_alusta(&sisaan, sisaan_data, 256) != 0
        || jono_alusta(&ulos, ulos_data, 256) != 0
        || prosessori_alusta(&p, h, LKM, viive, vahvistus) != 0) {
        return VIRHE;
    }
    bool kaynnissa = false;
    *alivuodot = 0;
    for (size_t t = 0; t < TIKKEJA; t++) {
        int16_t *x = &adc[t * TIKKI];       // ADC-keskeytys
        for (size_t i = 0; i < TIKKI; i++) {
            x[i] = adc_nayte(t * TIKKI + i);
        }
        if (jono_kirjoita(&sisaan, x, TIKKI) != TIKKI) {
            return VIRHE;                   // ylivuoto: kasittely ei ehdi
        }
        int16_t lohko[LOHKO];               // kasittelysaie
        while (jono_lue(&sisaan, lohko, LOHKO) == LOHKO) {
            prosessori_lohko(&p, lohko, lohko, LOHKO);
            jono_kirjoita(&ulos, lohko, LOHKO);
        }
        int16_t *y = &dac[t * TIKKI];       // DAC-keskeytys
        if (!kaynnissa && jono_taytto(&ulos) >= ESITAYTTO) {
            kaynnissa = true;
            *aloitus = t * TIKKI;
        }
        if (!kaynnissa || jono_lue(&ulos, y, TIKKI) != TIKKI) {
            for (size_t i = 0; i < TIKKI; i++) {
                y[i] = 0;                   // hiljaisuus, ei roskaa
            }
            *alivuodot += kaynnissa;
        }
    }
    return p.saturaatiot;
}
// @loppu silmukka

int main(void)
{
    // @alku tarkistus
    size_t aloitus = 0;
    unsigned long alivuodot = 0;
    unsigned long sat = simuloi(4096, &aloitus, &alivuodot);
    // Viite: koko signaali yhtena lohkona tuoreella kasittelijalla.
    static int16_t viite[PITUUS], viive[2 * LKM];
    prosessori_t p;
    if (sat == VIRHE || prosessori_alusta(&p, h, LKM, viive, 4096) != 0) {
        fputs("simulaatio epaonnistui\n", stderr);
        return 1;
    }
    prosessori_lohko(&p, adc, viite, PITUUS);
    bool samat = true;
    for (size_t i = 0; i + aloitus < PITUUS; i++) {
        samat = samat && dac[i + aloitus] == viite[i];
    }
    printf("DAC alkaa naytteesta %zu, alivuotoja %lu, saturaatioita %lu\n",
           aloitus, alivuodot, sat);
    printf("ulostulo bitilleen sama kuin kerralla: %s\n",
           samat ? "kylla" : "EI");
    printf("latenssi %zu + %d (ryhmaviive) naytetta = %.3f ms\n", aloitus,
           (LKM - 1) / 2, (double)(aloitus + (LKM - 1) / 2) * 1000.0 / FS);
    printf("vahvistus 4: saturaatioita %lu / %d\n",
           simuloi(4 * 4096, &aloitus, &alivuodot), PITUUS);
    printf("budjetti: %d MAC/nayte, %.2f MMAC/s, aikaraja %.3f ms/lohko\n",
           LKM, LKM * FS / 1e6, LOHKO * 1000.0 / FS);
    // @loppu tarkistus
    return 0;
}
