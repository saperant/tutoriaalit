// Avoin osoitteistus: kaikki avaimet ovat itse taulukossa. Törmäyksessä
// kokeillaan seuraavaa paikkaa (lineaarinen kokeilu). Poistettu paikka
// merkitään hautakiveksi, jotta hakuketju ei katkea.
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#include "satunnainen.h"

// @alku rakenne
typedef enum : uint8_t { TYHJA, KAYTOSSA, HAUTAKIVI } Tila;

typedef struct {
    uint32_t *avaimet;
    Tila *tilat;
    uint32_t kapasiteetti;      // kahden potenssi: 2^bitit
    unsigned bitit;
    uint32_t koko;              // käytössä olevat
    uint32_t hautakivia;
    long kokeiluja;             // mittausta varten
} Taulu;

// Fibonacci-hajautus: kertolasku kultaisen leikkauksen vakiolla ja
// ylimmät bitit indeksiksi. Peräkkäisetkin avaimet hajaantuvat.
static uint32_t paikka(const Taulu *t, uint32_t avain)
{
    return (uint32_t)((avain * 2654435769u) >> (32 - t->bitit));
}
// @loppu rakenne

static bool taulu_alusta(Taulu *t, uint32_t kapasiteetti)
{
    *t = (Taulu){.kapasiteetti = kapasiteetti};
    while ((1u << t->bitit) < kapasiteetti) {
        t->bitit++;
    }
    t->avaimet = malloc(kapasiteetti * sizeof *t->avaimet);
    t->tilat = calloc(kapasiteetti, sizeof *t->tilat);   // kaikki TYHJA
    if (t->avaimet == nullptr || t->tilat == nullptr) {
        free(t->avaimet);
        free(t->tilat);
        return false;
    }
    return true;
}

static void taulu_vapauta(Taulu *t)
{
    free(t->avaimet);
    free(t->tilat);
}

// @alku haku
// Palauttaa avaimen paikan tai -1. Hautakivien yli jatketaan; vain
// tyhjä paikka lopettaa haun.
static long taulu_etsi(Taulu *t, uint32_t avain)
{
    uint32_t maski = t->kapasiteetti - 1;
    for (uint32_t i = paikka(t, avain);; i = (i + 1) & maski) {
        t->kokeiluja++;
        if (t->tilat[i] == TYHJA) {
            return -1;
        }
        if (t->tilat[i] == KAYTOSSA && t->avaimet[i] == avain) {
            return i;
        }
    }
}
// @loppu haku

static bool taulu_lisaa(Taulu *t, uint32_t avain);

// @alku kasvu
// Kun käytössä olevat ja hautakivet täyttävät 3/4, taulu rakennetaan
// uudelleen (tarvittaessa suurempana). Hautakivet katoavat samalla.
static bool rakenna_uudelleen(Taulu *t)
{
    Taulu vanha = *t;
    uint32_t uusi = vanha.koko * 2 >= vanha.kapasiteetti
                    ? 2 * vanha.kapasiteetti : vanha.kapasiteetti;
    if (!taulu_alusta(t, uusi)) {
        *t = vanha;
        return false;
    }
    for (uint32_t i = 0; i < vanha.kapasiteetti; i++) {
        if (vanha.tilat[i] == KAYTOSSA) {
            taulu_lisaa(t, vanha.avaimet[i]);
        }
    }
    t->kokeiluja = vanha.kokeiluja;
    taulu_vapauta(&vanha);
    return true;
}

static bool taulu_lisaa(Taulu *t, uint32_t avain)
{
    if (4 * (t->koko + t->hautakivia + 1) > 3 * t->kapasiteetti
        && !rakenna_uudelleen(t)) {
        return false;
    }
    if (taulu_etsi(t, avain) >= 0) {
        return true;                    // oli jo
    }
    uint32_t maski = t->kapasiteetti - 1;
    uint32_t i = paikka(t, avain);
    while (t->tilat[i] == KAYTOSSA) {   // ensimmäinen vapaa tai
        i = (i + 1) & maski;            // hautakivi kelpaa
    }
    t->hautakivia -= t->tilat[i] == HAUTAKIVI;
    t->tilat[i] = KAYTOSSA;
    t->avaimet[i] = avain;
    t->koko++;
    return true;
}

static void taulu_poista(Taulu *t, uint32_t avain)
{
    long i = taulu_etsi(t, avain);
    if (i >= 0) {
        t->tilat[i] = HAUTAKIVI;
        t->koko--;
        t->hautakivia++;
    }
}
// @loppu kasvu

// @alku vertailu
// Satunnainen operaatiosarja ajetaan sekä taululle että yksinkertaiselle
// referenssille (totuusarvotaulukko); tulosten on oltava samat.
static bool vertailutesti(int operaatioita)
{
    enum { ALUE = 4096 };
    static bool mukana[ALUE];
    Taulu t;
    if (!taulu_alusta(&t, 16)) {
        return false;
    }
    Satunnainen s = {7};
    bool samat = true;
    for (int n = 0; n < operaatioita && samat; n++) {
        uint32_t avain = satunnainen_alle(&s, ALUE);
        switch (satunnainen_alle(&s, 3)) {
        case 0:
            samat = taulu_lisaa(&t, avain);
            mukana[avain] = true;
            break;
        case 1:
            taulu_poista(&t, avain);
            mukana[avain] = false;
            break;
        default:
            samat = (taulu_etsi(&t, avain) >= 0) == mukana[avain];
        }
    }
    uint32_t referenssi = 0;
    for (int i = 0; i < ALUE; i++) {
        referenssi += mukana[i];
    }
    samat = samat && t.koko == referenssi;
    printf("vertailutesti: %d operaatiota, %s, lopussa %u avainta\n",
           operaatioita, samat ? "ei eroja" : "EROJA", t.koko);
    taulu_vapauta(&t);
    return samat;
}
// @loppu vertailu

