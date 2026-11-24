#include "jono.h"

int jono_alusta(jono_t *j, int16_t *data, size_t koko)
{
    if (j == NULL || data == NULL || koko == 0 || (koko & (koko - 1))) {
        return -1;
    }
    j->data = data;
    j->koko = koko;
    atomic_init(&j->kirjoitettu, 0);
    atomic_init(&j->luettu, 0);
    return 0;
}

size_t jono_taytto(jono_t *j)
{
    return atomic_load_explicit(&j->kirjoitettu, memory_order_acquire)
           - atomic_load_explicit(&j->luettu, memory_order_acquire);
}

// @alku kirjoita
size_t jono_kirjoita(jono_t *j, const int16_t *x, size_t n)
{
    size_t k = atomic_load_explicit(&j->kirjoitettu, memory_order_relaxed);
    size_t l = atomic_load_explicit(&j->luettu, memory_order_acquire);
    size_t tilaa = j->koko - (k - l);
    if (n > tilaa) {
        n = tilaa;                          // ylivuoto: loput hylataan
    }
    for (size_t i = 0; i < n; i++) {
        j->data[(k + i) & (j->koko - 1)] = x[i];
    }
    // release: data nakyy kuluttajalle ennen uutta indeksia.
    atomic_store_explicit(&j->kirjoitettu, k + n, memory_order_release);
    return n;
}
// @loppu kirjoita

size_t jono_lue(jono_t *j, int16_t *y, size_t n)
{
    size_t l = atomic_load_explicit(&j->luettu, memory_order_relaxed);
    size_t k = atomic_load_explicit(&j->kirjoitettu, memory_order_acquire);
    if (k - l < n) {
        return 0;
    }
    for (size_t i = 0; i < n; i++) {
        y[i] = j->data[(l + i) & (j->koko - 1)];
    }
    atomic_store_explicit(&j->luettu, l + n, memory_order_release);
    return n;
}
