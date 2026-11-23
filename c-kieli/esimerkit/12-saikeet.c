#include <stdio.h>
#include <stdlib.h>
#include <threads.h>

// @alku tehtava
typedef struct {
    const int *alku;
    size_t pituus;
    long long summa;   // kukin säie kirjoittaa vain omaan tulokseensa
} Osa;

int laske_osa(void *arg)
{
    Osa *osa = arg;
    long long s = 0;
    for (size_t i = 0; i < osa->pituus; ++i) {
        s += osa->alku[i];
    }
    osa->summa = s;
    return thrd_success;
}
// @loppu tehtava

int main(void)
{
    // @alku kaytto
    enum { N = 1'000'000, SAIKEITA = 4 };
    int *luvut = malloc(N * sizeof *luvut);
    if (luvut == nullptr) {
        return EXIT_FAILURE;
    }
    for (int i = 0; i < N; ++i) {
        luvut[i] = i + 1;
    }

    thrd_t saikeet[SAIKEITA];
    Osa osat[SAIKEITA];
    size_t pala = N / SAIKEITA;
    for (int i = 0; i < SAIKEITA; ++i) {
        osat[i] = (Osa){.alku = luvut + i * pala, .pituus = pala};
        if (thrd_create(&saikeet[i], laske_osa, &osat[i]) != thrd_success) {
            return EXIT_FAILURE;
        }
    }

    long long summa = 0;
    for (int i = 0; i < SAIKEITA; ++i) {
        thrd_join(saikeet[i], nullptr);   // odotetaan säikeen loppua
        summa += osat[i].summa;
    }
    printf("summa: %lld\n", summa);
    free(luvut);
    // @loppu kaytto
}
