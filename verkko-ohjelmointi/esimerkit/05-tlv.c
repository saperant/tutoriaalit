// Mittausviesti binäärisenä TLV-koodauksena ja tekstinä. Vanha
// vastaanottaja ohittaa uuden lähettäjän lisäämän kentän.
#include <stdio.h>

#include "tlv.h"

static void heksa(const char *otsikko, const uint8_t *b, size_t n) {
    printf("%s (%zu tavua):", otsikko, n);
    for (size_t i = 0; i < n; i++) {
        printf("%s%02x", i % 16 == 0 ? "\n  " : " ", b[i]);
    }
    printf("\n");
}

int main(void) {
    // @alku kaytto
    mittaus m = {.anturi = "sauna", .lampotila = 8250, .aika = 1764000000};
    uint8_t viesti[128];
    size_t n = koodaa(&m, viesti);
    heksa("binääri", viesti, n);

    char teksti[128];
    int t = snprintf(teksti, sizeof teksti,
                     "anturi=%s;lampotila=%d.%02d;aika=%u\n", m.anturi,
                     m.lampotila / 100, m.lampotila % 100, m.aika);
    printf("teksti (%d tavua): %s", t, teksti);
    // @loppu kaytto

    // @alku uusi
    // Uudempi lähettäjä lisää kentän 4 (kosteus). Vanha purkaja ohittaa
    // sen, koska pituus kertoo, montako tavua hypätään yli.
    uint8_t kosteus[2] = {0x00, 0x2a};
    size_t uusi_n = (size_t)(kentta(viesti + n, 4, kosteus, 2) - viesti);
    mittaus purettu;
    purkutulos tulos = pura(viesti, uusi_n, &purettu);
    printf("uusi kenttä mukana: %s, anturi %s, %d.%02d astetta\n",
           PURKUTULOS[tulos], purettu.anturi, purettu.lampotila / 100,
           purettu.lampotila % 100);

    viesti[0] = 2;                       // tuntematon pääversio
    printf("versio 2: %s\n", PURKUTULOS[pura(viesti, uusi_n, &purettu)]);
    // @loppu uusi
    return 0;
}
