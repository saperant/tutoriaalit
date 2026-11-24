// Ajoitushyökkäys tunnisteen vertailuun. Laite vertaa vastaanotettua
// tunnistetta (esim. MAC tai PIN) tallennettuun. Aikaa mallinnetaan
// suoritettujen vertailukierrosten määrällä: se on deterministinen ja
// verrannollinen siihen, mitä hyökkääjä mittaisi kellolla tai
// tehonkulutuksesta.
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

enum { PITUUS = 8 };

static const uint8_t SALAINEN[PITUUS] = {0x3c, 0xa1, 0x07, 0xd2,
                                         0x58, 0x9e, 0x41, 0xf0};
static unsigned long kierrokset;    // mallinnettu suoritusaika

// @alku vuotava
// Palaa heti ensimmäisestä erosta: aika kertoo, montako tavua osui.
static int vertaa_vuotava(const uint8_t *a, const uint8_t *b, size_t n) {
    for (size_t i = 0; i < n; i++) {
        kierrokset++;
        if (a[i] != b[i]) {
            return 0;
        }
    }
    return 1;
}
// @loppu vuotava

// @alku vakioaikainen
// Käy aina kaikki tavut läpi ja kerää erot yhteen: aika ei riipu
// siitä, missä kohtaa ero on.
static int vertaa_vakio(const uint8_t *a, const uint8_t *b, size_t n) {
    uint8_t ero = 0;
    for (size_t i = 0; i < n; i++) {
        kierrokset++;
        ero |= (uint8_t)(a[i] ^ b[i]);
    }
    return ero == 0;
}
// @loppu vakioaikainen

typedef int vertailu_t(const uint8_t *, const uint8_t *, size_t);

// @alku hyokkays
// Arvaa tunnisteen tavu kerrallaan: valitaan arvo, jonka tarkistus
// kesti pisimpään. Palauttaa tarvittujen yritysten määrän.
static long hyokkaa(vertailu_t *vertaa, uint8_t arvaus[PITUUS]) {
    long yrityksia = 0;
    memset(arvaus, 0, PITUUS);
    for (int kohta = 0; kohta < PITUUS; kohta++) {
        unsigned long pisin = 0;
        int paras = 0;
        for (int arvo = 0; arvo < 256; arvo++) {
            arvaus[kohta] = (uint8_t)arvo;
            kierrokset = 0;
            yrityksia++;
            if (vertaa(arvaus, SALAINEN, PITUUS)) {
                return yrityksia;
            }
            if (kierrokset > pisin) {
                pisin = kierrokset;
                paras = arvo;
            }
        }
        arvaus[kohta] = (uint8_t)paras;
    }
    return -yrityksia;   // ei onnistunut
}
// @loppu hyokkays

static void raportoi(const char *nimi, vertailu_t *vertaa) {
    uint8_t arvaus[PITUUS];
    long tulos = hyokkaa(vertaa, arvaus);
    if (tulos > 0) {
        printf("%s: tunniste löytyi %ld yrityksellä\n", nimi, tulos);
    } else {
        printf("%s: ei löytynyt %ld yrityksellä\n", nimi, -tulos);
    }
}

int main(void) {
    raportoi("Vuotava vertailu", vertaa_vuotava);
    raportoi("Vakioaikainen   ", vertaa_vakio);
    printf("Raaka arvaus vaatisi keskimäärin 2^63 yritystä\n");
    return 0;
}
