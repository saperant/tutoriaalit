/* Ed25519-allekirjoituksen tarkistus (RFC 8032). */
#ifndef ED25519_H
#define ED25519_H

#include <stddef.h>
#include <stdint.h>

/* Palauttaa 0, jos allekirjoitus on kelvollinen, muuten -1. */
int ed25519_tarkista(const uint8_t allekirjoitus[64],
                     const uint8_t julkinen[32],
                     const void *viesti, size_t koko);

#endif
