// Laskeva semafori rajaa, kuinka moni säie on yhtä aikaa kriittisellä
// alueella. Ylin samanaikaisuus mitataan atomisilla laskureilla.
// TSAN
#define _GNU_SOURCE
#include <pthread.h>
#include <semaphore.h>
#include <stdatomic.h>
#include <unistd.h>

#include "tarkista.h"

enum { SAIKEITA = 8, PAIKKOJA = 3, KIERROKSIA = 50 };

// @alku semafori
static sem_t paikat;
static atomic_int sisalla, enimmillaan;

static void *asiakas(void *) {
    for (int k = 0; k < KIERROKSIA; k++) {
        while (sem_wait(&paikat) == -1 && errno == EINTR) {}  // P
        int nyt = atomic_fetch_add(&sisalla, 1) + 1;
        int vanha = atomic_load(&enimmillaan);
        while (nyt > vanha &&
               !atomic_compare_exchange_weak(&enimmillaan, &vanha, nyt)) {}
        usleep(100);                     // "käytetään resurssia"
        atomic_fetch_sub(&sisalla, 1);
        sem_post(&paikat);                                   // V
    }
    return nullptr;
}
// @loppu semafori

int main(void) {
    // @alku aja
    TARKISTA(sem_init(&paikat, 0, PAIKKOJA));
    pthread_t s[SAIKEITA];
    for (int i = 0; i < SAIKEITA; i++) {
        TARKISTA_PT(pthread_create(&s[i], nullptr, asiakas, nullptr));
    }
    for (int i = 0; i < SAIKEITA; i++) {
        TARKISTA_PT(pthread_join(s[i], nullptr));
    }
    int arvo;
    TARKISTA(sem_getvalue(&paikat, &arvo));
    printf("%d säiettä, %d paikkaa: enintään %d yhtä aikaa: %s\n",
           SAIKEITA, PAIKKOJA, PAIKKOJA,
           atomic_load(&enimmillaan) <= PAIKKOJA ? "kyllä" : "EI");
    printf("semaforin arvo lopussa: %d\n", arvo);
    sem_destroy(&paikat);
    // @loppu aja
    return 0;
}
