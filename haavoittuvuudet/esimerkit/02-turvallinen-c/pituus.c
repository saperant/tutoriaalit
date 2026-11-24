/* Kehyksen purku: pituuskenttä luetaan syötteestä. Tarkoituksella
 * haavoittuva: etumerkillinen pituus läpäisee ylärajan tarkistuksen. */
#include <stdio.h>
#include <string.h>

enum { DATA_MAX = 32 };

// @alku pura
/* Kopioi kehyksen datan puskuriin. Palauttaa datan pituuden tai -1. */
static int pura(const unsigned char *kehys, size_t koko,
                unsigned char data[DATA_MAX])
{
    if (koko < 2) {
        return -1;
    }
    /* Pituus on kaksi tavua, tulkitaan etumerkillisenä. */
    int pituus = (signed char)kehys[0] * 256 + kehys[1];
#ifdef KORJATTU
    if (pituus < 0 || pituus > DATA_MAX || (size_t)pituus > koko - 2) {
#else
    if (pituus > DATA_MAX) {            /* VIRHE: negatiivinen läpäisee */
#endif
        return -1;
    }
    memcpy(data, kehys + 2, (size_t)pituus);
    return pituus;
}
// @loppu pura

int main(void)
{
    unsigned char kehys[64];
    size_t koko = fread(kehys, 1, sizeof kehys, stdin);
    unsigned char data[DATA_MAX];
    int pituus = pura(kehys, koko, data);
    if (pituus < 0) {
        printf("kehys hylätty\n");
        return 1;
    }
    printf("dataa %d tavua\n", pituus);
    return 0;
}
