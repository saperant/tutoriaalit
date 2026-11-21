// pino.h: kokonaislukupinon julkinen rajapinta.
#ifndef PINO_H
#define PINO_H

#include <stddef.h>

// Epätäydellinen tyyppi: käyttäjä näkee vain nimen, ei kenttiä.
typedef struct pino Pino;

Pino *pino_luo(void);
void pino_tuhoa(Pino *p);
bool pino_lisaa(Pino *p, int arvo);
bool pino_ota(Pino *p, int *arvo);
size_t pino_koko(const Pino *p);

#endif
