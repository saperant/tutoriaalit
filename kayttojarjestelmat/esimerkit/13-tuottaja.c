// Tuottaja–kuluttaja rajatulla puskurilla: mutex suojaa puskurin,
// kaksi ehtomuuttujaa herättää odottajat. Lopetusmerkki kertoo
// kuluttajille, ettei töitä enää tule.
// TSAN
#define _GNU_SOURCE
#include <pthread.h>

#include "tarkista.h"

// @alku jono
enum { KOKO = 8, TUOTTAJIA = 3, KULUTTAJIA = 2, TUOTTEITA = 10'000 };

typedef struct {
    int alkiot[KOKO];
    int alku, maara;
    bool suljettu;
    pthread_mutex_t lukko;
    pthread_cond_t ei_tyhja, ei_taysi;
} jono_t;

static jono_t jono = {.lukko = PTHREAD_MUTEX_INITIALIZER,
                      .ei_tyhja = PTHREAD_COND_INITIALIZER,
                      .ei_taysi = PTHREAD_COND_INITIALIZER};

static void laita(jono_t *j, int x) {
    pthread_mutex_lock(&j->lukko);
    while (j->maara == KOKO) {           // while, ei if: herätys voi
        pthread_cond_wait(&j->ei_taysi, &j->lukko);   // olla turha
    }
    j->alkiot[(j->alku + j->maara++) % KOKO] = x;
    pthread_cond_signal(&j->ei_tyhja);
    pthread_mutex_unlock(&j->lukko);
}

// Palauttaa false, kun jono on suljettu ja tyhjä.
static bool ota(jono_t *j, int *x) {
    pthread_mutex_lock(&j->lukko);
    while (j->maara == 0 && !j->suljettu) {
        pthread_cond_wait(&j->ei_tyhja, &j->lukko);
    }
    bool saatiin = j->maara > 0;
    if (saatiin) {
        *x = j->alkiot[j->alku];
        j->alku = (j->alku + 1) % KOKO;
        j->maara--;
        pthread_cond_signal(&j->ei_taysi);
    }
    pthread_mutex_unlock(&j->lukko);
    return saatiin;
}

static void sulje(jono_t *j) {
    pthread_mutex_lock(&j->lukko);
    j->suljettu = true;
    pthread_cond_broadcast(&j->ei_tyhja);    // herätetään kaikki
    pthread_mutex_unlock(&j->lukko);
}
// @loppu jono

// @alku saikeet
typedef struct {
    int nro;
    long long summa;
    int maara;
} tyo_t;

// @alku kuluttaja
static void *tuottaja(void *arg) {
    tyo_t *t = arg;
    for (int i = 1; i <= TUOTTEITA; i++) {
        laita(&jono, t->nro * TUOTTEITA + i);
    }
    return nullptr;
}

static void *kuluttaja(void *arg) {
    tyo_t *t = arg;
    for (int x; ota(&jono, &x);) {
        t->summa += x;
        t->maara++;
    }
    return nullptr;
}
// @loppu kuluttaja

int main(void) {
    pthread_t tt[TUOTTAJIA], kt[KULUTTAJIA];
    tyo_t tuot[TUOTTAJIA], kul[KULUTTAJIA];
    for (int i = 0; i < KULUTTAJIA; i++) {
        kul[i] = (tyo_t){.nro = i};
        TARKISTA_PT(pthread_create(&kt[i], nullptr, kuluttaja, &kul[i]));
    }
    for (int i = 0; i < TUOTTAJIA; i++) {
        tuot[i] = (tyo_t){.nro = i};
        TARKISTA_PT(pthread_create(&tt[i], nullptr, tuottaja, &tuot[i]));
    }
    for (int i = 0; i < TUOTTAJIA; i++) {
        TARKISTA_PT(pthread_join(tt[i], nullptr));
    }
    sulje(&jono);                        // tuottajat valmiita
    long long summa = 0;
    int maara = 0;
    for (int i = 0; i < KULUTTAJIA; i++) {
        TARKISTA_PT(pthread_join(kt[i], nullptr));
        summa += kul[i].summa;          // jako kuluttajien kesken vaihtelee,
        maara += kul[i].maara;          // summa ei
    }
    long long odotettu = 0;
    for (int t = 0; t < TUOTTAJIA; t++) {
        for (int i = 1; i <= TUOTTEITA; i++) {
            odotettu += t * TUOTTEITA + i;
        }
    }
    printf("kulutettu %d tuotetta, summa %s\n", maara,
           summa == odotettu ? "oikein" : "VÄÄRIN");
    return 0;
}
// @loppu saikeet
