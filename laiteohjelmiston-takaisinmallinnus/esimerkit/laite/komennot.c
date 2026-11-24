/* Sarjakonsolin komennot. Komentotaulun rivillä on nimi, ohjeteksti
 * ja käsittelijä; rivit, joilla ei ole ohjetta, eivät näy ohjeessa. */
#include <stdint.h>
#include <string.h>

#include "asetukset.h"
#include "kehys.h"
#include "komennot.h"
#include "konsoli.h"
#include "loki.h"
#include "tehtavat.h"

#if defined(KORJATTU)
#define VERSIO "2.4.2"
#elif defined(VERSIO_240)
#define VERSIO "2.4.0"
#else
#define VERSIO "2.4.1"
#endif

typedef struct {
    const char *nimi;
    const char *ohje;
    int (*kasittele)(int argc, char **argv);
} komento_t;

#ifndef KORJATTU
static int huoltotila;
#endif

static int k_ohje(int argc, char **argv);

/* Etumerkitön luku annetussa kannassa (10 tai 16); virheellinen merkki
 * lopettaa luvun. */
static uint32_t luku(const char *teksti, unsigned kanta) {
    uint32_t arvo = 0;
    for (; *teksti != '\0'; teksti++) {
        char c = *teksti;
        unsigned numero;
        if (c >= '0' && c <= '9') {
            numero = (unsigned)(c - '0');
        } else if (kanta == 16 && c >= 'a' && c <= 'f') {
            numero = (unsigned)(c - 'a' + 10);
        } else {
            break;
        }
        arvo = arvo * kanta + numero;
    }
    return arvo;
}

static int k_versio(int argc, char **argv) {
    (void)argc;
    (void)argv;
    tulosta("LT-100 sovellus %s\n", VERSIO);
    return JATKA;
}

static int k_tila(int argc, char **argv) {
    (void)argc;
    (void)argv;
    const asetukset_t *a = asetukset();
    tulosta("nimi %s, sarja %s, aika %u ms, tietueita %u\n",
            laitteen_nimi(), a->sarjanumero, (unsigned)ajoaika_ms(),
            loki_maara());
    return JATKA;
}

static int k_aja(int argc, char **argv) {
    if (argc != 2) {
        return JATKA;
    }
    ajoita(luku(argv[1], 10));
    tulosta("ajettu %u ms\n", (unsigned)ajoaika_ms());
    return JATKA;
}

static int k_siirra(int argc, char **argv) {
    (void)argc;
    (void)argv;
    loki_siirra();
    return JATKA;
}

static int heksa(char merkki) {
    if (merkki >= '0' && merkki <= '9') {
        return merkki - '0';
    }
    if (merkki >= 'a' && merkki <= 'f') {
        return merkki - 'a' + 10;
    }
    return -1;
}

static int k_kehys(int argc, char **argv) {
    uint8_t kehys[80];
    size_t n = 0;
    if (argc != 2) {
        return JATKA;
    }
    for (const char *p = argv[1]; p[0] && p[1] && n < sizeof kehys;
         p += 2) {
        int a = heksa(p[0]), b = heksa(p[1]);
        if (a < 0 || b < 0) {
            break;
        }
        kehys[n++] = (uint8_t)(a << 4 | b);
    }
    tulosta("kehys %d\n", kasittele_kehys(kehys, n));
    return JATKA;
}

#ifndef KORJATTU
/* Huoltokomennot. Korjatussa versiossa niitä ei ole. */
static int k_huolto(int argc, char **argv) {
    if (argc == 2 && huoltosalasana_oikein(argv[1])) {
        huoltotila = 1;
        konsoli_kirjoita("huoltotila\n");
    }
    return JATKA;
}

static int k_lue(int argc, char **argv) {
    if (!huoltotila || argc != 3) {
        return JATKA;
    }
    const uint8_t *p = (const uint8_t *)luku(argv[1], 16);
    unsigned pituus = (unsigned)luku(argv[2], 10);
    for (unsigned i = 0; i < pituus; i++) {
        tulosta("%02x%c", p[i], (i % 16 == 15) ? '\n' : ' ');
    }
    if (pituus % 16 != 0) {
        konsoli_merkki('\n');
    }
    return JATKA;
}
#endif

static int k_sammuta(int argc, char **argv) {
    (void)argc;
    (void)argv;
    konsoli_kirjoita("sammutetaan\n");
    return LOPETA;
}

static const komento_t komennot[] = {
    {"ohje", "nayta komennot", k_ohje},
    {"versio", "nayta versio", k_versio},
    {"tila", "nayta tila", k_tila},
    {"aja", "aja <ms>: mittaa ja kirjaa", k_aja},
    {"siirra", "siirra loki kehyksina", k_siirra},
    {"kehys", "kehys <heksa>: kasittele kehys", k_kehys},
#ifndef KORJATTU
    {"huolto", NULL, k_huolto},
    {"lue", NULL, k_lue},
#endif
    {"sammuta", "sammuta laite", k_sammuta},
};

#define KOMENTOJA (sizeof komennot / sizeof komennot[0])

static int k_ohje(int argc, char **argv) {
    (void)argc;
    (void)argv;
    for (unsigned i = 0; i < KOMENTOJA; i++) {
        if (komennot[i].ohje != NULL) {
            tulosta("  %s: %s\n", komennot[i].nimi, komennot[i].ohje);
        }
    }
    return JATKA;
}

int suorita_rivi(char *rivi) {
    char *argv[4];
    int argc = 0;
    char *p = rivi;
    while (*p != '\0' && argc < 4) {
        while (*p == ' ') {
            *p++ = '\0';
        }
        if (*p == '\0') {
            break;
        }
        argv[argc++] = p;
        while (*p != '\0' && *p != ' ') {
            p++;
        }
    }
    if (argc == 0) {
        return JATKA;
    }
    for (unsigned i = 0; i < KOMENTOJA; i++) {
        if (strcmp(argv[0], komennot[i].nimi) == 0) {
            return komennot[i].kasittele(argc, argv);
        }
    }
    tulosta("tuntematon komento: %s\n", argv[0]);
    return JATKA;
}
