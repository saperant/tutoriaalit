/*
 * Ajastimen ajuri PeakRDL:n tuottamalla otsakkeella. Rekisterit ovat
 * tassa tavallisessa muistissa, jotta ajurin voi testata isantakoneella;
 * laitteessa osoitin asetettaisiin perusosoitteeseen.
 */

#include <stddef.h>
#include <stdint.h>
#include <stdio.h>

#include "ajastin.h"

/* Rakenteen asettelu vastaa kuvauksen osoitteita. Jos joku muuttaa
 * kuvausta ja otsake tuotetaan uudelleen, tama tarkistus kertoo, mihin
 * kohtaan ajurin oletukset menivat rikki. */
static_assert(offsetof(ajastin_t, STATUS) == 0x04, "STATUS siirtyi");
static_assert(offsetof(ajastin_t, VERTAA) == 0x0C, "VERTAA siirtyi");

// @alku kentta
/* Kentan arvo rekisteriarvoon otsakkeen bittisijainnilla ja maskilla. */
#define KENTTA(nimi, arvo) \
    (((uint32_t)(arvo) << AJASTIN__##nimi##_bp) & AJASTIN__##nimi##_bm)

static void kaynnista(volatile ajastin_t *ajastin, uint8_t jakaja,
                      uint16_t vertaa)
{
    ajastin->VERTAA = KENTTA(VERTAA__ARVO, vertaa);
    ajastin->STATUS = AJASTIN__STATUS__VALMIS_bm;   /* kuittaa vanha */
    ajastin->CTRL = KENTTA(CTRL__EN, 1) | KENTTA(CTRL__IE, 1)
                    | KENTTA(CTRL__JAKAJA, jakaja);
}
// @loppu kentta

static unsigned jakaja(const volatile ajastin_t *ajastin)
{
    return (ajastin->CTRL & AJASTIN__CTRL__JAKAJA_bm)
           >> AJASTIN__CTRL__JAKAJA_bp;
}

int main(void)
{
    ajastin_t muisti = {
        .CTRL = AJASTIN__CTRL__JAKAJA_reset << AJASTIN__CTRL__JAKAJA_bp,
        .VERTAA = AJASTIN__VERTAA__ARVO_reset,
    };
    volatile ajastin_t *ajastin = &muisti;

    printf("koko 0x%zx, nollauksen jalkeen CTRL=0x%08x jakaja=%u\n",
           sizeof(ajastin_t), (unsigned)ajastin->CTRL, jakaja(ajastin));
    kaynnista(ajastin, 5, 1000);
    printf("kaynnistyksen jalkeen CTRL=0x%08x jakaja=%u VERTAA=%u\n",
           (unsigned)ajastin->CTRL, jakaja(ajastin),
           (unsigned)ajastin->VERTAA);
    return 0;
}
