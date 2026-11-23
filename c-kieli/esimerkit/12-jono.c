// @alku jono
#include <stdio.h>
#include <threads.h>

// Rajattu tehtäväjono (bounded buffer): tuottajat odottavat, kun jono on
// täynnä, ja kuluttajat, kun se on tyhjä. Ehtomuuttujaa odotetaan aina
// silmukassa, koska herätys voi olla aiheeton (spurious wakeup).
enum { KAPASITEETTI = 4 };

typedef struct {
    int alkiot[KAPASITEETTI];
    int alku, maara;
    bool suljettu;
    mtx_t lukko;
    cnd_t ei_taynna, ei_tyhja;
} Jono;

void jono_lisaa(Jono *j, int arvo)
{
    mtx_lock(&j->lukko);
    while (j->maara == KAPASITEETTI) {
        cnd_wait(&j->ei_taynna, &j->lukko);
    }
    j->alkiot[(j->alku + j->maara++) % KAPASITEETTI] = arvo;
    cnd_signal(&j->ei_tyhja);
    mtx_unlock(&j->lukko);
}

// Palauttaa false, kun jono on suljettu ja tyhjä.
bool jono_ota(Jono *j, int *arvo)
{
    mtx_lock(&j->lukko);
    while (j->maara == 0 && !j->suljettu) {
        cnd_wait(&j->ei_tyhja, &j->lukko);
    }
    bool saatiin = j->maara > 0;
    if (saatiin) {
        *arvo = j->alkiot[j->alku];
        j->alku = (j->alku + 1) % KAPASITEETTI;
        j->maara--;
        cnd_signal(&j->ei_taynna);
    }
    mtx_unlock(&j->lukko);
    return saatiin;
}

void jono_sulje(Jono *j)
{
    mtx_lock(&j->lukko);
    j->suljettu = true;
    cnd_broadcast(&j->ei_tyhja);   // herätetään kaikki kuluttajat
    mtx_unlock(&j->lukko);
}
// @loppu jono

// @alku kaytto
typedef struct {
    Jono *jono;
    long long summa;
    int kasitelty;
} Kuluttaja;

int kuluta(void *arg)
{
    Kuluttaja *k = arg;
    int arvo;
    while (jono_ota(k->jono, &arvo)) {
        k->summa += arvo;
        k->kasitelty++;
    }
    return 0;
}

int main(void)
{
    Jono jono = {};
    mtx_init(&jono.lukko, mtx_plain);
    cnd_init(&jono.ei_taynna);
    cnd_init(&jono.ei_tyhja);

    Kuluttaja kuluttajat[3] = {
        {.jono = &jono}, {.jono = &jono}, {.jono = &jono},
    };
    thrd_t saikeet[3];
    for (int i = 0; i < 3; ++i) {
        thrd_create(&saikeet[i], kuluta, &kuluttajat[i]);
    }
    for (int i = 1; i <= 1000; ++i) {
        jono_lisaa(&jono, i);   // tuottaja: pääsäie
    }
    jono_sulje(&jono);

    long long summa = 0;
    int kasitelty = 0;
    for (int i = 0; i < 3; ++i) {
        thrd_join(saikeet[i], nullptr);
        summa += kuluttajat[i].summa;
        kasitelty += kuluttajat[i].kasitelty;
    }
    printf("käsitelty %d tehtävää, summa %lld\n", kasitelty, summa);

    cnd_destroy(&jono.ei_tyhja);
    cnd_destroy(&jono.ei_taynna);
    mtx_destroy(&jono.lukko);
}
// @loppu kaytto
