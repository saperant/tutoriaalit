// Lukkojärjestys estää lukkiutumisen: siirto tililtä toiselle lukitsee
// aina ensin pienemmän numeron tilin, joten kehää ei voi syntyä.
// TSAN
#define _GNU_SOURCE
#include <pthread.h>

#include "tarkista.h"

enum { TILEJA = 4, SAIKEITA = 4, SIIRTOJA = 20'000 };

// @alku siirto
typedef struct {
    pthread_mutex_t lukko;
    long saldo;
} tili_t;

static tili_t tilit[TILEJA];

static void siirra(int mista, int minne, long summa) {
    if (mista == minne) {
        return;
    }
    tili_t *eka = &tilit[mista < minne ? mista : minne];
    tili_t *toka = &tilit[mista < minne ? minne : mista];
    pthread_mutex_lock(&eka->lukko);     // aina sama järjestys
    pthread_mutex_lock(&toka->lukko);
    tilit[mista].saldo -= summa;
    tilit[minne].saldo += summa;
    pthread_mutex_unlock(&toka->lukko);
    pthread_mutex_unlock(&eka->lukko);
}
// @loppu siirto

static void *pankkivirkailija(void *arg) {
    unsigned tila = (unsigned)(*(int *)arg) * 2654435761u + 1;
    for (int k = 0; k < SIIRTOJA; k++) {
        tila = tila * 1103515245u + 12345u;  // oma generaattori:
        int a = (int)(tila >> 16) % TILEJA;  // rand ei ole säieturvallinen
        tila = tila * 1103515245u + 12345u;
        int b = (int)(tila >> 16) % TILEJA;
        siirra(a, b, 1 + (long)(tila >> 28));
    }
    return nullptr;
}

int main(void) {
    for (int i = 0; i < TILEJA; i++) {
        TARKISTA_PT(pthread_mutex_init(&tilit[i].lukko, nullptr));
        tilit[i].saldo = 1000;
    }
    pthread_t s[SAIKEITA];
    int nrot[SAIKEITA];
    for (int i = 0; i < SAIKEITA; i++) {
        nrot[i] = i;
        TARKISTA_PT(pthread_create(&s[i], nullptr, pankkivirkailija,
                                   &nrot[i]));
    }
    for (int i = 0; i < SAIKEITA; i++) {
        TARKISTA_PT(pthread_join(s[i], nullptr));
    }
    long yhteensa = 0;
    for (int i = 0; i < TILEJA; i++) {
        yhteensa += tilit[i].saldo;
        pthread_mutex_destroy(&tilit[i].lukko);
    }
    printf("%d siirtoa, saldojen summa %ld\n", SAIKEITA * SIIRTOJA,
           yhteensa);
    return 0;
}
