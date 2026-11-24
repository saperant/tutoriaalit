// Kaksi säiettä lukitsee kaksi mutexia eri järjestyksessä. Este
// varmistaa, että kumpikin ehtii ottaa ensimmäisen lukkonsa, joten
// lukkiutuma syntyy joka kerta. Aikarajallinen lukitus paljastaa sen.
#define _GNU_SOURCE
#include <pthread.h>
#include <time.h>

#include "tarkista.h"

// @alku ristikkain
static pthread_mutex_t a = PTHREAD_MUTEX_INITIALIZER;
static pthread_mutex_t b = PTHREAD_MUTEX_INITIALIZER;
static pthread_barrier_t este;
static int tulokset[2];

static void *saie(void *arg) {
    int nro = *(int *)arg;
    pthread_mutex_t *eka = nro == 0 ? &a : &b;
    pthread_mutex_t *toka = nro == 0 ? &b : &a;
    pthread_mutex_lock(eka);
    pthread_barrier_wait(&este);         // molemmat pitävät yhtä lukkoa
    struct timespec raja;
    clock_gettime(CLOCK_REALTIME, &raja);
    raja.tv_nsec += 100'000'000;         // 100 ms
    if (raja.tv_nsec >= 1'000'000'000) {
        raja.tv_sec++;
        raja.tv_nsec -= 1'000'000'000;
    }
    tulokset[nro] = pthread_mutex_timedlock(toka, &raja);
    if (tulokset[nro] == 0) {
        pthread_mutex_unlock(toka);
    }
    pthread_barrier_wait(&este);         // kumpikin luovuttaa vasta nyt
    pthread_mutex_unlock(eka);
    return nullptr;
}
// @loppu ristikkain

int main(void) {
    // @alku aja
    TARKISTA_PT(pthread_barrier_init(&este, nullptr, 2));
    pthread_t s[2];
    int nrot[2] = {0, 1};
    for (int i = 0; i < 2; i++) {
        TARKISTA_PT(pthread_create(&s[i], nullptr, saie, &nrot[i]));
    }
    for (int i = 0; i < 2; i++) {
        TARKISTA_PT(pthread_join(s[i], nullptr));
    }
    for (int i = 0; i < 2; i++) {
        printf("säie %d: toinen lukko %s\n", i,
               tulokset[i] == ETIMEDOUT ? "ETIMEDOUT (lukkiutuma)"
                                        : "saatiin");
    }
    pthread_barrier_destroy(&este);
    // @loppu aja

    // @alku tarkistava
    pthread_mutexattr_t ominaisuudet;
    pthread_mutexattr_init(&ominaisuudet);
    pthread_mutexattr_settype(&ominaisuudet, PTHREAD_MUTEX_ERRORCHECK);
    pthread_mutex_t m;
    TARKISTA_PT(pthread_mutex_init(&m, &ominaisuudet));
    pthread_mutexattr_destroy(&ominaisuudet);
    TARKISTA_PT(pthread_mutex_lock(&m));
    int r = pthread_mutex_lock(&m);      // sama säie toisen kerran
    printf("ERRORCHECK-mutex uudelleen: %s\n", strerrorname_np(r));
    TARKISTA_PT(pthread_mutex_unlock(&m));
    r = pthread_mutex_unlock(&m);        // ei ole lukittuna
    printf("vapautus ilman lukitusta: %s\n", strerrorname_np(r));
    pthread_mutex_destroy(&m);
    // @loppu tarkistava
    return 0;
}
