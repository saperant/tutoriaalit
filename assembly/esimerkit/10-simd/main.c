// Vektorisumma: skalaari- ja SIMD-toteutusten on annettava sama tulos.
#include <stdint.h>
#include <stdio.h>

int32_t summa_skalaari(const int32_t *t, size_t n);
#if defined(__x86_64__)
int32_t summa_sse2(const int32_t *t, size_t n);
int32_t summa_avx2(const int32_t *t, size_t n);
#else
int32_t summa_rvv(const int32_t *t, size_t n);
#endif

enum { N = 1024 };

int main(void) {
    static int32_t t[N];
    for (int i = 0; i < N; i++) {
        t[i] = (i * 37) % 1000 - 500;
    }
    int32_t s = summa_skalaari(t, N);
    printf("skalaari: %d\n", s);
#if defined(__x86_64__)
    printf("sse2: %s\n", summa_sse2(t, N) == s ? "sama" : "ERI");
    // AVX2 ei ole kaikissa x86-64-suorittimissa: tarkista ennen käyttöä.
    if (__builtin_cpu_supports("avx2")) {
        printf("avx2: %s\n", summa_avx2(t, N) == s ? "sama" : "ERI");
    } else {
        printf("avx2: ei tukea\n");
    }
#else
    printf("rvv: %s\n", summa_rvv(t, N) == s ? "sama" : "ERI");
    printf("rvv, 1000 alkiota: %s\n",
           summa_rvv(t, 1000) == summa_skalaari(t, 1000) ? "sama" : "ERI");
#endif
    return 0;
}
