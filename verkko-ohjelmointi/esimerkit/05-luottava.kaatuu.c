// Virhe: purkaja luottaa viestin omaan pituuskenttään eikä vertaa sitä
// vastaanotettuun tavumäärään. Hyökkääjän 6 tavun viesti väittää
// anturin nimeksi 200 tavua, ja memcpy lukee puskurin ohi.
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// @alku virhe
static void pura_anturi(const uint8_t *b, size_t n, char *nimi) {
    (void)n;                             // VÄÄRIN: n:ää ei käytetä
    size_t pituus = (size_t)(b[2] << 8 | b[3]);
    memcpy(nimi, b + 4, pituus);         // lukee b:n lopun yli
    nimi[pituus] = '\0';
}
// @loppu virhe

int main(void) {
    const uint8_t hyokkays[] = {1, 1, 0, 200, 'a', 'b'};
    uint8_t *viesti = (uint8_t *)malloc(sizeof hyokkays);
    memcpy(viesti, hyokkays, sizeof hyokkays);
    char nimi[256];
    pura_anturi(viesti, sizeof hyokkays, nimi);
    printf("anturi: %s\n", nimi);
    free(viesti);
    return 0;
}
