/* Ajastimen ajuri käyttää vain tuotetun otsakkeen nimiä: osoitteet ja
 * bittikentät tulevat rekisterikuvauksesta, eivät käsin kirjoitetuista
 * vakioista. Rekisterit ovat tässä taulukossa, ei oikeassa laitteessa. */
#include <stdint.h>
#include <stdio.h>

#include "ajastin_regs.h"

static uint32_t rekisterit[4];

/* @alku kentta */
static uint32_t kentta(uint32_t arvo, uint32_t maski, uint32_t siirto)
{
    return (arvo << siirto) & maski;
}

static void kaynnista(uint32_t jakaja, uint32_t vertaa)
{
    rekisterit[AJASTIN_VERTAA_OFFSET / 4] =
        kentta(vertaa, AJASTIN_VERTAA_ARVO_MASK, AJASTIN_VERTAA_ARVO_SHIFT);
    rekisterit[AJASTIN_CTRL_OFFSET / 4] =
        kentta(jakaja, AJASTIN_CTRL_JAKAJA_MASK, AJASTIN_CTRL_JAKAJA_SHIFT)
        | AJASTIN_CTRL_EN_MASK | AJASTIN_CTRL_IE_MASK;
}
/* @loppu kentta */

int main(void)
{
    kaynnista(5, 1000);
    printf("CTRL   @ 0x%08X = 0x%08X\n",
           (unsigned)(AJASTIN_PERUSOSOITE + AJASTIN_CTRL_OFFSET),
           (unsigned)rekisterit[AJASTIN_CTRL_OFFSET / 4]);
    printf("VERTAA @ 0x%08X = 0x%08X\n",
           (unsigned)(AJASTIN_PERUSOSOITE + AJASTIN_VERTAA_OFFSET),
           (unsigned)rekisterit[AJASTIN_VERTAA_OFFSET / 4]);
    return 0;
}
