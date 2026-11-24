/* Konsoli UART0:n kautta: pollaava lähetys ja vastaanotto sekä pieni
 * printf. */
#ifndef KONSOLI_H
#define KONSOLI_H

#include <stddef.h>

void konsoli_alusta(void);
void konsoli_merkki(char merkki);
void konsoli_kirjoita(const char *teksti);

/* Lukee rivin (ilman rivinvaihtoa) ja kaiuttaa sen. Palauttaa rivin
 * pituuden; liian pitkä rivi katkaistaan. */
size_t konsoli_lue_rivi(char *puskuri, size_t koko);

/* Muotoilut: %s %c %d %u %x ja leveys nollilla, esim. %08x. */
void tulosta(const char *muoto, ...);

#endif
