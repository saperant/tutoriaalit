// Lukijat–kirjoittajat: monta lukijaa saa olla sisällä yhtä aikaa,
// kirjoittaja vain yksin. Oma toteutus suosii kirjoittajia, jotta
// lukijavirta ei näännytä niitä.
// TSAN
#define _GNU_SOURCE
#include <pthread.h>

#include "tarkista.h"

// @alku lukko
typedef struct {
    pthread_mutex_t m;
    pthread_cond_t vuoro;
    int lukijoita;                       // sisällä olevat lukijat
    int odottavia_kirjoittajia;
    bool kirjoittaja;                    // kirjoittaja sisällä
} rw_t;

static void lue_alku(rw_t *l) {
    pthread_mutex_lock(&l->m);
    while (l->kirjoittaja || l->odottavia_kirjoittajia > 0) {
        pthread_cond_wait(&l->vuoro, &l->m);
    }
    l->lukijoita++;
    pthread_mutex_unlock(&l->m);
}

static void lue_loppu(rw_t *l) {
    pthread_mutex_lock(&l->m);
    if (--l->lukijoita == 0) {
        pthread_cond_broadcast(&l->vuoro);
    }
    pthread_mutex_unlock(&l->m);
}

static void kirjoita_alku(rw_t *l) {
    pthread_mutex_lock(&l->m);
    l->odottavia_kirjoittajia++;
    while (l->kirjoittaja || l->lukijoita > 0) {
        pthread_cond_wait(&l->vuoro, &l->m);
    }
    l->odottavia_kirjoittajia--;
    l->kirjoittaja = true;
    pthread_mutex_unlock(&l->m);
}

static void kirjoita_loppu(rw_t *l) {
    pthread_mutex_lock(&l->m);
    l->kirjoittaja = false;
    pthread_cond_broadcast(&l->vuoro);
    pthread_mutex_unlock(&l->m);
}
// @loppu lukko

// @alku testi
enum { LUKIJOITA = 4, KIRJOITTAJIA = 2, KIERROKSIA = 2000 };

// @alku saikeet
static rw_t lukko = {.m = PTHREAD_MUTEX_INITIALIZER,
                     .vuoro = PTHREAD_COND_INITIALIZER};
enum { SUMMA = 10'000 };
static long tili_a = SUMMA, tili_b = 0;  // invariantti: summa pysyy
static int rikkomuksia[LUKIJOITA];

static void *lukija(void *arg) {
    int nro = *(int *)arg;
    for (int k = 0; k < KIERROKSIA; k++) {
        lue_alku(&lukko);
        if (tili_a + tili_b != SUMMA) {
            rikkomuksia[nro]++;          // näkisi puolivalmiin siirron
        }
        lue_loppu(&lukko);
    }
    return nullptr;
}

static void *kirjoittaja(void *) {
    for (int k = 0; k < KIERROKSIA; k++) {
        kirjoita_alku(&lukko);
        tili_a -= 1;                     // välitila rikkoo invariantin
        tili_b += 1;
        kirjoita_loppu(&lukko);
    }
    return nullptr;
}
// @loppu saikeet

int main(void) {
    pthread_t l[LUKIJOITA], k[KIRJOITTAJIA];
    int nrot[LUKIJOITA];
    for (int i = 0; i < LUKIJOITA; i++) {
        nrot[i] = i;
        TARKISTA_PT(pthread_create(&l[i], nullptr, lukija, &nrot[i]));
    }
    for (int i = 0; i < KIRJOITTAJIA; i++) {
        TARKISTA_PT(pthread_create(&k[i], nullptr, kirjoittaja, nullptr));
    }
    for (int i = 0; i < LUKIJOITA; i++) {
        TARKISTA_PT(pthread_join(l[i], nullptr));
    }
    for (int i = 0; i < KIRJOITTAJIA; i++) {
        TARKISTA_PT(pthread_join(k[i], nullptr));
    }
    int yhteensa = 0;
    for (int i = 0; i < LUKIJOITA; i++) {
        yhteensa += rikkomuksia[i];
    }
    printf("lukijat näkivät rikkinäisen tilan %d kertaa\n", yhteensa);
    printf("tili_a = %ld, tili_b = %ld\n", tili_a, tili_b);
    return 0;
}
// @loppu testi
