// Näyttää, millaisina tavuina arvot ovat muistissa.
#include <stdint.h>
#include <stdio.h>
#include <string.h>

// Tulostaa minkä tahansa olion tavut muistiosoitteiden järjestyksessä.
static void tulosta_tavut(const char *nimi, const void *olio, size_t koko)
{
    unsigned char tavut[16];
    memcpy(tavut, olio, koko);
    printf("%-22s", nimi);
    for (size_t i = 0; i < koko; i++) {
        printf(" %02x", tavut[i]);
    }
    printf("\n");
}

int main(void)
{
    // @alku arvot
    int32_t lampotila = 1000;       // 0x000003e8
    int32_t miinus_yksi = -1;
    uint16_t portti = 443;          // 0x01bb
    float paino = 0.1f;
    double hinta = 0.1;
    char teksti[] = "äö";           // UTF-8: kaksi tavua merkkiä kohden
    // @loppu arvot

    tulosta_tavut("int32_t 1000", &lampotila, sizeof lampotila);
    tulosta_tavut("int32_t -1", &miinus_yksi, sizeof miinus_yksi);
    tulosta_tavut("uint16_t 443", &portti, sizeof portti);
    tulosta_tavut("float 0.1", &paino, sizeof paino);
    tulosta_tavut("double 0.1", &hinta, sizeof hinta);
    tulosta_tavut("char[] UTF-8", teksti, sizeof teksti);
    return 0;
}
