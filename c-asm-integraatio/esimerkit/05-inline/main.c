// GCC:n laajennettu inline-assembly: tulosteet, syötteet ja rajoitteet.
#include <stdio.h>

// @alku lisaa
// "+r": x on sekä syöte että tuloste rekisterissä.
// "r":  y on pelkkä syöte rekisterissä.
static inline long lisaa(long x, long y) {
#if defined(__x86_64__)
    __asm__("add %[y], %[x]" : [x] "+r"(x) : [y] "r"(y));
#else
    __asm__("add %[x], %[x], %[y]" : [x] "+r"(x) : [y] "r"(y));
#endif
    return x;
}
// @loppu lisaa

// @alku vakio
// "i": operandi on käännösaikainen vakio, joka kirjoitetaan
// käskyyn välittömänä arvona (x86: $100, RISC-V: 100).
static inline long lisaa_sata(long x) {
#if defined(__x86_64__)
    __asm__("add %1, %0" : "+r"(x) : "i"(100));
#else
    __asm__("addi %0, %0, %1" : "+r"(x) : "i"(100));
#endif
    return x;
}
// @loppu vakio

// @alku muisti
// "+m": operandi on muistissa, ja käsky lukee ja kirjoittaa sen.
// RISC-V:ssä aritmetiikka toimii vain rekistereillä, joten väliarvo
// tarvitsee oman rekisterin: "=&r" kertoo kääntäjälle, että apu
// kirjoitetaan ennen kuin kaikki syötteet on luettu.
static inline void kasvata(int *p) {
#if defined(__x86_64__)
    __asm__("incl %0" : "+m"(*p));
#else
    int apu;
    __asm__("lw %1, %0\n\t"
            "addi %1, %1, 1\n\t"
            "sw %1, %0"
            : "+m"(*p), "=&r"(apu));
#endif
}
// @loppu muisti

// @alku poisto
#if defined(__x86_64__)
#define ASETA_7 "mov $7, %0"
#else
#define ASETA_7 "li %0, 7"
#endif
// Tuloste, jota ei käytetä: ilman volatile-sanaa kääntäjä saa
// poistaa koko lauseen, volatile pakottaa sen jäämään.
__attribute__((noipa)) void ilman_volatile(void) {
    long x;
    __asm__(ASETA_7 : "=r"(x));
}
__attribute__((noipa)) void volatilen_kanssa(void) {
    long x;
    __asm__ volatile(ASETA_7 : "=r"(x));
}
// @loppu poisto

int main(void) {
    int laskuri = 41;
    kasvata(&laskuri);
    printf("lisaa(40, 2)     = %ld\n", lisaa(40, 2));
    printf("lisaa_sata(-58)  = %ld\n", lisaa_sata(-58));
    printf("kasvata(41)      = %d\n", laskuri);
    ilman_volatile();
    volatilen_kanssa();
    return 0;
}
