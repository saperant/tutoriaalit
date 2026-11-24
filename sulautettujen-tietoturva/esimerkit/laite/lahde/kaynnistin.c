/* Käynnistin: ROM:ssa ajettava luottamusketjun ensimmäinen lenkki.
 * Tarkistaa laiteohjelmistokuvien allekirjoitukset ja versiot ja
 * käynnistää uusimman kelvollisen. */
#include <stdint.h>
#include <string.h>

#include "ed25519.h"
#include "julkinen_avain.h"   /* rakennuksessa generoitu */
#include "otsake.h"
#include "semihost.h"
#include "sha512.h"

#define PAIKKA_A 0x00100000u
#define PAIKKA_B 0x00180000u
#define PAIKAN_KOKO 0x00080000u
#define OTP_LASKURI 0x003F0000u
#define SCB_VTOR (*(volatile uint32_t *)0xE000ED08u)

/* Vikahyökkäysten vuoksi onnistuminen ei ole 1 eikä hylkäys 0:
 * yksittäinen bittivirhe tai ohitettu käsky ei muuta toista toiseksi. */
#define KELPAA 0x5AA5C33Cu
#define HYLATTY 0xA55A3CC3u

// @alku laskuri
/* Monotoninen laskuri OTP-muistissa: poltettujen bittien määrä.
 * OTP-bitin voi polttaa 0 -> 1 mutta ei koskaan takaisin. */
static uint32_t lue_laskuri(void) {
    uint32_t bitit = *(const volatile uint32_t *)OTP_LASKURI;
    uint32_t n = 0;
    while (bitit != 0) {
        n += bitit & 1u;
        bitit >>= 1;
    }
    return n;
}
// @loppu laskuri

// @alku tarkista
static uint32_t tarkista(uint32_t osoite, const char *nimi,
                         uint32_t laskuri) {
    const kuvan_otsake_t *o = (const kuvan_otsake_t *)osoite;
    tulosta("Paikka ");
    tulosta(nimi);
    tulosta(": ");
    if (o->taika != KUVA_TAIKA) {
        tulosta("tyhjä\n");
        return HYLATTY;
    }
    if (o->koko == 0 || o->koko > PAIKAN_KOKO - OTSAKKEEN_KOKO) {
        tulosta("virheellinen koko\n");
        return HYLATTY;
    }
    tulosta("versio ");
    tulosta_luku(o->versio);
    /* 1. Allekirjoitus otsakkeen alkuosasta. */
    if (ed25519_tarkista(o->allekirjoitus, JULKINEN_AVAIN, o,
                         ALLEKIRJOITETTU_OSA) != 0) {
        tulosta(", allekirjoitus EI kelpaa\n");
        return HYLATTY;
    }
    /* 2. Sovelluksen tiiviste vastaa allekirjoitettua. */
    uint8_t tiiviste[64];
    sha512_t s;
    sha512_alusta(&s);
    sha512_lisaa(&s, (const uint8_t *)osoite + OTSAKKEEN_KOKO, o->koko);
    sha512_valmis(&s, tiiviste);
    if (memcmp(tiiviste, o->tiiviste, sizeof tiiviste) != 0) {
        tulosta(", tiiviste EI täsmää\n");
        return HYLATTY;
    }
    /* 3. Versionpalautuksen esto. */
    if (o->versio < laskuri) {
        tulosta(", vanhempi kuin laskuri: hylätään\n");
        return HYLATTY;
    }
    tulosta(", kelpaa\n");
    return KELPAA;
}
// @loppu tarkista

// @alku hyppy
_Noreturn static void kaynnista(uint32_t osoite) {
    uint32_t vektorit = osoite + OTSAKKEEN_KOKO;
    uint32_t pino = ((const uint32_t *)vektorit)[0];
    uint32_t alku = ((const uint32_t *)vektorit)[1];
    SCB_VTOR = vektorit;             /* sovelluksen keskeytysvektorit */
    __asm__ volatile("msr msp, %0\n"
                     "bx %1\n" : : "r"(pino), "r"(alku));
    __builtin_unreachable();
}
// @loppu hyppy

// @alku paa
void kaynnistin(void) {
    uint32_t laskuri = lue_laskuri();
    tulosta("Käynnistin: OTP-laskuri ");
    tulosta_luku(laskuri);
    tulosta("\n");

    /* volatile: kääntäjä ei saa yhdistää eikä poistaa tarkistuksia. */
    volatile uint32_t a = tarkista(PAIKKA_A, "A", laskuri);
    volatile uint32_t b = tarkista(PAIKKA_B, "B", laskuri);
    const kuvan_otsake_t *oa = (const kuvan_otsake_t *)PAIKKA_A;
    const kuvan_otsake_t *ob = (const kuvan_otsake_t *)PAIKKA_B;

    uint32_t valittu = 0;
    if (a == KELPAA && (b != KELPAA || oa->versio >= ob->versio)) {
        valittu = PAIKKA_A;
    } else if (b == KELPAA) {
        valittu = PAIKKA_B;
    }
    if (valittu == 0) {
        tulosta("Ei kelvollista kuvaa: pysähdytään\n");
        lopeta(1);
    }
    /* Tuplatarkistus: ohitettu ehtolause ei riitä hyökkääjälle. */
    if ((valittu == PAIKKA_A && a != KELPAA)
        || (valittu == PAIKKA_B && b != KELPAA)) {
        lopeta(2);
    }
    const kuvan_otsake_t *o = (const kuvan_otsake_t *)valittu;
    tulosta(valittu == PAIKKA_A ? "Valitaan A" : "Valitaan B");
    if (o->versio > laskuri) {
        tulosta(", laskuri nostetaan arvoon ");
        tulosta_luku(o->versio);
    }
    tulosta("\n");
    kaynnista(valittu);
}
// @loppu paa

/* Vektoritaulu: pinon alku ja käynnistysosoite. */
extern uint32_t _pino;
__attribute__((section(".vektorit"), used))
static const void *const vektorit[2] = {&_pino, kaynnistin};
