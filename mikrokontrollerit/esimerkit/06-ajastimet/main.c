/* Ajastimet: SysTick-tikki, viive ilman kiireistä odotusta, CMSDK-
 * ajastimen jaksollinen keskeytys ja kuittaamaton keskeytys. */
#include <stdint.h>

#include "konsoli.h"
#include "mps2.h"

// @alku systick
static volatile uint32_t millit;    /* kasvaa kerran millisekunnissa */

void SysTick_Handler(void) {
    millit++;
}

static void systick_alusta(uint32_t jakso) {
    SYSTICK->LOAD = jakso - 1u;      /* laskee LOAD..0: jakso kelloa */
    SYSTICK->VAL = 0;                /* mikä tahansa kirjoitus nollaa */
    SYSTICK->CTRL = SYSTICK_CTRL_CLKSOURCE | SYSTICK_CTRL_TICKINT |
                    SYSTICK_CTRL_ENABLE;
}
// @loppu systick

// @alku viive
/* Erotus nyt - alku on oikein myös laskurin pyörähtäessä ympäri, koska
 * etumerkittömän aritmetiikan tulos lasketaan modulo 2^32. */
static void viive_ms(uint32_t ms) {
    uint32_t alku = millit;
    while ((uint32_t)(millit - alku) < ms) {
        odota_keskeytysta();         /* nukutaan seuraavaan tikkiin */
    }
}
// @loppu viive

// @alku ajastin0
static volatile uint32_t ajastin0_kertoja;

void TIMER0_IRQHandler(void) {
    AJASTIN0->INTSTATUS = 1u;        /* kuittaus: kirjoita 1 */
    ajastin0_kertoja++;
    FPGAIO->LED ^= LED0;
}

static void ajastin0_alusta(uint32_t jakso) {
    AJASTIN0->CTRL = 0;
    AJASTIN0->RELOAD = jakso - 1u;   /* asettaa myös VALUE:n */
    AJASTIN0->INTSTATUS = 1u;
    AJASTIN0->CTRL = AJASTIN_CTRL_EN | AJASTIN_CTRL_IRQEN;
    nvic_salli(TIMER0_IRQn);
}
// @loppu ajastin0

// @alku myrsky
static volatile uint32_t ajastin1_kertoja;
static volatile int kuittaa_heti;

void TIMER1_IRQHandler(void) {
    ajastin1_kertoja++;
    if (kuittaa_heti || ajastin1_kertoja == 1000) {
        AJASTIN1->INTSTATUS = 1u;
    }
}

static uint32_t yksi_laukaisu(int kuittaus) {
    kuittaa_heti = kuittaus;
    ajastin1_kertoja = 0;
    /* RELOAD-kirjoitus asettaa myös VALUE:n, joten järjestys on tämä. */
    AJASTIN1->RELOAD = KELLO_HZ;            /* seuraava vasta 1 s päästä */
    AJASTIN1->VALUE = KELLO_HZ / 1000u;     /* laukeaa 1 ms päästä */
    AJASTIN1->CTRL = AJASTIN_CTRL_EN | AJASTIN_CTRL_IRQEN;
    viive_ms(5);
    AJASTIN1->CTRL = 0;
    return ajastin1_kertoja;
}
// @loppu myrsky

int main(void) {
    konsoli_alusta();
    // @alku pyorahdys
    uint32_t alku = 0xFFFFFFF0u, nyt = 0x00000005u;   /* 21 ms myöhemmin */
    tulosta("alku 0x%08x, nyt 0x%08x\n", (unsigned)alku, (unsigned)nyt);
    tulosta("  nyt >= alku + 10:  %s\n", nyt >= alku + 10u ? "kyllä" : "ei");
    tulosta("  nyt - alku >= 10:  %s\n",
            (uint32_t)(nyt - alku) >= 10u ? "kyllä" : "ei");
    // @loppu pyorahdys

    // @alku kaytto
    millit = 0xFFFFFFF0u;              /* pyörähtää 16 ms kuluttua */
    systick_alusta(KELLO_HZ / 1000u);  /* 25 000 kelloa = 1 ms */
    viive_ms(20);
    tulosta("viive_ms(20) yli pyörähdyksen: %s\n",
            millit < 0xFFFFFFF0u ? "valmis, laskuri pyörähti" : "kesken");

    ajastin0_alusta(KELLO_HZ / 10u);   /* 100 ms jakso */
    while (ajastin0_kertoja < 10) {
        odota_keskeytysta();
    }
    nvic_kiella(TIMER0_IRQn);
    tulosta("ajastin0: %u keskeytystä, LED0=%u\n",
            (unsigned)ajastin0_kertoja, (unsigned)(FPGAIO->LED & LED0));
    // @loppu kaytto

    nvic_salli(TIMER1_IRQn);
    tulosta("yksi laukaisu, kuitattu heti: %u käsittelykertaa\n",
            (unsigned)yksi_laukaisu(1));
    tulosta("yksi laukaisu, ei kuitattu:   %u käsittelykertaa\n",
            (unsigned)yksi_laukaisu(0));
    return 0;
}
