/* Virransäästö: WFI-silmukka ja kadonnut herätys. */
#include <stdint.h>

#include "konsoli.h"
#include "mps2.h"

static volatile uint32_t tapahtumia;      /* ajastin0 */
static volatile int tapahtuma;            /* VAPAA0 */

// @alku isr
void TIMER0_IRQHandler(void) {
    AJASTIN0->INTSTATUS = 1u;
    tapahtumia++;
}

void VAPAA0_IRQHandler(void) {
    tapahtuma = 1;
}
// @loppu isr

static void ajastin0_kaynnista(uint32_t jakso) {
    AJASTIN0->CTRL = 0;
    AJASTIN0->RELOAD = jakso - 1u;
    AJASTIN0->INTSTATUS = 1u;
    tapahtumia = 0;
    AJASTIN0->CTRL = AJASTIN_CTRL_EN | AJASTIN_CTRL_IRQEN;
}

// @alku silmukka
static void odota_tapahtumia(uint32_t montako) {
    uint32_t heratyksia = 0;
    while (tapahtumia < montako) {
        keskeytykset_pois();
        if (tapahtumia < montako) {
            odota_keskeytysta();
            heratyksia++;
        }
        keskeytykset_paalle();
    }
    tulosta("%u tapahtumaa, %u herätystä\n", (unsigned)tapahtumia,
            (unsigned)heratyksia);
}
// @loppu silmukka

// @alku kadonnut
/* VIRHE: tarkistuksen ja WFI:n välissä tullut keskeytys ei herätä. */
static void nuku_vaarin(void) {
    tapahtuma = 0;
    ajastin0_kaynnista(KELLO_HZ);      /* varaherätys 1 s päästä */
    if (!tapahtuma) {
        nvic_laukaise(VAPAA0_IRQn);    /* keskeytys osuu juuri tähän */
        muistiaita();
        odota_keskeytysta();           /* nukutaan silti */
    }
    tulosta("väärin: tapahtuma=%d, herätti ajastin: %s\n", tapahtuma,
            tapahtumia > 0 ? "kyllä" : "ei");
}

static void nuku_oikein(void) {
    tapahtuma = 0;
    ajastin0_kaynnista(KELLO_HZ);
    keskeytykset_pois();
    if (!tapahtuma) {
        nvic_laukaise(VAPAA0_IRQn);    /* jää odottamaan */
        muistiaita();
        odota_keskeytysta();           /* odottava keskeytys herättää */
    }
    keskeytykset_paalle();             /* VAPAA0 ajetaan tässä */
    tulosta("oikein: tapahtuma=%d, herätti ajastin: %s\n", tapahtuma,
            tapahtumia > 0 ? "kyllä" : "ei");
}
// @loppu kadonnut

int main(void) {
    konsoli_alusta();
    nvic_salli(TIMER0_IRQn);
    nvic_salli(VAPAA0_IRQn);

    ajastin0_kaynnista(KELLO_HZ / 10u);   /* 100 ms */
    odota_tapahtumia(5);

    nuku_vaarin();
    nuku_oikein();

    AJASTIN0->CTRL = 0;
    return 0;
}
