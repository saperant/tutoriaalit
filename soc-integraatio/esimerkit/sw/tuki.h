/* Tukikirjasto: UART-tulostus, lopetus ja ansojen käsittely. */
#ifndef TUKI_H
#define TUKI_H

#include <stdint.h>

void tulosta(const char *teksti);
void tulosta_hex(uint32_t arvo);
void tulosta_luku(uint32_t arvo);
_Noreturn void lopeta(int koodi);

/* Ansan käsittely: start.S kutsuu funktiota ansa(), joka jakaa
 * keskeytykset ja poikkeukset alla oleville funktioille. Ohjelma voi
 * määritellä ne itse; oletustoteutukset ovat heikkoja symboleita. */
void ajastin_keskeytys(void);
void ulkoinen_keskeytys(void);
uint32_t poikkeus(uint32_t syy, uint32_t mepc, uint32_t mtval);

#endif
