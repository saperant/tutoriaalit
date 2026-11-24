// Kaksi toteutusta ja ifunc, joka valitsee niistä toisen ohjelman
// käynnistyessä.
#include <immintrin.h>

#include "tunnistus.h"

static size_t laske_perus(const uint8_t *t, size_t n, uint8_t c) {
    size_t m = 0;
    for (size_t i = 0; i < n; i++) {
        m += t[i] == c;
    }
    return m;
}

// @alku avx2
// target("avx2") sallii AVX2-käskyt vain tässä funktiossa; muu
// ohjelma käännetään perustason x86-64:lle.
__attribute__((target("avx2"))) static size_t
laske_avx2(const uint8_t *t, size_t n, uint8_t c) {
    const __m256i haettava = _mm256_set1_epi8((char)c);
    size_t m = 0, i = 0;
    for (; i + 32 <= n; i += 32) {
        __m256i v = _mm256_loadu_si256((const __m256i *)(t + i));
        __m256i yht = _mm256_cmpeq_epi8(v, haettava);
        m += (size_t)__builtin_popcount(
            (unsigned)_mm256_movemask_epi8(yht));
    }
    return m + laske_perus(t + i, n - i, c);
}
// @loppu avx2

// @alku ifunc
// Valitsija ajetaan kerran, kun dynaaminen linkkeri (tai staattisessa
// ohjelmassa käynnistyskoodi) käsittelee laske-symbolin. Se ajetaan
// ennen konstruktoreita, joten __builtin_cpu_init on kutsuttava itse.
typedef size_t laske_t(const uint8_t *, size_t, uint8_t);

static laske_t *valitse_laske(void) {
    __builtin_cpu_init();
    return __builtin_cpu_supports("avx2") ? laske_avx2 : laske_perus;
}

size_t laske(const uint8_t *t, size_t n, uint8_t c)
    __attribute__((ifunc("valitse_laske")));
// @loppu ifunc
