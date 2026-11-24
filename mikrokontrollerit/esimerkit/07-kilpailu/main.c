/* Pääohjelman ja keskeytyksen yhteinen data. Keskeytys laukaistaan
 * tarkoituksella pahimpaan kohtaan, jotta kilpailutilanne toistuu
 * joka ajossa samana. */
#include <stdint.h>

#include "konsoli.h"
#include "mps2.h"

static volatile uint32_t jaettu;
static volatile uint64_t tikit64;
static volatile int keskeytyksen_tyo;   /* 0: jaettu += 100, 1: tikki */

void VAPAA0_IRQHandler(void) {
    if (keskeytyksen_tyo == 0) {
        jaettu += 100;
    } else {
        tikit64++;
    }
}

/* Keskeytys juuri nyt: tämän jälkeen se on jo ajettu, jos sallittu. */
static void keskeytys_tahan(void) {
    nvic_laukaise(VAPAA0_IRQn);
    muistiaita();
}

// @alku menetetty
/* jaettu++ on kolme käskyä: ldr, adds, str. Keskeytys välissä. */
static void kasvata_suojaamatta(void) {
    uint32_t arvo = jaettu;            /* ldr */
    keskeytys_tahan();                 /* ISR: jaettu += 100 */
    jaettu = arvo + 1;                 /* adds, str: ISR:n työ katoaa */
}
// @loppu menetetty

// @alku kriittinen
static void kasvata_suojattuna(void) {
    uint32_t tila = lue_primask();     /* olivatko keskeytykset jo pois? */
    keskeytykset_pois();
    uint32_t arvo = jaettu;
    keskeytys_tahan();                 /* jää odottamaan */
    jaettu = arvo + 1;
    aseta_primask(tila);               /* ISR ajetaan vasta tässä */
}
// @loppu kriittinen

// @alku sokea
/* VIRHE: palauttaa keskeytykset päälle, vaikka kutsuja oli kieltänyt ne. */
static void apu_sokea(void) {
    keskeytykset_pois();
    /* ... jotain lyhyttä ... */
    keskeytykset_paalle();
}

static void kasvata_sisakkain(void) {
    uint32_t tila = lue_primask();
    keskeytykset_pois();
    uint32_t arvo = jaettu;
    apu_sokea();                       /* PRIMASK = 0 tästä eteenpäin */
    keskeytys_tahan();
    jaettu = arvo + 1;
    aseta_primask(tila);
}
// @loppu sokea

// @alku ldrex
/* LDREX merkitsee osoitteen varatuksi; STREX onnistuu vain, jos
 * varaus on voimassa. Poikkeus välissä purkaa varauksen. */
static uint32_t kasvata_ldrex(void) {
    uint32_t yrityksia = 0, epaonnistui;
    do {
        uint32_t arvo;
        __asm__ volatile("ldrex %0, [%1]" : "=r"(arvo) : "r"(&jaettu));
        if (++yrityksia == 1) {
            keskeytys_tahan();
        }
        __asm__ volatile("strex %0, %2, [%1]"
                         : "=&r"(epaonnistui)
                         : "r"(&jaettu), "r"(arvo + 1)
                         : "memory");
    } while (epaonnistui);
    return yrityksia;
}
// @loppu ldrex

// @alku repeama
/* 64-bittinen luku on Cortex-M3:lla kaksi 32-bittistä lukua. */
static uint64_t lue_suojaamatta(void) {
    const volatile uint32_t *osat = (const volatile uint32_t *)&tikit64;
    uint32_t ala = osat[0];
    keskeytys_tahan();                 /* ala 0xffffffff -> yla kasvaa */
    uint32_t yla = osat[1];
    return ((uint64_t)yla << 32) | ala;
}

/* Lue yläosa ennen ja jälkeen; jos se muuttui, yritä uudelleen. */
static uint64_t lue_toistaen(unsigned *yrityksia) {
    const volatile uint32_t *osat = (const volatile uint32_t *)&tikit64;
    uint32_t yla, ala;
    *yrityksia = 0;
    do {
        yla = osat[1];
        ala = osat[0];
        if (++*yrityksia == 1) {
            keskeytys_tahan();
        }
    } while (osat[1] != yla);
    return ((uint64_t)yla << 32) | ala;
}
// @loppu repeama

static void tulosta64(const char *nimi, uint64_t arvo) {
    tulosta("%s0x%08x_%08x\n", nimi, (unsigned)(arvo >> 32),
            (unsigned)arvo);
}

int main(void) {
    konsoli_alusta();
    nvic_salli(VAPAA0_IRQn);

    // @alku main
    jaettu = 0;
    kasvata_suojaamatta();
    tulosta("suojaamatta:        %u (odotettu 101)\n", (unsigned)jaettu);
    jaettu = 0;
    kasvata_suojattuna();
    tulosta("PRIMASK:            %u\n", (unsigned)jaettu);
    jaettu = 0;
    kasvata_sisakkain();
    tulosta("sisäkkäin, sokea:   %u\n", (unsigned)jaettu);
    jaettu = 0;
    unsigned yrityksia = kasvata_ldrex();
    tulosta("LDREX/STREX:        %u, %u yritystä\n", (unsigned)jaettu,
            yrityksia);
    jaettu = 0;
    __atomic_fetch_add(&jaettu, 1, __ATOMIC_RELAXED);
    tulosta("__atomic_fetch_add: %u\n", (unsigned)jaettu);
    // @loppu main

    // @alku main64
    keskeytyksen_tyo = 1;
    tikit64 = 0xFFFFFFFFu;
    tulosta64("suojaamatta:  ", lue_suojaamatta());
    tikit64 = 0xFFFFFFFFu;
    uint64_t arvo = lue_toistaen(&yrityksia);
    tulosta64("toistaen:     ", arvo);
    tulosta("  %u yritystä\n", yrityksia);
    // @loppu main64
    return 0;
}