// @alku kuormitus
static void kuormitus(double alfa)
{
    enum { KAPASITEETTI = 1 << 16 };
    Taulu t;
    if (!taulu_alusta(&t, KAPASITEETTI)) {
        return;
    }
    Satunnainen s = {42};
    uint32_t n = (uint32_t)(alfa * KAPASITEETTI);
    uint32_t *avaimet = malloc(n * sizeof *avaimet);
    if (avaimet == nullptr) {
        taulu_vapauta(&t);
        return;
    }
    // Lisäys suoraan ilman kasvatusta, jotta kuormitus on haluttu.
    for (uint32_t k = 0; k < n; k++) {
        uint32_t a;
        do {
            a = (uint32_t)satunnainen_seuraava(&s);
        } while (taulu_etsi(&t, a) >= 0);
        uint32_t i = paikka(&t, a);
        while (t.tilat[i] == KAYTOSSA) {
            i = (i + 1) & (KAPASITEETTI - 1);
        }
        t.tilat[i] = KAYTOSSA;
        t.avaimet[i] = avaimet[k] = a;
        t.koko++;
    }
    t.kokeiluja = 0;
    for (uint32_t k = 0; k < n; k++) {
        taulu_etsi(&t, avaimet[k]);
    }
    double onnistunut = (double)t.kokeiluja / n;
    t.kokeiluja = 0;
    for (uint32_t k = 0; k < n; k++) {
        taulu_etsi(&t, (uint32_t)satunnainen_seuraava(&s) | 1u << 31);
    }
    double epaonnistunut = (double)t.kokeiluja / n;
    double teoria_s = 0.5 * (1 + 1 / (1 - alfa));
    double teoria_e = 0.5 * (1 + 1 / ((1 - alfa) * (1 - alfa)));
    printf("alfa %.3f: löytyy %5.2f (teoria %5.2f), "
           "ei löydy %6.2f (teoria %6.2f)\n", alfa, onnistunut, teoria_s,
           epaonnistunut, teoria_e);
    free(avaimet);
    taulu_vapauta(&t);
}
// @loppu kuormitus

// @alku jakso
// Kahdeksan paikan taulu ja kolme avainta, joilla on sama kotipaikka.
// Keskimmäinen poistetaan: hautakiven yli haku löytää kolmannen, mutta
// tyhjäksi merkitty paikka katkaisisi jakson.
static void tulosta_taulu(const Taulu *t, const char *tila)
{
    printf("%s", tila);
    for (uint32_t i = 0; i < t->kapasiteetti; i++) {
        if (t->tilat[i] == KAYTOSSA) {
            printf(" %2u", t->avaimet[i]);
        } else {
            printf("  %c", t->tilat[i] == HAUTAKIVI ? '+' : '-');
        }
    }
    printf("\n");
}

static bool jakso(void)
{
    Taulu t;
    if (!taulu_alusta(&t, 8)) {
        return false;
    }
    uint32_t sama[3], n = 0;
    for (uint32_t a = 1; n < 3; a++) {      // kolme avainta samaan paikkaan
        if (paikka(&t, a) == paikka(&t, 1)) {
            sama[n++] = a;
        }
    }
    bool ok = true;
    for (uint32_t i = 0; i < 3; i++) {
        ok &= taulu_lisaa(&t, sama[i]);
    }
    printf("avainten %u, %u ja %u kotipaikka on %u\n", sama[0], sama[1],
           sama[2], paikka(&t, 1));
    tulosta_taulu(&t, "lisätty:    ");
    taulu_poista(&t, sama[1]);
    tulosta_taulu(&t, "hautakivi:  ");
    t.kokeiluja = 0;
    long loytyi = taulu_etsi(&t, sama[2]);
    printf("haku %u: paikka %ld, %ld kokeilua\n", sama[2], loytyi,
           t.kokeiluja);
    t.tilat[paikka(&t, 1) + 1] = TYHJA;     // virheellinen poisto
    tulosta_taulu(&t, "tyhjäksi:   ");
    printf("haku %u: %s\n\n", sama[2],
           taulu_etsi(&t, sama[2]) < 0 ? "ei löydy, vaikka avain on taulussa"
                                       : "löytyy");
    taulu_vapauta(&t);
    return ok && loytyi >= 0;
}
// @loppu jakso

int main(void)
{
    bool ok = jakso() && vertailutesti(200000);
    const double alfat[] = {0.25, 0.5, 0.625, 0.75, 0.875, 0.9};
    for (size_t i = 0; i < sizeof alfat / sizeof alfat[0]; i++) {
        kuormitus(alfat[i]);
    }
    return ok ? EXIT_SUCCESS : EXIT_FAILURE;
}
