// Muunnokset kokonaislukujen ja liukulukujen välillä.
#include <math.h>
#include <stdint.h>
#include <stdio.h>

// @alku turvallinen
// Muuntaa liukuluvun 32-bittiseksi kokonaisluvuksi lähimpään
// pyöristäen. Palauttaa false, jos arvo on NaN tai ei mahdu: silloin
// suora muunnos (int32_t)x olisi määrittelemätön.
static bool kokonaisluvuksi(double x, int32_t *tulos)
{
    double r = rint(x);                    // tasapelit parilliseen
    if (!(r >= -2147483648.0 && r <= 2147483647.0)) {
        return false;                      // NaN ei läpäise vertailua
    }
    *tulos = (int32_t)r;
    return true;
}
// @loppu turvallinen

int main(void)
{
    // @alku tarkkuus
    // Kokonaisluvusta liukuluvuksi: suuret arvot pyöristyvät.
    int32_t i = 16777217;                  // 2^24 + 1
    int64_t j = 9007199254740993;          // 2^53 + 1
    printf("%d -> float %.1f\n", i, (double)(float)i);
    printf("%lld -> double %.1f\n", (long long)j, (double)j);
    // Liukuluvusta kokonaisluvuksi: murto-osa katkaistaan kohti nollaa.
    printf("(int)2.7 = %d, (int)-2.7 = %d\n", (int)2.7, (int)-2.7);
    // @loppu tarkkuus
    const double arvot[] = {2.5, -2.7, 3e9, NAN};
    for (int k = 0; k < 4; k++) {
        int32_t n;
        if (kokonaisluvuksi(arvot[k], &n)) {
            printf("%g -> %d\n", arvot[k], n);
        } else {
            printf("%g ei mahdu\n", arvot[k]);
        }
    }
    return 0;
}
