// kartta.h: merkkijonoavaimisen laskurikartan rajapinta.
#ifndef KARTTA_H
#define KARTTA_H

#include <stddef.h>

typedef struct kartta Kartta;

Kartta *kartta_luo(void);
void kartta_tuhoa(Kartta *k);

// Kasvattaa avaimen laskuria yhdellä; lisää avaimen tarvittaessa.
// Avain kopioidaan. Palauttaa false, jos muisti loppui.
bool kartta_kasvata(Kartta *k, const char *avain);

// Laskurin arvo tai 0, jos avainta ei ole.
long kartta_arvo(const Kartta *k, const char *avain);

size_t kartta_koko(const Kartta *k);
size_t kartta_ampareita(const Kartta *k);
int kartta_uudelleenhajautuksia(const Kartta *k);

typedef struct {
    const char *avain;      // kartan omistama; voimassa kartan ajan
    long arvo;
} Pari;

// Kopioi kaikki parit taulukkoon, jossa on tilaa kartta_koko(k)
// parille. Järjestys on määrittelemätön.
void kartta_parit(const Kartta *k, Pari *kohde);

#endif
