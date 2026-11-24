// Pyöristystavat, kun k bittiä pudotetaan pois (jako 2^k:lla).
#include <stdint.h>
#include <stdio.h>

// @alku lattia
// Aritmeettinen siirto oikealle eli katkaisu kohti -ääretöntä.
// Negatiivisen luvun >> on C:ssä toteutuksen määrittelemä; tämä muoto
// on siirrettävä, koska se siirtää vain ei-negatiivisia lukuja.
static int32_t lattia(int32_t x, int k)
{
    return x >= 0 ? x >> k : ~(~x >> k);
}
// @loppu lattia

// @alku tavat
static int32_t kohti_nollaa(int32_t x, int k)     // C:n jakolasku
{
    return x / (1 << k);
}

static int32_t lahimpaan_ylos(int32_t x, int k)   // puolikas ylöspäin
{
    return lattia(x + (1 << (k - 1)), k);
}

static int32_t lahimpaan_parilliseen(int32_t x, int k)  // konvergentti
{
    int32_t puolikas = 1 << (k - 1);
    int32_t jaannos = x & ((1 << k) - 1);         // 0 ... 2^k - 1
    int32_t q = lattia(x, k);
    if (jaannos > puolikas || (jaannos == puolikas && (q & 1))) {
        q += 1;
    }
    return q;
}
// @loppu tavat

int main(void)
{
    // @alku taulukko
    // Pudotetaan kaksi bittiä: arvot ovat neljäsosia (x / 4).
    printf("   x/4  lattia  nollaa  ylös  parill.\n");
    for (int32_t x = -10; x <= 10; x += 2) {
        printf("%6.2f  %6d  %6d  %4d  %7d\n", x / 4.0, lattia(x, 2),
               kohti_nollaa(x, 2), lahimpaan_ylos(x, 2),
               lahimpaan_parilliseen(x, 2));
    }
    // @loppu taulukko
    return 0;
}
