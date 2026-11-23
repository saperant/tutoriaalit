#include <stdatomic.h>
#include <stdio.h>
#include <threads.h>

// @alku jaettu
typedef struct {
    mtx_t lukko;
    long saldo;          // suojattu lukolla
    atomic_int tapahtumat;
} Tili;

int talleta_monesti(void *arg)
{
    Tili *tili = arg;
    for (int i = 0; i < 10'000; ++i) {
        mtx_lock(&tili->lukko);
        tili->saldo += 1;   // vain yksi säie kerrallaan
        mtx_unlock(&tili->lukko);

        atomic_fetch_add(&tili->tapahtumat, 1);   // jakamaton lisäys
    }
    return 0;
}
// @loppu jaettu

int main(void)
{
    // @alku kaytto
    Tili tili = {.saldo = 0};
    atomic_init(&tili.tapahtumat, 0);
    if (mtx_init(&tili.lukko, mtx_plain) != thrd_success) {
        return 1;
    }

    thrd_t saikeet[4];
    for (int i = 0; i < 4; ++i) {
        thrd_create(&saikeet[i], talleta_monesti, &tili);
    }
    for (int i = 0; i < 4; ++i) {
        thrd_join(saikeet[i], nullptr);
    }
    mtx_destroy(&tili.lukko);

    printf("saldo %ld, tapahtumia %d\n", tili.saldo,
           atomic_load(&tili.tapahtumat));
    // @loppu kaytto
}
