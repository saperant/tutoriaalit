#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

// @alku tyyppi
typedef struct {
    int32_t tunnus;
    float lampotila;
} Mittaus;
// @loppu tyyppi

int main(void)
{
    // @alku kirjoitus
    Mittaus mittaukset[] = {{1, 21.5f}, {2, 22.0f}, {3, 19.75f}};
    size_t n = sizeof mittaukset / sizeof mittaukset[0];

    FILE *f = fopen("mittaukset.bin", "wb");
    if (f == nullptr) {
        return EXIT_FAILURE;
    }
    size_t kirjoitettu = fwrite(mittaukset, sizeof mittaukset[0], n, f);
    fclose(f);
    printf("kirjoitettiin %zu mittausta\n", kirjoitettu);
    // @loppu kirjoitus

    // @alku luku
    f = fopen("mittaukset.bin", "rb");
    if (f == nullptr) {
        return EXIT_FAILURE;
    }
    fseek(f, 0, SEEK_END);
    long koko = ftell(f);
    printf("tiedoston koko %ld tavua\n", koko);

    fseek(f, 2 * (long)sizeof(Mittaus), SEEK_SET);   // kolmas mittaus
    Mittaus m;
    if (fread(&m, sizeof m, 1, f) == 1) {
        printf("mittaus %d: %.2f astetta\n", m.tunnus, m.lampotila);
    }
    fclose(f);
    remove("mittaukset.bin");
    // @loppu luku
}
