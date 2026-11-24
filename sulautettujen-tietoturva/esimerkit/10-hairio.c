// Vikahyökkäyksen simulointi. Jännite- tai kellohäiriö voi saada
// suorittimen ohittamaan käskyn tai kääntämään rekisterin bitin.
// Käynnistimen päätös mallinnetaan pienenä käskyohjelmana, ja kaikki
// yksittäiset viat kokeillaan, kun allekirjoitus EI kelpaa: kuinka
// moni vika saa laitteen silti käynnistämään väärän kuvan?
#include <stdint.h>
#include <stdio.h>

enum op { TARKISTA, HYPPAA_JOS_NOLLA, HYPPAA_JOS_ERI, LASKURI_LISAA,
          HYPPAA_JOS_LASKURI_ERI, KAYNNISTA, PYSAYTA };

typedef struct {
    enum op op;
    int kohde;          // hypyn kohde
    uint32_t arvo;      // vertailuarvo
} kasky_t;

typedef struct {
    const char *nimi;
    const kasky_t *koodi;
    int pituus;
    uint32_t kelpaa, hylatty, alkuarvo;
} ohjelma_t;

#define KELPAA 0x5AA5C33Cu
#define HYLATTY 0xA55A3CC3u

// @alku ohjelmat
// Tavallinen: if (!tarkista()) pysähdy; käynnistä();
static const kasky_t TAVALLINEN[] = {
    {TARKISTA, 0, 0},
    {HYPPAA_JOS_NOLLA, 3, 0},
    {KAYNNISTA, 0, 0},
    {PYSAYTA, 0, 0},
};

// Kovennettu: turvallinen oletusarvo, vaikeasti käännettävät vakiot,
// tuplatarkistus ja kulunlaskuri, joka todistaa molempien
// tarkistusten suorittamisen.
static const kasky_t KOVENNETTU[] = {
    {TARKISTA, 0, 0},
    {LASKURI_LISAA, 0, 0},
    {HYPPAA_JOS_ERI, 7, KELPAA},
    {LASKURI_LISAA, 0, 0},
    {HYPPAA_JOS_ERI, 7, KELPAA},
    {HYPPAA_JOS_LASKURI_ERI, 7, 2},
    {KAYNNISTA, 0, 0},
    {PYSAYTA, 0, 0},
};
// @loppu ohjelmat

// Ajaa ohjelman. ohitettavat: käskyjen indeksit, jotka ohitetaan
// (bittimaski); kaanto: XOR-maski tulosrekisteriin tarkistuksen
// jälkeen. Palauttaa 1, jos laite käynnisti kuvan.
static int aja(const ohjelma_t *p, uint32_t ohitettavat, uint32_t kaanto) {
    uint32_t r = p->alkuarvo;
    int laskuri = 0;
    int pc = 0;
    for (int askel = 0; askel < 64 && pc < p->pituus; askel++) {
        kasky_t k = p->koodi[pc];
        if (ohitettavat & (1u << pc)) {
            pc++;
            continue;
        }
        pc++;
        switch (k.op) {
        case TARKISTA:      // allekirjoitus ei kelpaa
            r = p->hylatty ^ kaanto;
            break;
        case HYPPAA_JOS_NOLLA:
            if (r == 0) pc = k.kohde;
            break;
        case HYPPAA_JOS_ERI:
            if (r != k.arvo) pc = k.kohde;
            break;
        case LASKURI_LISAA:
            laskuri++;
            break;
        case HYPPAA_JOS_LASKURI_ERI:
            if (laskuri != (int)k.arvo) pc = k.kohde;
            break;
        case KAYNNISTA:
            return 1;
        case PYSAYTA:
            return 0;
        }
    }
    return 0;
}

// @alku kokeile
static void kokeile(const ohjelma_t *p) {
    int ohitus = 0, kaanto = 0, kaksi = 0, pareja = 0;
    for (int i = 0; i < p->pituus; i++) {
        ohitus += aja(p, 1u << i, 0);
    }
    for (int b = 0; b < 32; b++) {
        kaanto += aja(p, 0, 1u << b);
    }
    for (int i = 0; i < p->pituus; i++) {
        for (int j = i + 1; j < p->pituus; j++) {
            kaksi += aja(p, (1u << i) | (1u << j), 0);
            pareja++;
        }
    }
    printf("%s:\n", p->nimi);
    printf("  yksi ohitettu käsky:  %d/%d käynnistää\n", ohitus,
           p->pituus);
    printf("  yksi käännetty bitti: %d/32 käynnistää\n", kaanto);
    printf("  kaksi ohitettua:      %d/%d käynnistää\n", kaksi, pareja);
}
// @loppu kokeile

int main(void) {
    const ohjelma_t tavallinen = {"Tavallinen", TAVALLINEN, 4, 1, 0, 0};
    const ohjelma_t kovennettu = {"Kovennettu", KOVENNETTU, 8,
                                  KELPAA, HYLATTY, HYLATTY};
    printf("Ilman vikaa: tavallinen %d, kovennettu %d\n",
           aja(&tavallinen, 0, 0), aja(&kovennettu, 0, 0));
    kokeile(&tavallinen);
    kokeile(&kovennettu);
    return 0;
}
