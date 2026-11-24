/* Konsoli UART0:n kautta: pollaava lähetys ja pieni printf.
 * Isäntäkoneella sama rajapinta on tiedostossa
 * ../isanta/konsoli_isanta.c. */
#ifndef KONSOLI_H
#define KONSOLI_H

void konsoli_alusta(void);
void konsoli_merkki(char merkki);
void konsoli_kirjoita(const char *teksti);

/* Muotoilut: %s %c %d %u %x ja leveys nollilla, esim. %08x. */
void tulosta(const char *muoto, ...);

#endif
