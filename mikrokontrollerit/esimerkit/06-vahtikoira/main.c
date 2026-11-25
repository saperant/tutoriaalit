/* Vahtikoira: väärä ja oikea ruokintapaikka. Pääsilmukka jumiutuu
 * kolmannella kierroksella odottamaan kuittausta, jota ei tule.
 *
 * Käynnistys 1: vahtikoiraa ruokitaan tikkikeskeytyksessä. Keskeytys
 *   toimii, vaikka pääsilmukka on jumissa, joten vahtikoira ei laukea.
 * Käynnistys 2: ruokinta on pääsilmukan lopussa. Vahtikoira varoittaa
 *   (NMI) ja resetoi laitteen.
 * Käynnistys 3: ohjelma lukee .noinit-alueelta, miksi se käynnistyi. */
#include <stdint.h>

#include "konsoli.h"
#include "mps2.h"

#define AIKARAJA_MS 100u

// @alku tila
enum vaihe { VAIHE_EI, VAIHE_MITTAUS, VAIHE_LAHETYS };
static const char *const vaiheen_nimi[] = {"-", "mittaus", "lähetys"};

/* Säilyvät resetin yli: käynnistyskoodi ei koske .noinit-alueeseen. */
#define TAIKA 0x56414854u
__attribute__((section(".noinit"))) static uint32_t taika;
__attribute__((section(".noinit"))) static uint32_t kaynnistys;
__attribute__((section(".noinit"))) static uint32_t vahti_laukesi;
__attribute__((section(".noinit"))) static uint32_t jumivaihe;
// @loppu tila

static volatile uint32_t millit;
static volatile uint32_t edistys_ms;     /* edellisen kierroksen loppu */
static volatile enum vaihe vaihe;
static volatile int ruoki_tikissa;
static volatile int kuittaus;            /* laite ei koskaan aseta tätä */

// @alku vahti
static void vahti_alusta(uint32_t ms) {
    VAHTIKOIRA->LOCK = VAHTI_AVAIN;      /* rekisterit auki */
    VAHTIKOIRA->LOAD = (KELLO_HZ / 1000u) * ms;
    VAHTIKOIRA->CTRL = VAHTI_CTRL_INTEN | VAHTI_CTRL_RESEN;
    VAHTIKOIRA->LOCK = 0;                /* lukkoon: karannut ohjelma
                                            ei voi sammuttaa vahtia */
}

static void vahti_ruoki(void) {
    VAHTIKOIRA->LOCK = VAHTI_AVAIN;
    VAHTIKOIRA->INTCLR = 1u;             /* lataa laskurin uudelleen */
    VAHTIKOIRA->LOCK = 0;
}
// @loppu vahti

static void ohjelmallinen_reset(void) {
    SCB->AIRCR = SCB_AIRCR_AVAIMET | SCB_AIRCR_SYSRESETREQ;
    muistiaita();
    for (;;) {
    }
}

// @alku tikki
void SysTick_Handler(void) {
    millit++;
    if (ruoki_tikissa) {
        vahti_ruoki();                   /* VÄÄRIN: ei todista mitään */
        if (millit - edistys_ms == 3u * AIKARAJA_MS) {
            tulosta("  pääsilmukka on ollut jumissa %u ms, "
                    "vahtikoira ei lauennut\n", 3u * AIKARAJA_MS);
            ohjelmallinen_reset();       /* esimerkki jatkuu */
        }
    }
}
// @loppu tikki

// @alku nmi
/* Ensimmäinen aikaraja: viimeinen tilaisuus kirjata, missä oltiin.
 * Keskeytystä ei kuitata, joten toinen aikaraja resetoi laitteen. */
void NMI_Handler(void) {
    vahti_laukesi = 1;
    jumivaihe = vaihe;
    tulosta("  NMI: vahtikoira varoittaa, vaihe = %s\n",
            vaiheen_nimi[vaihe]);
}
// @loppu nmi

static void viive_ms(uint32_t ms) {
    uint32_t alku = millit;
    while ((uint32_t)(millit - alku) < ms) {
        odota_keskeytysta();
    }
}

// @alku tyo
static void mittaa(void) {
    vaihe = VAIHE_MITTAUS;
    viive_ms(10);
}

/* Kolmannella kierroksella vastapuoli ei kuittaa, ja silmukassa ei ole
 * aikakatkaisua: tavallinen tapa jumiutua. */
static void laheta(unsigned kierros) {
    vaihe = VAIHE_LAHETYS;
    viive_ms(10);
    while (kierros == 3 && !kuittaus) {
        odota_keskeytysta();
    }
}

static void paasilmukka(void) {
    for (unsigned kierros = 1;; kierros++) {
        mittaa();
        laheta(kierros);
        if (!ruoki_tikissa) {
            vahti_ruoki();               /* OIKEIN: kierros tehtiin */
        }
        edistys_ms = millit;
        tulosta("  kierros %u valmis\n", kierros);
    }
}
// @loppu tyo

// @alku main
int main(void) {
    konsoli_alusta();
    if (taika != TAIKA) {                /* virrankytkentä */
        taika = TAIKA;
        kaynnistys = 0;
        vahti_laukesi = 0;
    }
    kaynnistys++;
    tulosta("käynnistys %u: ", (unsigned)kaynnistys);
    if (vahti_laukesi) {
        tulosta("vahtikoira resetoi, jumissa vaiheessa %s\n",
                vaiheen_nimi[jumivaihe]);
        return 0;
    }
    ruoki_tikissa = (kaynnistys == 1);
    tulosta("ruokinta %s\n",
            ruoki_tikissa ? "tikkikeskeytyksessä" : "pääsilmukan lopussa");

    SYSTICK->LOAD = KELLO_HZ / 1000u - 1u;
    SYSTICK->VAL = 0;
    SYSTICK->CTRL = SYSTICK_CTRL_CLKSOURCE | SYSTICK_CTRL_TICKINT |
                    SYSTICK_CTRL_ENABLE;
    vahti_alusta(AIKARAJA_MS);
    paasilmukka();
    return 1;
}
// @loppu main
