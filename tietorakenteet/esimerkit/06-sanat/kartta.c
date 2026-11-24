// kartta.c: hajautustaulu ketjutuksella. Jokainen ämpäri on linkitetty
// lista avaimista, joiden hajautusarvo osuu siihen. Kun kuormituskerroin
// (avaimia / ämpäreitä) ylittää 1, ämpäreiden määrä tuplataan ja
// avaimet jaetaan uudelleen.
#include "kartta.h"

#include <stdint.h>
#include <stdlib.h>
#include <string.h>

// @alku rakenne
typedef struct alkio {
    struct alkio *seuraava;
    uint32_t hajautus;          // tallennettu: uudelleenhajautus halpa
    long arvo;
    char avain[];               // joustava taulukkojäsen
} Alkio;

struct kartta {
    Alkio **amparit;
    size_t ampareita;           // kahden potenssi
    size_t koko;
    int uudelleenhajautuksia;
};
// @loppu rakenne

static uint32_t fnv1a(const char *s)
{
    uint32_t h = 2166136261u;
    while (*s != '\0') {
        h ^= (unsigned char)*s++;
        h *= 16777619u;
    }
    return h;
}

Kartta *kartta_luo(void)
{
    Kartta *k = calloc(1, sizeof *k);
    if (k == nullptr) {
        return nullptr;
    }
    k->ampareita = 8;
    k->amparit = calloc(k->ampareita, sizeof *k->amparit);
    if (k->amparit == nullptr) {
        free(k);
        return nullptr;
    }
    return k;
}

void kartta_tuhoa(Kartta *k)
{
    if (k == nullptr) {
        return;
    }
    for (size_t i = 0; i < k->ampareita; i++) {
        Alkio *a = k->amparit[i];
        while (a != nullptr) {
            Alkio *seuraava = a->seuraava;
            free(a);
            a = seuraava;
        }
    }
    free(k->amparit);
    free(k);
}

static Alkio *etsi(const Kartta *k, const char *avain, uint32_t h)
{
    for (Alkio *a = k->amparit[h & (k->ampareita - 1)]; a != nullptr;
         a = a->seuraava) {
        if (a->hajautus == h && strcmp(a->avain, avain) == 0) {
            return a;
        }
    }
    return nullptr;
}

// @alku uudelleen
// Tuplaa ämpärit ja siirtää alkiot. Alkioita ei kopioida eikä
// hajautusarvoa lasketa uudelleen: vain linkit vaihtuvat.
static bool uudelleenhajauta(Kartta *k)
{
    size_t uusi = 2 * k->ampareita;
    Alkio **amparit = calloc(uusi, sizeof *amparit);
    if (amparit == nullptr) {
        return false;           // vanha taulu jää voimaan
    }
    for (size_t i = 0; i < k->ampareita; i++) {
        Alkio *a = k->amparit[i];
        while (a != nullptr) {
            Alkio *seuraava = a->seuraava;
            size_t j = a->hajautus & (uusi - 1);
            a->seuraava = amparit[j];
            amparit[j] = a;
            a = seuraava;
        }
    }
    free(k->amparit);
    k->amparit = amparit;
    k->ampareita = uusi;
    k->uudelleenhajautuksia++;
    return true;
}
// @loppu uudelleen

// @alku kasvata
bool kartta_kasvata(Kartta *k, const char *avain)
{
    uint32_t h = fnv1a(avain);
    Alkio *a = etsi(k, avain, h);
    if (a != nullptr) {
        a->arvo++;
        return true;
    }
    if (k->koko + 1 > k->ampareita && !uudelleenhajauta(k)) {
        return false;
    }
    size_t pituus = strlen(avain) + 1;
    a = malloc(sizeof *a + pituus);
    if (a == nullptr) {
        return false;
    }
    memcpy(a->avain, avain, pituus);
    a->hajautus = h;
    a->arvo = 1;
    size_t i = h & (k->ampareita - 1);
    a->seuraava = k->amparit[i];        // uusi ketjun alkuun
    k->amparit[i] = a;
    k->koko++;
    return true;
}
// @loppu kasvata

long kartta_arvo(const Kartta *k, const char *avain)
{
    const Alkio *a = etsi(k, avain, fnv1a(avain));
    return a != nullptr ? a->arvo : 0;
}

size_t kartta_koko(const Kartta *k) { return k->koko; }
size_t kartta_ampareita(const Kartta *k) { return k->ampareita; }
int kartta_uudelleenhajautuksia(const Kartta *k)
{
    return k->uudelleenhajautuksia;
}

void kartta_parit(const Kartta *k, Pari *kohde)
{
    size_t n = 0;
    for (size_t i = 0; i < k->ampareita; i++) {
        for (const Alkio *a = k->amparit[i]; a != nullptr;
             a = a->seuraava) {
            kohde[n++] = (Pari){a->avain, a->arvo};
        }
    }
}
