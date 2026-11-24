/* Ed25519 Monocypherin rakennuspalikoilla. Monocypherin oma
 * crypto_eddsa_check käyttää BLAKE2b:tä; standardin Ed25519 tiiviste
 * on SHA-512, joten tiiviste lasketaan tässä ja yhtälö tarkistetaan
 * Monocypherilla. */
#include "ed25519.h"

#include "monocypher.h"
#include "sha512.h"

int ed25519_tarkista(const uint8_t allekirjoitus[64],
                     const uint8_t julkinen[32],
                     const void *viesti, size_t koko) {
    uint8_t laaja[64], h[32];
    sha512_t s;
    sha512_alusta(&s);
    sha512_lisaa(&s, allekirjoitus, 32);   /* R */
    sha512_lisaa(&s, julkinen, 32);        /* A */
    sha512_lisaa(&s, viesti, koko);        /* M */
    sha512_valmis(&s, laaja);
    crypto_eddsa_reduce(h, laaja);         /* h = SHA-512(R, A, M) mod L */
    return crypto_eddsa_check_equation(allekirjoitus, julkinen, h);
}
