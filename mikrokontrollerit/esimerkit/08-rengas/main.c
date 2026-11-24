/* Keskeytysohjattu vastaanotto: UART0:n RX-keskeytys siirtää tavut
 * rengaspuskuriin, ja pääsilmukka kokoaa niistä komentorivejä. */
#include <stdint.h>
#include <string.h>

#include "konsoli.h"
#include "mps2.h"
#include "rengas.h"

static rengas_t vastaanotto;

// @alku isr
void UART0RX_IRQHandler(void) {
    /* Kuittaus ensin: jos se tehtäisiin silmukan jälkeen, silmukan ja
     * kuittauksen välissä saapuneen tavun keskeytys katoaisi. */
    UART0->INTSTATUS = UART_INT_RX;
    while (UART0->STATE & UART_STATE_RXFULL) {
        rengas_lisaa(&vastaanotto, (uint8_t)UART0->DATA);
    }
}
// @loppu isr

// @alku hae
/* Odottaa tavua nukkuen. Tarkistus ja WFI keskeytykset kiellettyinä:
 * muuten tavu voisi tulla tarkistuksen jälkeen mutta ennen WFI:tä. */
static uint8_t hae_tavu(void) {
    uint8_t tavu;
    for (;;) {
        keskeytykset_pois();
        if (rengas_ota(&vastaanotto, &tavu)) {
            keskeytykset_paalle();
            return tavu;
        }
        odota_keskeytysta();           /* herää, vaikka PRIMASK = 1 */
        keskeytykset_paalle();         /* käsittelijä ajetaan tässä */
    }
}
// @loppu hae

// @alku komento
static int suorita(const char *rivi) {
    if (strcmp(rivi, "led 1") == 0) {
        FPGAIO->LED |= LED0;
    } else if (strcmp(rivi, "led 0") == 0) {
        FPGAIO->LED &= ~LED0;
    } else if (strcmp(rivi, "tila") == 0) {
        tulosta("LED0=%u, luettu %u tavua, ylivuotoja %u\n",
                (unsigned)(FPGAIO->LED & LED0),
                (unsigned)vastaanotto.luku,
                (unsigned)vastaanotto.ylivuotoja);
    } else if (strcmp(rivi, "loppu") == 0) {
        return 0;
    } else {
        tulosta("tuntematon komento '%s'\n", rivi);
    }
    return 1;
}
// @loppu komento

// @alku main
int main(void) {
    konsoli_alusta();
    UART0->CTRL |= UART_CTRL_RXINTEN;
    nvic_salli(UART0RX_IRQn);
    /* Tavu on voinut tulla jo ennen kuin keskeytys sallittiin, eikä
     * siitä silloin synny keskeytystä: käsittelijä kerran käsin. */
    nvic_laukaise(UART0RX_IRQn);

    char rivi[32];
    unsigned pituus = 0;
    for (;;) {
        char merkki = (char)hae_tavu();
        if (merkki == '\r') {
            continue;
        }
        if (merkki != '\n') {
            if (pituus < sizeof rivi - 1) {
                rivi[pituus++] = merkki;
            }
            continue;
        }
        rivi[pituus] = '\0';
        pituus = 0;
        tulosta("> %s\n", rivi);
        if (!suorita(rivi)) {
            return 0;
        }
    }
}
// @loppu main
