// Tilauksen loppusumma senteissä ylivuoto tarkistaen (C23).
#include <stdckdint.h>
#include <stdint.h>
#include <stdio.h>

typedef struct {
    const char *tuote;
    int64_t hinta_snt;
    int64_t maara;
} Rivi;

// @alku tarkistus
// Laskee rivien summan. Palauttaa false, jos tulos ei mahdu.
static bool loppusumma(const Rivi *rivit, size_t n, int64_t *summa)
{
    int64_t s = 0;
    for (size_t i = 0; i < n; i++) {
        int64_t rivi;
        if (ckd_mul(&rivi, rivit[i].hinta_snt, rivit[i].maara) ||
            ckd_add(&s, s, rivi)) {
            return false;
        }
    }
    *summa = s;
    return true;
}
// @loppu tarkistus

int main(void)
{
    const Rivi tavallinen[] = {{"kahvi", 1295, 3}, {"maito", 189, 12}};
    const Rivi virheellinen[] = {{"kahvi", 1295, 3},
                                 {"bugi", INT64_MAX / 2, 3}};
    int64_t summa;
    if (loppusumma(tavallinen, 2, &summa)) {
        printf("%lld.%02lld e\n", (long long)(summa / 100),
               (long long)(summa % 100));
    }
    if (!loppusumma(virheellinen, 2, &summa)) {
        printf("virhe: summa ei mahdu 64 bittiin\n");
    }
    return 0;
}
