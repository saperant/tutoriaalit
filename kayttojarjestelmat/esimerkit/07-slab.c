// Slab-varaajan idea: saman kokoiset oliot varataan valmiiksi
// pilkotusta sivusta, ja vapaat paikat ketjutetaan olioiden itsensä
// läpi. Varaus ja vapautus ovat vakioaikaisia, eikä pirstoutumista synny.
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>

// @alku slab
enum { SIVU = 4096 };

// @alku tyypit
typedef union paikka {
    union paikka *seuraava;          // vapaana: linkki seuraavaan
    max_align_t tasaus;
} paikka_t;

typedef struct slab {
    struct slab *seuraava;
    paikka_t *vapaat;
    size_t kaytossa;
    alignas(max_align_t) unsigned char data[SIVU];
} slab_t;
// @loppu tyypit

typedef struct {
    size_t koko;                     // olion koko tasattuna
    slab_t *slabit;
    size_t slabeja;
} valimuisti_t;

static slab_t *uusi_slab(valimuisti_t *v) {
    slab_t *s = calloc(1, sizeof *s);
    if (s == nullptr) {
        return nullptr;
    }
    for (size_t k = 0; k + v->koko <= SIVU; k += v->koko) {
        paikka_t *p = (paikka_t *)(s->data + k);
        p->seuraava = s->vapaat;         // pino: viimeinen ensin
        s->vapaat = p;
    }
    s->seuraava = v->slabit;
    v->slabit = s;
    v->slabeja++;
    return s;
}
// @loppu slab

// @alku varaa
static void *varaa(valimuisti_t *v) {
    slab_t *s = v->slabit;
    while (s && s->vapaat == nullptr) {
        s = s->seuraava;
    }
    if (s == nullptr && (s = uusi_slab(v)) == nullptr) {
        return nullptr;
    }
    paikka_t *p = s->vapaat;
    s->vapaat = p->seuraava;
    s->kaytossa++;
    return p;
}

// Vapautettu paikka on todennäköisesti vielä välimuistissa, joten sen
// slab siirretään listan alkuun ja paikka annetaan seuraavaksi.
static void vapauta(valimuisti_t *v, void *olio) {
    for (slab_t **l = &v->slabit; *l; l = &(*l)->seuraava) {
        slab_t *s = *l;
        unsigned char *c = olio;
        if (c >= s->data && c < s->data + SIVU) {   // oma slab
            paikka_t *p = olio;
            p->seuraava = s->vapaat;
            s->vapaat = p;
            s->kaytossa--;
            *l = s->seuraava;
            s->seuraava = v->slabit;
            v->slabit = s;
            return;
        }
    }
}
// @loppu varaa

static void tuhoa(valimuisti_t *v) {
    while (v->slabit) {
        slab_t *s = v->slabit;
        v->slabit = s->seuraava;
        free(s);
    }
}

// @alku kaytto
typedef struct {                     // esimerkiksi ytimen tiedostokahva
    int kuvaaja, liput;
    long sijainti;
    char nimi[44];
} kahva_t;

int main(void) {
    const size_t tasaus = alignof(max_align_t);
    valimuisti_t v = {
        .koko = (sizeof(kahva_t) + tasaus - 1) / tasaus * tasaus};
    printf("olion koko %zu, oliota sivussa %zu\n", v.koko, SIVU / v.koko);

    kahva_t *kahvat[100];
    for (int i = 0; i < 100; i++) {
        kahvat[i] = varaa(&v);
        *kahvat[i] = (kahva_t){.kuvaaja = i};
    }
    printf("100 oliota: %zu slabia\n", v.slabeja);

    kahva_t *vanha = kahvat[42];
    vapauta(&v, vanha);
    kahvat[42] = varaa(&v);
    printf("vapautettu paikka käytetään heti uudelleen: %s\n",
           kahvat[42] == vanha ? "kyllä" : "ei");
    for (int i = 0; i < 100; i++) {
        vapauta(&v, kahvat[i]);
    }
    size_t kaytossa = 0;
    for (slab_t *s = v.slabit; s; s = s->seuraava) {
        kaytossa += s->kaytossa;
    }
    printf("kaikki vapautettu: käytössä %zu, slabit säilyvät: %zu\n",
           kaytossa, v.slabeja);
    tuhoa(&v);
    return 0;
}
// @loppu kaytto
