// SIMD-intrinsicsit: SSE2 aina, AVX2 vain jos suoritin tukee sitä.
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>

#include "mittari.h"

#if defined(__x86_64__)
#include <immintrin.h>
#endif

// @alku skalaari
// Pistetulo, viitetoteutus.
static float piste_skalaari(const float *a, const float *b, size_t n)
{
    float s = 0;
    for (size_t i = 0; i < n; i++) {
        s += a[i] * b[i];
    }
    return s;
}
// @loppu skalaari

#if defined(__x86_64__)
// @alku sse2
// SSE2 kuuluu jokaiseen x86-64-suorittimeen: neljä float-lukua kerralla.
static float piste_sse2(const float *a, const float *b, size_t n)
{
    __m128 s = _mm_setzero_ps();
    size_t i = 0;
    for (; i + 4 <= n; i += 4) {
        __m128 x = _mm_loadu_ps(a + i);     // ei tasausvaatimusta
        __m128 y = _mm_loadu_ps(b + i);
        s = _mm_add_ps(s, _mm_mul_ps(x, y));
    }
    float osat[4];
    _mm_storeu_ps(osat, s);
    float tulos = (osat[0] + osat[1]) + (osat[2] + osat[3]);
    for (; i < n; i++) {
        tulos += a[i] * b[i];
    }
    return tulos;
}
// @loppu sse2

// @alku avx2
// Kahdeksan float-lukua kerralla. target-attribuutti kääntää vain tämän
// funktion AVX2-käskyillä; muu ohjelma toimii myös vanhemmilla
// suorittimilla, kunhan tätä kutsutaan vain tuen tarkistuksen jälkeen.
[[gnu::target("avx2")]] static float piste_avx2(const float *a,
                                                const float *b, size_t n)
{
    __m256 s = _mm256_setzero_ps();
    size_t i = 0;
    for (; i + 8 <= n; i += 8) {
        __m256 x = _mm256_loadu_ps(a + i);
        __m256 y = _mm256_loadu_ps(b + i);
        s = _mm256_add_ps(s, _mm256_mul_ps(x, y));
    }
    __m128 puolikkaat = _mm_add_ps(_mm256_castps256_ps128(s),
                                   _mm256_extractf128_ps(s, 1));
    float osat[4];
    _mm_storeu_ps(osat, puolikkaat);
    float tulos = (osat[0] + osat[1]) + (osat[2] + osat[3]);
    for (; i < n; i++) {
        tulos += a[i] * b[i];
    }
    return tulos;
}
// @loppu avx2
#endif

typedef float (*Pistetulo)(const float *, const float *, size_t);

// @alku valinta
// Valitaan paras toteutus kerran ohjelman alussa.
static Pistetulo valitse(const char **nimi)
{
#if defined(__x86_64__)
    __builtin_cpu_init();
    if (__builtin_cpu_supports("avx2")) {
        *nimi = "avx2";
        return piste_avx2;
    }
    *nimi = "sse2";
    return piste_sse2;
#else
    *nimi = "skalaari";
    return piste_skalaari;
#endif
}
// @loppu valinta

typedef struct {
    const float *a, *b;
    size_t n;
    Pistetulo f;
    float tulos;
} Tila;

static void aja(void *p)
{
    Tila *t = p;
    for (int k = 0; k < 1000; k++) {
        t->tulos = t->f(t->a, t->b, t->n);
        kayta(&t->tulos);
    }
}

int main(int argc, char **argv)
{
    enum { N = 4099 };      // ei kahdeksalla jaollinen: loppu testataan
    static float a[N], b[N];
    // Pienet kokonaisluvut: kaikki osasummat ovat tarkkoja, joten eri
    // järjestyksessä lasketut tulokset ovat samat.
    for (size_t i = 0; i < N; i++) {
        a[i] = (float)(i % 13);
        b[i] = (float)(i % 7);
    }
    const char *nimi;
    Pistetulo paras = valitse(&nimi);
    if (mittaustila(argc, argv)) {
        printf("pistetulo, %d alkiota (aika = 1000 kutsua), valittu %s\n",
               N, nimi);
        Tila t1 = {a, b, N, piste_skalaari, 0}, t2 = {a, b, N, paras, 0};
        Tilasto s1 = mittaa(aja, &t1, 21);
        Tilasto s2 = mittaa(aja, &t2, 21);
        tulosta_mittaus("skalaari", s1, 0);
        tulosta_mittaus(nimi, s2, s1.mediaani);
        return 0;
    }
    float viite = piste_skalaari(a, b, N);
    bool samat = paras(a, b, N) == viite;
#if defined(__x86_64__)
    samat = samat && piste_sse2(a, b, N) == viite;
#endif
    printf("pistetulo %.0f\n", viite);
    printf("toteutukset samaa mielta: %s\n", samat ? "kylla" : "ei");
    return 0;
}
