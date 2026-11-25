// Tuloste ei saa riippua koneesta, joten ohjelma kertoo vain, ovatko
// tunnistustavat samaa mieltä ja antaako valittu toteutus oikean
// tuloksen. Kumpi toteutus valittiin, vaihtelee koneittain
// (ks. tarkistus.sh).
#include <stdio.h>
#include <stdlib.h>

#include "tunnistus.h"

int main(void) {
    __builtin_cpu_init();
    int oma = avx2_kaytettavissa();
    int gcc = __builtin_cpu_supports("avx2") != 0;
    printf("cpuid ja __builtin_cpu_supports samaa mieltä: %s\n",
           oma == gcc ? "kyllä" : "ei");
    if (getenv("NAYTA_AVX2")) { // tarkistus.sh:n käyttöön
        printf("AVX2 käytettävissä: %s\n", oma ? "kyllä" : "ei");
    }

    static uint8_t t[1000];
    size_t odotettu = 0;
    for (size_t i = 0; i < sizeof t; i++) {
        t[i] = (uint8_t)(i * 7 % 13);
        odotettu += t[i] == 5;
    }
    int oikein = 1;
    for (size_t n = 0; n <= sizeof t; n += 37) {
        size_t m = 0;
        for (size_t i = 0; i < n; i++) {
            m += t[i] == 5;
        }
        oikein &= laske(t, n, 5) == m;
    }
    printf("laske(1000 tavua) = %zu, odotettu %zu\n",
           laske(t, sizeof t, 5), odotettu);
    printf("kaikki pituudet oikein: %s\n", oikein ? "kyllä" : "ei");
    return !oikein;
}
