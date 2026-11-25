// Tavujen laskeminen kääntäjän sisäisillä funktioilla (intrinsics):
// SSE2 x86-64:llä (aina saatavilla) ja V-laajennus RISC-V:llä.
#include "laske.h"

#if defined(__x86_64__)
// @alku sse2
#include <immintrin.h>

size_t laske_simd(const uint8_t *t, size_t n, uint8_t c) {
    const __m128i haettava = _mm_set1_epi8((char)c); // 16 kopiota c:stä
    size_t m = 0, i = 0;
    for (; i + 16 <= n; i += 16) {
        // loadu: ei vaadi 16 tavun tasausta.
        __m128i v = _mm_loadu_si128((const __m128i *)(t + i));
        __m128i yhtasuuret = _mm_cmpeq_epi8(v, haettava); // 0xFF tai 0
        // Kunkin tavun ylin bitti 16-bittiseksi maskiksi.
        unsigned maski = (unsigned)_mm_movemask_epi8(yhtasuuret);
        m += (size_t)__builtin_popcount(maski);
    }
    for (; i < n; i++) { // loput tavut yksi kerrallaan
        m += t[i] == c;
    }
    return m;
}
// @loppu sse2
#else
// @alku rvv
#include <riscv_vector.h>

size_t laske_simd(const uint8_t *t, size_t n, uint8_t c) {
    size_t m = 0;
    while (n > 0) {
        // vsetvl: montako alkiota tällä kierroksella käsitellään.
        // Silmukka ei tarvitse erillistä loppuosaa.
        size_t vl = __riscv_vsetvl_e8m1(n);
        vuint8m1_t v = __riscv_vle8_v_u8m1(t, vl);
        vbool8_t yhtasuuret = __riscv_vmseq_vx_u8m1_b8(v, c, vl);
        m += __riscv_vcpop_m_b8(yhtasuuret, vl); // maskin ykköset
        t += vl;
        n -= vl;
    }
    return m;
}
// @loppu rvv
#endif
