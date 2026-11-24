// Kaksi ensimmäistä toteutusta: selkeitä mutta hitaita.
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "loki.h"

// @alku etsi
// Etsii osoitteen taulukosta alusta alkaen: O(n) jokaiselle riville.
[[gnu::noinline]] static Asiakas *etsi_lineaarisesti(
    Asiakas *a, size_t n, const char *osoite)
{
    for (size_t i = 0; i < n; i++) {
        if (strcmp(a[i].osoite, osoite) == 0) {
            return &a[i];
        }
    }
    return NULL;
}
// @loppu etsi

// @alku sscanf
// Jäsentää rivin alun osoitteen ja lopun tavumäärän.
[[gnu::noinline]] static int jasenna_sscanf(const char *rivi,
                                            char osoite[16],
                                            unsigned long *tavut)
{
    int tila;
    if (sscanf(rivi, "%15s %*s %*s %*s %*s \"%*s %*s %*[^\"]\" %d %lu",
               osoite, &tila, tavut) != 3) {
        return -1;
    }
    return 0;
}
// @loppu sscanf

// Jos kopioi_rivi on tosi, rivi kopioidaan ensin omaan puskuriinsa.
static Yhteenveto laske(const char *loki, bool kopioi_rivi)
{
    size_t kapasiteetti = 64, n = 0;
    Asiakas *a = malloc(kapasiteetti * sizeof *a);
    if (a == NULL) {
        return (Yhteenveto){NULL, 0};
    }
    for (const char *rivi = loki; *rivi != '\0';) {
        char osoite[16];
        unsigned long tavut;
        const char *loppu = strchr(rivi, '\n');
        size_t pituus = loppu ? (size_t)(loppu - rivi) : strlen(rivi);
        // @alku kopio
        char puskuri[256];
        const char *jasennettava = rivi;
        if (kopioi_rivi && pituus < sizeof puskuri) {
            memcpy(puskuri, rivi, pituus);
            puskuri[pituus] = '\0';
            jasennettava = puskuri;
        }
        // @loppu kopio
        if (jasenna_sscanf(jasennettava, osoite, &tavut) == 0) {
            Asiakas *k = etsi_lineaarisesti(a, n, osoite);
            if (k == NULL) {
                if (n == kapasiteetti) {
                    kapasiteetti *= 2;
                    Asiakas *uusi = realloc(a, kapasiteetti * sizeof *a);
                    if (uusi == NULL) {
                        free(a);
                        return (Yhteenveto){NULL, 0};
                    }
                    a = uusi;
                }
                k = &a[n++];
                memcpy(k->osoite, osoite, sizeof k->osoite);
                k->pyynnot = 0;
                k->tavut = 0;
            }
            k->pyynnot++;
            k->tavut += tavut;
        }
        rivi = loppu ? loppu + 1 : rivi + pituus;
    }
    qsort(a, n, sizeof *a, vertaa_asiakkaat);
    return (Yhteenveto){a, n};
}

Yhteenveto laske_hidas(const char *loki)
{
    return laske(loki, false);
}

Yhteenveto laske_puskuroitu(const char *loki)
{
    return laske(loki, true);
}
