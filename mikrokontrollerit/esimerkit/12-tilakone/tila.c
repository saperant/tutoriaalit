#include "tila.h"

// @alku suodin
int suodin_nayte(suodin_t *s, int raaka) {
    uint8_t nayte = raaka ? 1u : 0u;
    if (nayte != s->ehdokas) {
        s->ehdokas = nayte;
        s->sama = 1;
        return 0;
    }
    if (s->sama < SUOTIMEN_NAYTTEET) {
        s->sama++;
    }
    if (s->sama == SUOTIMEN_NAYTTEET && s->vakaa != nayte) {
        s->vakaa = nayte;
        return 1;
    }
    return 0;
}
// @loppu suodin

void valo_alusta(valo_t *v) {
    *v = (valo_t){.tila = POIS};
}

static void siirry(valo_t *v, valotila_t uusi, uint32_t nyt) {
    v->tila = uusi;
    v->led = (uusi != POIS);
    v->vaihdettu = nyt;
}

// @alku kasittele
int valo_kasittele(valo_t *v, tapahtuma_t t, uint32_t nyt) {
    valotila_t ennen = v->tila;
    switch (t) {
    case T_PAINETTU:
        v->pohjassa = 1;
        v->pitka_kasitelty = 0;
        v->painettu = nyt;
        break;
    case T_VAPAUTETTU:
        v->pohjassa = 0;
        if (!v->pitka_kasitelty) {            /* lyhyt painallus */
            static const valotila_t seuraava[] = {
                [POIS] = PAALLA, [PAALLA] = VILKKU, [VILKKU] = POIS};
            siirry(v, seuraava[v->tila], nyt);
        }
        break;
    case T_TIKKI:
        if (v->pohjassa && !v->pitka_kasitelty &&
            nyt - v->painettu >= PITKA_PAINALLUS_MS) {
            v->pitka_kasitelty = 1;           /* pitkä: aina pois */
            siirry(v, POIS, nyt);
        } else if (v->tila == VILKKU &&
                   nyt - v->vaihdettu >= VILKKUJAKSO_MS) {
            v->led = !v->led;
            v->vaihdettu = nyt;
        }
        break;
    }
    return v->tila != ennen;
}
// @loppu kasittele

const char *valo_nimi(valotila_t tila) {
    switch (tila) {
    case POIS:
        return "POIS";
    case PAALLA:
        return "PAALLA";
    case VILKKU:
        return "VILKKU";
    }
    return "?";
}
