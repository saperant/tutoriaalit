// Mitä kääntäjä tekee tavallisesta C:stä. tarkistus.sh purkaa
// funktiot konekielestä takaisin assemblyksi.
#include <stdio.h>

// @alku jako
// Jako vakiolla: kääntäjä korvaa hitaan jakokäskyn kertolaskulla
// "käänteisluvulla" ja siirrolla.
__attribute__((noipa)) unsigned long jaa_kymmenella(unsigned long x) {
    return x / 10;
}
// @loppu jako

// @alku musta
// Sama yhteenlasku C:nä ja inline-assemblynä. Optimoija laskee
// C-version valmiiksi, mutta asm-lause on sille musta laatikko.
static inline long lisaa_c(long a, long b) { return a + b; }

static inline long lisaa_asm(long a, long b) {
#if defined(__x86_64__)
    __asm__("add %1, %0" : "+r"(a) : "r"(b));
#else
    __asm__("add %0, %0, %1" : "+r"(a) : "r"(b));
#endif
    return a;
}

__attribute__((noipa)) long vakio_c(void) { return lisaa_c(40, 2); }
__attribute__((noipa)) long vakio_asm(void) { return lisaa_asm(40, 2); }
// @loppu musta

int main(void) {
    printf("jaa_kymmenella(4207) = %lu\n", jaa_kymmenella(4207));
    printf("vakio_c() = %ld, vakio_asm() = %ld\n", vakio_c(), vakio_asm());
    return 0;
}
