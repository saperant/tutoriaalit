// Yhden tuottajan ja yhden kuluttajan rengasjono (esim. keskeytys ja
// kasittelysaie). Indeksit kasvavat vapaasti; koko on kahden potenssi.
#pragma once
#include <stdatomic.h>
#include <stddef.h>
#include <stdint.h>

// @alku jono
typedef struct {
    int16_t *data;
    size_t koko;                    // kahden potenssi
    atomic_size_t kirjoitettu;      // vain tuottaja kirjoittaa
    atomic_size_t luettu;           // vain kuluttaja kirjoittaa
} jono_t;
// @loppu jono

int jono_alusta(jono_t *j, int16_t *data, size_t koko);
size_t jono_taytto(jono_t *j);
// Kirjoittaa enintaan n naytetta ja palauttaa kirjoitettujen maaran.
size_t jono_kirjoita(jono_t *j, const int16_t *x, size_t n);
// Lukee tasan n naytetta, jos niita on; muuten ei mitaan. Palauttaa n
// tai 0.
size_t jono_lue(jono_t *j, int16_t *y, size_t n);
