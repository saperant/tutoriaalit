/* PGM-kuvan (harmaasävy, P5) lukija. Tarkoituksella haavoittuva:
 * puskurin koko lasketaan int-tyypillä, joka voi ylivuotaa.
 * KORJATTU valitsee korjatun version. */
#include <stdckdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

struct kuva {
    int leveys;
    int korkeus;
    unsigned char *pikselit;
};

enum { MITTA_MAX = 1 << 16 };

// @alku varaa
static int varaa(struct kuva *kuva)
{
#ifdef KORJATTU
    constexpr size_t KOKO_MAX = 64u << 20;  /* 64 MiB */
    size_t koko;
    if (kuva->leveys <= 0 || kuva->korkeus <= 0
        || kuva->leveys > MITTA_MAX || kuva->korkeus > MITTA_MAX
        || ckd_mul(&koko, (size_t)kuva->leveys, (size_t)kuva->korkeus)
        || koko > KOKO_MAX) {
        return -1;
    }
#else
    int koko = kuva->leveys * kuva->korkeus;    /* JUURISYY */
#endif
    kuva->pikselit = malloc((size_t)koko);
    return kuva->pikselit == NULL ? -1 : 0;
}
// @loppu varaa

// @alku tayta
/* Täyttää kuvan taustavärillä rivi kerrallaan. */
static void tayta(struct kuva *kuva, unsigned char vari)
{
    for (int y = 0; y < kuva->korkeus; y++) {
        memset(kuva->pikselit + (size_t)y * (size_t)kuva->leveys, vari,
               (size_t)kuva->leveys);              /* KAATUMISKOHTA */
    }
}
// @loppu tayta

int main(void)
{
    struct kuva kuva = {0};
    if (scanf("P5 %d %d 255", &kuva.leveys, &kuva.korkeus) != 2) {
        fprintf(stderr, "virheellinen otsake\n");
        return 1;
    }
    if (varaa(&kuva) != 0) {
        fprintf(stderr, "kuva hylätty: %d x %d\n", kuva.leveys,
                kuva.korkeus);
        return 1;
    }
    tayta(&kuva, 0x80);
    printf("kuva %d x %d luettu\n", kuva.leveys, kuva.korkeus);
    free(kuva.pikselit);
    return 0;
}
