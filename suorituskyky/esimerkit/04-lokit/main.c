// Lokianalyysin pääohjelma: syötteen tuottaminen, testi ja mittaus.
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "../mittari.h"
#include "../satunnainen.h"
#include "loki.h"

int vertaa_asiakkaat(const void *a, const void *b)
{
    const Asiakas *x = a, *y = b;
    if (x->pyynnot != y->pyynnot) {
        return x->pyynnot > y->pyynnot ? -1 : 1;
    }
    return strcmp(x->osoite, y->osoite);
}

void vapauta(Yhteenveto *y)
{
    free(y->asiakkaat);
    y->asiakkaat = NULL;
    y->maara = 0;
}

// Tuottaa lokin, jossa on `rivit` riviä `osoitteita` eri asiakkaalta.
static char *tuota_loki(size_t rivit, uint32_t osoitteita)
{
    size_t koko = rivit * 96 + 1, kaytetty = 0;
    char *loki = malloc(koko);
    if (loki == NULL) {
        perror("malloc");
        exit(EXIT_FAILURE);
    }
    Satunnainen r = {2026};
    for (size_t i = 0; i < rivit; i++) {
        // Osa asiakkaista on muita aktiivisempia.
        uint32_t k = satunnainen_alle(&r, osoitteita);
        if (satunnainen_alle(&r, 4) == 0) {
            k %= 16;
        }
        uint32_t ip = 0x0A000001u + k * 7919u;
        uint32_t sivu = satunnainen_alle(&r, 500);
        uint32_t tavut = 200 + satunnainen_alle(&r, 30000);
        kaytetty += (size_t)snprintf(
            loki + kaytetty, koko - kaytetty,
            "%u.%u.%u.%u - - [24/Nov/2026:10:%02zu:%02zu +0200] "
            "\"GET /sivu/%u HTTP/1.1\" 200 %u\n",
            ip >> 24, ip >> 16 & 255, ip >> 8 & 255, ip & 255,
            i / 60 % 60, i % 60, sivu, tavut);
    }
    return loki;
}

static void tulosta(const Yhteenveto *y, size_t montako)
{
    printf("asiakkaita %zu\n", y->maara);
    for (size_t i = 0; i < montako && i < y->maara; i++) {
        printf("  %-15s %6u pyyntoa %10lu tavua\n", y->asiakkaat[i].osoite,
               y->asiakkaat[i].pyynnot,
               (unsigned long)y->asiakkaat[i].tavut);
    }
}

static bool samat(const Yhteenveto *a, const Yhteenveto *b)
{
    if (a->maara != b->maara) {
        return false;
    }
    for (size_t i = 0; i < a->maara; i++) {
        const Asiakas *x = &a->asiakkaat[i], *y = &b->asiakkaat[i];
        if (strcmp(x->osoite, y->osoite) != 0 || x->pyynnot != y->pyynnot
            || x->tavut != y->tavut) {
            return false;
        }
    }
    return true;
}

typedef struct {
    const char *loki;
    Yhteenveto (*laske)(const char *);
} Tila;

static void aja(void *p)
{
    Tila *t = p;
    Yhteenveto y = t->laske(t->loki);
    kayta(y.asiakkaat);
    vapauta(&y);
}

int main(int argc, char **argv)
{
    // Profilointia varten: --aja hidas|nopea RIVIT OSOITTEITA
    if (argc == 5 && strcmp(argv[1], "--aja") == 0) {
        char *loki = tuota_loki(strtoul(argv[3], NULL, 10),
                                (uint32_t)strtoul(argv[4], NULL, 10));
        Yhteenveto y = strcmp(argv[2], "hidas") == 0 ? laske_hidas(loki)
                       : strcmp(argv[2], "puskuroitu") == 0
                           ? laske_puskuroitu(loki)
                           : laske_nopea(loki);
        tulosta(&y, 3);
        vapauta(&y);
        free(loki);
        return 0;
    }
    if (mittaustila(argc, argv)) {
        char *loki = tuota_loki(20000, 3000);
        Tila hidas = {loki, laske_hidas};
        Tila puskuroitu = {loki, laske_puskuroitu};
        Tila nopea = {loki, laske_nopea};
        printf("lokianalyysi, 20000 rivia, 3000 asiakasta\n");
        Tilasto th = mittaa(aja, &hidas, 3);
        Tilasto tp = mittaa(aja, &puskuroitu, 5);
        Tilasto tn = mittaa(aja, &nopea, 21);
        tulosta_mittaus("hidas", th, 0);
        tulosta_mittaus("puskuroitu", tp, th.mediaani);
        tulosta_mittaus("nopea", tn, th.mediaani);
        free(loki);
        return 0;
    }
    // @alku testi
    char *loki = tuota_loki(5000, 300);
    Yhteenveto a = laske_hidas(loki);
    Yhteenveto b = laske_puskuroitu(loki);
    Yhteenveto c = laske_nopea(loki);
    tulosta(&a, 5);
    printf("toteutukset samaa mielta: %s\n",
           samat(&a, &b) && samat(&a, &c) ? "kylla" : "ei");
    // @loppu testi
    vapauta(&a);
    vapauta(&b);
    vapauta(&c);
    free(loki);
    return 0;
}
