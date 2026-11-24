/* Tapahtumaohjattu pääsilmukka: SysTick-keskeytys näytteistää
 * painikkeen ja lähettää tapahtumat jonoon, pääsilmukka ajaa
 * tilakonetta ja nukkuu, kun jono on tyhjä. */
#include <stdint.h>

#include "konsoli.h"
#include "mps2.h"
#include "tila.h"

// @alku painike
/* Painikkeen jännite simuloituna: (aika ms, taso). Mukana kosketin-
 * värähtelyä, jonka suodin poistaa. */
static const struct {
    uint16_t aika;
    uint8_t taso;
} reunat[] = {
    {200, 1},  {210, 0},  {220, 1},  {400, 0},   /* lyhyt, värähtelee */
    {800, 1},  {1000, 0},                        /* lyhyt */
    {2000, 1}, {2010, 0}, {2020, 1}, {2150, 0},  /* lyhyt */
    {2500, 1}, {2600, 0},                        /* lyhyt */
    {3000, 1}, {4300, 0},                        /* pitkä */
};
#define LOPPU_MS 4500u

static int raaka_painike(uint32_t nyt) {
    int taso = 0;
    for (unsigned i = 0; i < sizeof reunat / sizeof reunat[0]; i++) {
        if (reunat[i].aika <= nyt) {
            taso = reunat[i].taso;
        }
    }
    return taso;
}
// @loppu painike

// @alku jono
typedef struct {
    tapahtuma_t tyyppi;
    uint32_t aika;
} viesti_t;

#define JONON_KOKO 16u
static viesti_t jono[JONON_KOKO];
static volatile uint32_t jono_kirjoitus, jono_luku, jono_ylivuotoja;

static void jonoon(tapahtuma_t tyyppi, uint32_t aika) {   /* ISR */
    if (jono_kirjoitus - jono_luku == JONON_KOKO) {
        jono_ylivuotoja++;
        return;
    }
    jono[jono_kirjoitus % JONON_KOKO] = (viesti_t){tyyppi, aika};
    __asm__ volatile("" ::: "memory");   /* data ennen indeksiä */
    jono_kirjoitus++;
}

static int jonosta(viesti_t *viesti) {                    /* main */
    if (jono_kirjoitus == jono_luku) {
        return 0;
    }
    *viesti = jono[jono_luku % JONON_KOKO];
    __asm__ volatile("" ::: "memory");
    jono_luku++;
    return 1;
}
// @loppu jono

// @alku isr
static volatile uint32_t millit;
static suodin_t suodin;               /* vain keskeytys käyttää */

void SysTick_Handler(void) {          /* 10 ms välein */
    millit += 10;
    if (suodin_nayte(&suodin, raaka_painike(millit))) {
        jonoon(suodin.vakaa ? T_PAINETTU : T_VAPAUTETTU, millit);
    }
    jonoon(T_TIKKI, millit);
}
// @loppu isr

// @alku main
int main(void) {
    konsoli_alusta();
    valo_t valo;
    valo_alusta(&valo);
    SYSTICK->LOAD = KELLO_HZ / 100u - 1u;
    SYSTICK->VAL = 0;
    SYSTICK->CTRL = SYSTICK_CTRL_CLKSOURCE | SYSTICK_CTRL_TICKINT |
                    SYSTICK_CTRL_ENABLE;

    int led = 0;
    for (;;) {
        viesti_t viesti;
        keskeytykset_pois();
        if (!jonosta(&viesti)) {
            odota_keskeytysta();      /* jono tyhjä: nukutaan */
            keskeytykset_paalle();
            continue;
        }
        keskeytykset_paalle();

        valotila_t ennen = valo.tila;
        if (valo_kasittele(&valo, viesti.tyyppi, viesti.aika)) {
            tulosta("%4u ms  %s -> %s\n", (unsigned)viesti.aika,
                    valo_nimi(ennen), valo_nimi(valo.tila));
        }
        if (valo.led != led) {        /* tilakone päättää, ajuri tekee */
            led = valo.led;
            FPGAIO->LED = led ? LED0 : 0u;
            tulosta("%4u ms    LED0 = %d\n", (unsigned)viesti.aika, led);
        }
        if (viesti.aika >= LOPPU_MS) {
            break;
        }
    }
    SYSTICK->CTRL = 0;
    tulosta("jonon ylivuotoja %u\n", (unsigned)jono_ylivuotoja);
    return 0;
}
// @loppu main
