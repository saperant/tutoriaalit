#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// @alku rajapinta
// Lokikohteen rajapinta: funktio-osoittimien taulu (vrt. Linuxin
// struct file_operations). Toteutus saa tilansa void-osoittimena.
typedef struct {
    void (*kirjoita)(void *tila, const char *rivi);
    void (*tuhoa)(void *tila);
} LokiOps;

typedef struct {
    const LokiOps *ops;   // yhteinen, muuttumaton taulu
    void *tila;           // toteutuksen oma data
} Loki;

static inline void loki_kirjoita(Loki *l, const char *rivi)
{
    l->ops->kirjoita(l->tila, rivi);
}

static inline void loki_tuhoa(Loki *l)
{
    l->ops->tuhoa(l->tila);
}
// @loppu rajapinta

// @alku konsoli
// Toteutus 1: kirjoittaa riveille etuliitteen ja tulostaa ne.
typedef struct {
    char etuliite[16];
} Konsoli;

static void konsoli_kirjoita(void *tila, const char *rivi)
{
    const Konsoli *k = tila;
    printf("[%s] %s\n", k->etuliite, rivi);
}

static void konsoli_tuhoa(void *tila)
{
    free(tila);
}

static const LokiOps KONSOLI_OPS = {konsoli_kirjoita, konsoli_tuhoa};

bool konsoli_luo(Loki *loki, const char *etuliite)
{
    Konsoli *k = malloc(sizeof *k);
    if (k == nullptr) {
        return false;
    }
    snprintf(k->etuliite, sizeof k->etuliite, "%s", etuliite);
    *loki = (Loki){.ops = &KONSOLI_OPS, .tila = k};
    return true;
}
// @loppu konsoli

// @alku laskuri
// Toteutus 2: ei tulosta mitään, vaan laskee rivit ja merkit (testeihin).
typedef struct {
    size_t rivit;
    size_t merkit;
} Laskuri;

static void laskuri_kirjoita(void *tila, const char *rivi)
{
    Laskuri *l = tila;
    l->rivit++;
    l->merkit += strlen(rivi);
}

static void laskuri_tuhoa(void *) {}   // C23: nimetön parametri

static const LokiOps LASKURI_OPS = {laskuri_kirjoita, laskuri_tuhoa};
// @loppu laskuri

// @alku kaytto
// Käyttäjä tuntee vain rajapinnan.
void kasittele_tilaus(Loki *loki, int tilausnumero)
{
    char rivi[64];
    snprintf(rivi, sizeof rivi, "tilaus %d vastaanotettu", tilausnumero);
    loki_kirjoita(loki, rivi);
    loki_kirjoita(loki, "maksu tarkistettu");
}

int main(void)
{
    Loki konsoli;
    if (!konsoli_luo(&konsoli, "kauppa")) {
        return EXIT_FAILURE;
    }
    Laskuri tilasto = {};
    Loki laskuri = {.ops = &LASKURI_OPS, .tila = &tilasto};

    Loki *kohteet[] = {&konsoli, &laskuri};
    for (size_t i = 0; i < 2; ++i) {
        kasittele_tilaus(kohteet[i], 1001);
    }
    printf("laskuri: %zu riviä, %zu merkkiä\n", tilasto.rivit,
           tilasto.merkit);

    loki_tuhoa(&konsoli);
    loki_tuhoa(&laskuri);
}
// @loppu kaytto
