/* Pieni C-kirjasto, jota käytetään Pythonista ctypesillä. */
#ifndef TARKISTUS_H
#define TARKISTUS_H

#include <stddef.h>
#include <stdint.h>

/* @alku rajapinta */
/* CRC-32 (sama kuin zlib.crc32) puskurista. */
uint32_t crc32_laske(const uint8_t *data, size_t n);

/* Keskiarvo ja keskihajonta ulostuloparametreihin.
   Palauttaa 0 tai -1, jolloin errno kertoo syyn (EINVAL: n == 0). */
int tilasto_laske(const double *x, size_t n,
                  double *keskiarvo, double *hajonta);

/* Paloittainen laskenta, joka kutsuu takaisinkutsua jokaisen palan
   jälkeen. Takaisinkutsun nollasta poikkeava paluuarvo keskeyttää. */
typedef int (*edistyminen_fn)(size_t tehty, size_t yhteensa,
                              void *kayttaja);
int crc32_paloittain(const uint8_t *data, size_t n, size_t pala,
                     edistyminen_fn edistyminen, void *kayttaja,
                     uint32_t *tulos);

/* Heksamerkkijono, jonka kirjasto varaa. Kutsuja vapauttaa sen
   funktiolla heksana_vapauta, ei Pythonin eikä omalla free():llä. */
char *heksana(const uint8_t *data, size_t n);
void heksana_vapauta(char *p);
/* @loppu rajapinta */

#endif
