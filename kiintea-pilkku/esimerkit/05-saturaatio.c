// Saturaatio ja kierto: vahvistettu signaali ylittää Q1.15:n alueen.
#include <math.h>
#include <stdint.h>
#include <stdio.h>

// @alku summaimet
// Kiertävä summa: laitteiston n-bittinen summain ilman lisälogiikkaa.
// C:ssä lasketaan leveämmässä tyypissä ja otetaan alimmat 16 bittiä.
static int16_t kierto(int32_t x)
{
    uint16_t alin = (uint16_t)x;                 // modulo 2^16
    return alin > INT16_MAX ? (int16_t)(alin - 65536)
                            : (int16_t)alin;
}

// Saturoiva: ylivuoto leikataan alueen rajaan.
static int16_t saturoi(int32_t x)
{
    if (x > INT16_MAX) {
        return INT16_MAX;
    }
    if (x < INT16_MIN) {
        return INT16_MIN;
    }
    return (int16_t)x;
}
// @loppu summaimet

int main(void)
{
    // @alku koe
    // Siniaalto amplitudilla 0,6 kerrotaan kahdella (1,2 > 1).
    double suurin_k = 0.0, suurin_s = 0.0, pahin_oikea = 0.0;
    int16_t pahin_k = 0;
    for (int i = 0; i < 64; i++) {
        int16_t x = (int16_t)lround(0.6 * 32767 * sin(i * 0.1));
        int32_t kaksi = 2 * (int32_t)x;
        double oikea = 2.0 * x / 32768.0;
        double ek = fabs(kierto(kaksi) / 32768.0 - oikea);
        double es = fabs(saturoi(kaksi) / 32768.0 - oikea);
        if (ek > suurin_k) {
            suurin_k = ek;
            pahin_k = kierto(kaksi);
            pahin_oikea = oikea;
        }
        suurin_s = es > suurin_s ? es : suurin_s;
    }
    printf("kierto:     suurin virhe %.3f (tulos %+.3f, oikea %+.3f)\n",
           suurin_k, pahin_k / 32768.0, pahin_oikea);
    printf("saturaatio: suurin virhe %.3f\n", suurin_s);
    // @loppu koe
    return 0;
}
