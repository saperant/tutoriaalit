/* Muistiin kuvatut rekisterit: LEDit, volatile ja bittialueet. */
#include <stdint.h>

#include "konsoli.h"
#include "mps2.h"

// @alku makrot
/* Sama rekisteri ilman rakennetta: osoite makrona. */
#define FPGAIO_LED (*(volatile uint32_t *)0x40028000u)
// @loppu makrot

// @alku bittialue
/* Cortex-M3:n bit-band: oheislaitealueen 0x40000000..0x400FFFFF
 * jokaisella bitillä on oma sananosoitteensa alueella 0x42000000. */
static volatile uint32_t *bitti(volatile void *rekisteri, unsigned n) {
    uint32_t siirtyma = (uint32_t)rekisteri - 0x40000000u;
    return (volatile uint32_t *)(0x42000000u + siirtyma * 32u + n * 4u);
}
// @loppu bittialue

static void ledit(const char *mita) {
    uint32_t arvo = FPGAIO->LED;
    tulosta("%s: LED1=%u LED0=%u\n", mita, (unsigned)((arvo >> 1) & 1u),
            (unsigned)(arvo & 1u));
}

// @alku ilman-volatilea
/* VIRHE: osoitin ilman volatilea. Kääntäjä saa olettaa, ettei kukaan
 * muu lue muistia, ja jättää ensimmäisen kirjoituksen pois. */
static void kirjoita_ilman_volatilea(void) {
    uint32_t *data = (uint32_t *)&UART0->DATA;
    *data = 'A';
    *data = 'B';
}
// @loppu ilman-volatilea

static void kirjoita_volatilella(void) {
    volatile uint32_t *data = &UART0->DATA;
    *data = 'A';
    *data = 'B';
}

int main(void) {
    konsoli_alusta();
    // @alku rmw
    FPGAIO->LED = 0;                   /* kirjoitus: kaikki pois */
    ledit("alku");
    FPGAIO->LED |= LED1;               /* lue, muuta, kirjoita */
    ledit("LED1 päälle");
    FPGAIO->LED ^= LED0 | LED1;        /* vaihda molemmat */
    ledit("vaihto");
    FPGAIO->LED &= ~LED0;              /* nollaa yksi bitti */
    ledit("LED0 pois");
    FPGAIO_LED = LED0 | LED1;          /* makron kautta */
    ledit("makro");
    // @loppu rmw

    // @alku bittialue-kaytto
    *bitti(&FPGAIO->LED, 1) = 0;       /* yksi kirjoitus, ei lukua */
    ledit("bit-band");
    tulosta("bit-band-osoite LED1:lle 0x%08x\n",
            (unsigned)bitti(&FPGAIO->LED, 1));
    // @loppu bittialue-kaytto

    // @alku volatile-koe
    tulosta("ilman volatilea: ");
    kirjoita_ilman_volatilea();
    tulosta("\nvolatilella:     ");
    kirjoita_volatilella();
    tulosta("\n");
    // @loppu volatile-koe
    return 0;
}
