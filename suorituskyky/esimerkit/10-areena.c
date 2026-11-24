// Muistinvaraus: malloc jokaiselle solmulle vai areena.
#define _POSIX_C_SOURCE 200809L
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>

#include "mittari.h"
#include "satunnainen.h"

typedef struct Solmu {
    struct Solmu *vasen, *oikea;
    int avain;
} Solmu;

// @alku areena
// Areena varaa muistia suurina lohkoina ja jakaa sitä peräkkäin.
// Yksittäisiä olioita ei vapauteta; koko areena vapautetaan kerralla.
typedef struct Lohko {
    struct Lohko *edellinen;
    size_t kaytetty;
    alignas(max_align_t) unsigned char data[];
} Lohko;

typedef struct {
    Lohko *nykyinen;
    size_t lohkon_koko;
    size_t lohkoja;
} Areena;

enum { TASAUS = alignof(max_align_t) };

static void *areena_varaa(Areena *a, size_t koko)
{
    koko = (koko + TASAUS - 1) & ~(size_t)(TASAUS - 1);  // pyöristys ylös
    Lohko *l = a->nykyinen;
    if (l == NULL || l->kaytetty + koko > a->lohkon_koko) {
        size_t tila = koko > a->lohkon_koko ? koko : a->lohkon_koko;
        l = malloc(sizeof(Lohko) + tila);
        if (l == NULL) {
            return NULL;
        }
        l->edellinen = a->nykyinen;
        l->kaytetty = 0;
        a->nykyinen = l;
        a->lohkoja++;
    }
    void *p = l->data + l->kaytetty;
    l->kaytetty += koko;
    return p;
}

static void areena_vapauta(Areena *a)
{
    while (a->nykyinen != NULL) {
        Lohko *edellinen = a->nykyinen->edellinen;
        free(a->nykyinen);
        a->nykyinen = edellinen;
    }
    a->lohkoja = 0;
}
// @loppu areena

// @alku puu
// Varaajaa kutsutaan funktio-osoittimen kautta, jotta sama puukoodi
// toimii molemmilla. konteksti on areena tai NULL (malloc).
typedef void *(*Varaaja)(void *konteksti, size_t koko);

static void *varaa_malloc(void *konteksti, size_t koko)
{
    size_t *laskuri = konteksti;
    (*laskuri)++;
    return malloc(koko);
}

static void *varaa_areena(void *konteksti, size_t koko)
{
    return areena_varaa(konteksti, koko);
}

// Lisää avaimen binäärihakupuuhun (ei tasapainotusta).
static Solmu *lisaa(Solmu *juuri, int avain, Varaaja v, void *k)
{
    Solmu **p = &juuri;
    while (*p != NULL) {
        p = avain < (*p)->avain ? &(*p)->vasen : &(*p)->oikea;
    }
    *p = v(k, sizeof **p);
    if (*p == NULL) {
        perror("varaus");
        exit(EXIT_FAILURE);
    }
    **p = (Solmu){NULL, NULL, avain};
    return juuri;
}
// @loppu puu

static long summa(const Solmu *s)
{
    return s == NULL ? 0 : s->avain + summa(s->vasen) + summa(s->oikea);
}

static void vapauta_puu(Solmu *s)
{
    if (s != NULL) {
        vapauta_puu(s->vasen);
        vapauta_puu(s->oikea);
        free(s);
    }
}

typedef struct {
    size_t n;
    bool areena;
    long tulos;
} Tila;

static void aja(void *p)
{
    Tila *t = p;
    Satunnainen r = {5};
    Solmu *juuri = NULL;
    size_t malloceja = 0;
    Areena a = {NULL, 1 << 16, 0};
    for (size_t i = 0; i < t->n; i++) {
        int avain = (int)satunnainen_alle(&r, 1u << 30);
        juuri = t->areena ? lisaa(juuri, avain, varaa_areena, &a)
                          : lisaa(juuri, avain, varaa_malloc, &malloceja);
    }
    t->tulos = summa(juuri);
    kayta(&t->tulos);
    if (t->areena) {
        areena_vapauta(&a);
    } else {
        vapauta_puu(juuri);
    }
}

int main(int argc, char **argv)
{
    if (mittaustila(argc, argv)) {
        Tila m = {300000, false, 0}, a = {300000, true, 0};
        printf("binaarihakupuu, 300000 satunnaista avainta\n");
        Tilasto tm = mittaa(aja, &m, 5);
        Tilasto ta = mittaa(aja, &a, 5);
        tulosta_mittaus("malloc / solmu", tm, 0);
        tulosta_mittaus("areena", ta, tm.mediaani);
        return 0;
    }
    // @alku testi
    enum { N = 10000 };
    Satunnainen r = {5};
    size_t malloceja = 0;
    Areena a = {NULL, 1 << 16, 0};
    Solmu *p1 = NULL, *p2 = NULL;
    for (int i = 0; i < N; i++) {
        int avain = (int)satunnainen_alle(&r, 1000000);
        p1 = lisaa(p1, avain, varaa_malloc, &malloceja);
        p2 = lisaa(p2, avain, varaa_areena, &a);
    }
    printf("summat %ld ja %ld\n", summa(p1), summa(p2));
    printf("malloc-kutsuja %zu, areenan lohkoja %zu\n", malloceja,
           a.lohkoja);
    vapauta_puu(p1);
    areena_vapauta(&a);
    // @loppu testi
    return 0;
}
