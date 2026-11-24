// Kontekstinvaihtojen laskeminen getrusagella: vapaaehtoinen vaihto
// syntyy, kun säie odottaa, tahaton, kun vuorontaja keskeyttää sen.
// TSAN
#define _GNU_SOURCE
#include <pthread.h>
#include <sched.h>
#include <sys/resource.h>
#include <time.h>
#include <unistd.h>

#include "tarkista.h"

// @alku vaihdot
static void vaihdot(long *vapaaehtoiset, long *tahattomat) {
    struct rusage r;
    TARKISTA(getrusage(RUSAGE_THREAD, &r));
    *vapaaehtoiset = r.ru_nvcsw;
    *tahattomat = r.ru_nivcsw;
}

static double sekunnit(void) {
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return (double)t.tv_sec + (double)t.tv_nsec / 1e9;
}

// Pyörii 0,3 s samalla suorittimella toisen säikeen kanssa.
static void *pyori(void *arg) {
    cpu_set_t *joukko = arg;
    TARKISTA_PT(pthread_setaffinity_np(pthread_self(),
                                       sizeof *joukko, joukko));
    long v0, t0, v1, t1;
    vaihdot(&v0, &t0);
    for (double alku = sekunnit(); sekunnit() - alku < 0.3;) {}
    vaihdot(&v1, &t1);
    return (void *)(t1 - t0);
}
// @loppu vaihdot

int main(void) {
    // @alku odotus
    long v0, t0, v1, t1;
    vaihdot(&v0, &t0);
    for (int i = 0; i < 20; i++) {
        usleep(1000);                // nukkuminen luovuttaa suorittimen
    }
    vaihdot(&v1, &t1);
    printf("20 x usleep: vähintään 20 vapaaehtoista vaihtoa: %s\n",
           v1 - v0 >= 20 ? "kyllä" : "ei");
    // @loppu odotus

    // @alku kilpailu
    cpu_set_t sallitut, yksi;
    TARKISTA(sched_getaffinity(0, sizeof sallitut, &sallitut));
    CPU_ZERO(&yksi);
    for (int c = 0; c < CPU_SETSIZE; c++) {
        if (CPU_ISSET(c, &sallitut)) {
            CPU_SET(c, &yksi);       // ensimmäinen sallittu suoritin
            break;
        }
    }
    pthread_t s[2];
    for (int i = 0; i < 2; i++) {
        TARKISTA_PT(pthread_create(&s[i], nullptr, pyori, &yksi));
    }
    for (int i = 0; i < 2; i++) {
        void *tahattomia;
        TARKISTA_PT(pthread_join(s[i], &tahattomia));
        printf("säie %d: tahattomia vaihtoja yli nolla: %s\n", i,
               (long)tahattomia > 0 ? "kyllä" : "ei");
    }
    // @loppu kilpailu
    return 0;
}
