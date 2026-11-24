// Toinen toteutus: oma jäsennin ja hajautustaulu.
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "loki.h"

// @alku jasenna
// Lukee luvun 0-255 ja siirtää osoitinta. Palauttaa -1 virheessä.
static int lue_tavu(const char **p)
{
    int arvo = 0, numeroita = 0;
    while (**p >= '0' && **p <= '9' && numeroita < 3) {
        arvo = arvo * 10 + (**p - '0');
        (*p)++;
        numeroita++;
    }
    return numeroita > 0 && arvo <= 255 ? arvo : -1;
}

// Jäsentää IPv4-osoitteen 32-bittiseksi luvuksi.
[[gnu::noinline]] static bool jasenna_osoite(const char **p,
                                             uint32_t *osoite)
{
    uint32_t tulos = 0;
    for (int i = 0; i < 4; i++) {
        int t = lue_tavu(p);
        if (t < 0 || (i < 3 && *(*p)++ != '.')) {
            return false;
        }
        tulos = tulos << 8 | (uint32_t)t;
    }
    *osoite = tulos;
    return **p == ' ';
}
// @loppu jasenna

// Rivin viimeinen kenttä on tavumäärä.
static unsigned long lue_tavut(const char *rivi, const char *loppu)
{
    const char *p = loppu;
    while (p > rivi && p[-1] != ' ') {
        p--;
    }
    unsigned long t = 0;
    for (; p < loppu && *p >= '0' && *p <= '9'; p++) {
        t = t * 10 + (unsigned long)(*p - '0');
    }
    return t;
}

// @alku hajautus
typedef struct {
    uint32_t osoite;        // 0 = tyhjä paikka (0.0.0.0 ei esiinny)
    uint32_t pyynnot;
    uint64_t tavut;
} Paikka;

typedef struct {
    Paikka *paikat;
    size_t koko;            // kahden potenssi
    size_t kaytossa;
} Taulu;

static size_t hajauta(uint32_t x)
{
    x ^= x >> 16;
    x *= 0x7feb352du;
    x ^= x >> 15;
    return x;
}

// Avoin hajautus lineaarisella kokeilulla. Täyttöaste pidetään alle
// puolessa, joten etsintä päättyy keskimäärin parin kokeilun jälkeen.
[[gnu::noinline]] static Paikka *taulu_hae(Taulu *t, uint32_t osoite)
{
    size_t i = hajauta(osoite) & (t->koko - 1);
    while (t->paikat[i].osoite != 0 && t->paikat[i].osoite != osoite) {
        i = (i + 1) & (t->koko - 1);
    }
    return &t->paikat[i];
}
// @loppu hajautus

static bool kasvata(Taulu *t)
{
    Taulu uusi = {calloc(t->koko * 2, sizeof(Paikka)), t->koko * 2,
                  t->kaytossa};
    if (uusi.paikat == NULL) {
        return false;
    }
    for (size_t i = 0; i < t->koko; i++) {
        if (t->paikat[i].osoite != 0) {
            *taulu_hae(&uusi, t->paikat[i].osoite) = t->paikat[i];
        }
    }
    free(t->paikat);
    *t = uusi;
    return true;
}

Yhteenveto laske_nopea(const char *loki)
{
    Taulu t = {calloc(1024, sizeof(Paikka)), 1024, 0};
    if (t.paikat == NULL) {
        return (Yhteenveto){NULL, 0};
    }
    for (const char *rivi = loki; *rivi != '\0';) {
        const char *loppu = strchr(rivi, '\n');
        if (loppu == NULL) {
            loppu = rivi + strlen(rivi);
        }
        const char *p = rivi;
        uint32_t osoite;
        if (jasenna_osoite(&p, &osoite) && osoite != 0) {
            Paikka *k = taulu_hae(&t, osoite);
            if (k->osoite == 0) {
                if (2 * (t.kaytossa + 1) > t.koko) {
                    if (!kasvata(&t)) {
                        free(t.paikat);
                        return (Yhteenveto){NULL, 0};
                    }
                    k = taulu_hae(&t, osoite);
                }
                k->osoite = osoite;
                t.kaytossa++;
            }
            k->pyynnot++;
            k->tavut += lue_tavut(rivi, loppu);
        }
        rivi = *loppu ? loppu + 1 : loppu;
    }
    Asiakas *a = malloc((t.kaytossa ? t.kaytossa : 1) * sizeof *a);
    size_t n = 0;
    for (size_t i = 0; a != NULL && i < t.koko; i++) {
        Paikka *k = &t.paikat[i];
        if (k->osoite != 0) {
            snprintf(a[n].osoite, sizeof a[n].osoite, "%u.%u.%u.%u",
                     k->osoite >> 24, k->osoite >> 16 & 255,
                     k->osoite >> 8 & 255, k->osoite & 255);
            a[n].pyynnot = k->pyynnot;
            a[n].tavut = k->tavut;
            n++;
        }
    }
    free(t.paikat);
    if (a != NULL) {
        qsort(a, n, sizeof *a, vertaa_asiakkaat);
    }
    return (Yhteenveto){a, n};
}
