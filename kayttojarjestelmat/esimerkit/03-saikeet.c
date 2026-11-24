// Säikeet jakavat osoiteavaruuden mutta niillä on omat pinot,
// säiekohtaiset muuttujat ja ytimen tunnisteet (TID).
// TSAN
#define _GNU_SOURCE
#include <dirent.h>
#include <pthread.h>
#include <unistd.h>

#include "tarkista.h"

enum { SAIKEITA = 4, N = 1'000'000 };

// @alku osa
typedef struct {
    const int *data;
    size_t alku, loppu;
    long long summa;                 // tulos: kukin säie omaansa
    pid_t tid;
    int paikallinen;
} osa_t;

static int data[N];
static thread_local int laskuri;     // jokaisella säikeellä oma
static pthread_barrier_t este;

static void *laske(void *arg) {
    osa_t *o = arg;
    for (size_t i = o->alku; i < o->loppu; i++) {
        o->summa += o->data[i];
        laskuri++;
    }
    o->tid = gettid();
    o->paikallinen = laskuri;
    pthread_barrier_wait(&este);     // kaikki elossa yhtä aikaa
    pthread_barrier_wait(&este);
    return o;                        // paluuarvo pthread_joinille
}
// @loppu osa

static int saikeiden_maara(void) {
    DIR *d = opendir("/proc/self/task");
    if (d == nullptr) {
        return -1;
    }
    int n = 0;
    for (struct dirent *e; (e = readdir(d)) != nullptr;) {
        n += e->d_name[0] != '.';
    }
    closedir(d);
    return n;
}

int main(void) {
    for (int i = 0; i < N; i++) {
        data[i] = i + 1;
    }
    // @alku luo
    TARKISTA_PT(pthread_barrier_init(&este, nullptr, SAIKEITA + 1));
    pthread_t saikeet[SAIKEITA];
    osa_t osat[SAIKEITA];
    for (int i = 0; i < SAIKEITA; i++) {
        osat[i] = (osa_t){.data = data, .alku = (size_t)i * N / SAIKEITA,
                          .loppu = (size_t)(i + 1) * N / SAIKEITA};
        TARKISTA_PT(pthread_create(&saikeet[i], nullptr, laske,
                                   &osat[i]));
    }
    pthread_barrier_wait(&este);
    // Testityökalut voivat lisätä omia säikeitään, siksi "vähintään".
    printf("säikeitä prosessissa vähintään %d: %s\n", SAIKEITA + 1,
           saikeiden_maara() >= SAIKEITA + 1 ? "kyllä" : "ei");
    pthread_barrier_wait(&este);

    long long yhteensa = 0;
    for (int i = 0; i < SAIKEITA; i++) {
        void *tulos;
        TARKISTA_PT(pthread_join(saikeet[i], &tulos));
        osa_t *o = tulos;
        yhteensa += o->summa;
        printf("säie %d: %d alkiota, TID %s PID\n", i, o->paikallinen,
               o->tid != getpid() ? "eri kuin" : "sama kuin");
    }
    printf("pääsäikeen laskuri: %d, TID == PID: %s\n", laskuri,
           gettid() == getpid() ? "kyllä" : "ei");
    printf("summa: %lld\n", yhteensa);
    pthread_barrier_destroy(&este);
    // @loppu luo
    return 0;
}
