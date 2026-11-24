/* TLV-jäsennin, jossa on kaksi tarkoituksellista virhettä fuzzauksen
 * löydettäväksi. KORJAUS=1 korjaa ensimmäisen, KORJAUS=2 molemmat. */
#include "tlv.h"

#include <string.h>

#ifndef KORJAUS
#define KORJAUS 0
#endif

static const char *const versiot[] = {"1.0", "1.1", "2.0", "2.1"};

// @alku nimi
static int lue_nimi(struct viesti *viesti, const uint8_t *arvo,
                    size_t pituus)
{
#if KORJAUS >= 1
    if (pituus >= sizeof viesti->nimi) {
        return -1;
    }
#endif
    memcpy(viesti->nimi, arvo, pituus);     /* VIRHE ilman korjausta */
    viesti->nimi[pituus] = '\0';
    return 0;
}
// @loppu nimi

// @alku versio
/* Versiotietue: "VERS" ja yhden tavun versionumero. */
static int lue_versio(struct viesti *viesti, const uint8_t *arvo,
                      size_t pituus)
{
    if (pituus != 5 || memcmp(arvo, "VERS", 4) != 0) {
        return -1;
    }
    size_t indeksi = arvo[4];
#if KORJAUS >= 2
    if (indeksi >= sizeof versiot / sizeof versiot[0]) {
        return -1;
    }
#endif
    viesti->versio = versiot[indeksi];      /* VIRHE ilman korjausta */
    return 0;
}
// @loppu versio

int tlv_jasenna(const uint8_t *data, size_t koko, struct viesti *viesti)
{
    memset(viesti, 0, sizeof *viesti);
    size_t kohta = 0;
    while (kohta + 2 <= koko) {
        uint8_t tyyppi = data[kohta];
        size_t pituus = data[kohta + 1];
        const uint8_t *arvo = data + kohta + 2;
        if (pituus > koko - kohta - 2) {
            return -1;
        }
        int tulos = 0;
        if (tyyppi == TLV_NIMI) {
            tulos = lue_nimi(viesti, arvo, pituus);
        } else if (tyyppi == TLV_VERSIO) {
            tulos = lue_versio(viesti, arvo, pituus);
        }
        if (tulos != 0) {
            return -1;
        }
        viesti->tietueita++;
        kohta += 2 + pituus;
    }
    return kohta == koko ? 0 : -1;
}
