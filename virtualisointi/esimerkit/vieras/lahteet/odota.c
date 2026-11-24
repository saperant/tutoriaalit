/* Siirrettävä vieras: tulostaa A, jää odottamaan sarjaportin syötettä ja
 * kertoo, minkä merkin sai. Elävän siirron esimerkki siirtää koneen
 * odottamisen aikana toiseen QEMU-prosessiin. */
#include "laitteet.h"

static volatile uint32_t laskuri;   /* muisti, joka siirtyy mukana */

void vieras_main(void)
{
    tulosta("A: odotan syötettä\n");
    while ((inb(COM1_LSR) & 1) == 0)  /* bitti 0: dataa saatavilla */
        laskuri++;
    char merkki = (char)inb(COM1);
    char viesti[] = "B: sain merkin ?\n";
    viesti[15] = merkki;
    tulosta(viesti);
    lopeta(laskuri > 0 ? 5 : 6);
}
