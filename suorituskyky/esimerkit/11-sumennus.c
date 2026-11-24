// Tapaustutkimus: kuvan laatikkosumennus neljässä vaiheessa.
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>

#include "mittari.h"
#include "satunnainen.h"

// Harmaasävykuva, yksi tavu pikseliä kohden, riveittäin.
typedef struct {
    int leveys, korkeus;
    uint8_t *data;
} Kuva;

enum { R = 4, IKKUNA = 2 * R + 1, ALA = IKKUNA * IKKUNA };

static int rajaa(int i, int n)
{
    return i < 0 ? 0 : i >= n ? n - 1 : i;
}

// Pyöristetty keskiarvo; jakaja on vakio, joten kääntäjä korvaa
// jakolaskun kertolaskulla ja siirrolla.
static uint8_t keskiarvo(uint32_t summa)
{
    return (uint8_t)((summa + ALA / 2) / ALA);
}

// @alku v1
// Vaihe 1: suoraviivainen. (2R+1)^2 = 81 lukua ja rajausta pikselille.
[[gnu::noinline]] static void sumenna_v1(const Kuva *k, uint8_t *ulos)
{
    for (int y = 0; y < k->korkeus; y++) {
        for (int x = 0; x < k->leveys; x++) {
            uint32_t s = 0;
            for (int dy = -R; dy <= R; dy++) {
                for (int dx = -R; dx <= R; dx++) {
                    int yy = rajaa(y + dy, k->korkeus);
                    int xx = rajaa(x + dx, k->leveys);
                    s += k->data[(size_t)yy * (size_t)k->leveys
                                 + (size_t)xx];
                }
            }
            ulos[(size_t)y * (size_t)k->leveys + (size_t)x] = keskiarvo(s);
        }
    }
}
// @loppu v1

// @alku v2
// Vaihe 2: erotuva suodin. Laatikon summa = rivisummien summa, joten
// ensin vaakasuunta väliaikaiseen taulukkoon ja sitten pystysuunta.
// 2 x 9 lukua pikseliä kohden 81:n sijaan.
[[gnu::noinline]] static void sumenna_v2(const Kuva *k, uint16_t *vali,
                                         uint8_t *ulos)
{
    int w = k->leveys, h = k->korkeus;
    for (int y = 0; y < h; y++) {
        for (int x = 0; x < w; x++) {
            uint32_t s = 0;
            for (int dx = -R; dx <= R; dx++) {
                s += k->data[(size_t)y * (size_t)w
                             + (size_t)rajaa(x + dx, w)];
            }
            vali[(size_t)y * (size_t)w + (size_t)x] = (uint16_t)s;
        }
    }
    for (int y = 0; y < h; y++) {
        for (int x = 0; x < w; x++) {
            uint32_t s = 0;
            for (int dy = -R; dy <= R; dy++) {
                s += vali[(size_t)rajaa(y + dy, h) * (size_t)w + (size_t)x];
            }
            ulos[(size_t)y * (size_t)w + (size_t)x] = keskiarvo(s);
        }
    }
}
// @loppu v2

// @alku v3
// Vaihe 3: liukuva summa. Ikkunan siirtyessä yhden askeleen summaan
// lisätään tuleva ja siitä vähennetään poistuva arvo: työ ei riipu
// säteestä R. Pystysuunta kulkee yhä sarake kerrallaan.
[[gnu::always_inline]] static inline void vaaka_liukuva(const Kuva *k,
                                                     uint16_t *vali)
{
    int w = k->leveys;
    for (int y = 0; y < k->korkeus; y++) {
        const uint8_t *rivi = k->data + (size_t)y * (size_t)w;
        uint32_t s = 0;
        for (int dx = -R; dx <= R; dx++) {
            s += rivi[rajaa(dx, w)];
        }
        for (int x = 0; x < w; x++) {
            vali[(size_t)y * (size_t)w + (size_t)x] = (uint16_t)s;
            s += rivi[rajaa(x + R + 1, w)];
            s -= rivi[rajaa(x - R, w)];
        }
    }
}

[[gnu::noinline]] static void sumenna_v3(const Kuva *k, uint16_t *vali,
                                         uint8_t *ulos)
{
    int w = k->leveys, h = k->korkeus;
    vaaka_liukuva(k, vali);
    for (int x = 0; x < w; x++) {           // sarake kerrallaan
        uint32_t s = 0;
        for (int dy = -R; dy <= R; dy++) {
            s += vali[(size_t)rajaa(dy, h) * (size_t)w + (size_t)x];
        }
        for (int y = 0; y < h; y++) {
            ulos[(size_t)y * (size_t)w + (size_t)x] = keskiarvo(s);
            s += vali[(size_t)rajaa(y + R + 1, h) * (size_t)w + (size_t)x];
            s -= vali[(size_t)rajaa(y - R, h) * (size_t)w + (size_t)x];
        }
    }
}
// @loppu v3

// @alku v4
// Vaihe 4: pystysuunnan liukuva summa rivi kerrallaan. Jokaisella
// sarakkeella on oma summansa taulukossa; rivin kaikki sarakkeet
// päivitetään peräkkäin, joten muistia luetaan riveittäin ja sisin
// silmukka vektoroituu.
[[gnu::noinline]] static void sumenna_v4(const Kuva *k, uint16_t *vali,
                                         uint16_t *restrict summat,
                                         uint8_t *ulos)
{
    int w = k->leveys, h = k->korkeus;
    vaaka_liukuva(k, vali);
    for (int x = 0; x < w; x++) {
        summat[x] = 0;
    }
    for (int dy = -R; dy <= R; dy++) {
        const uint16_t *restrict r =
            vali + (size_t)rajaa(dy, h) * (size_t)w;
        for (int x = 0; x < w; x++) {
            summat[x] = (uint16_t)(summat[x] + r[x]);
        }
    }
    for (int y = 0; y < h; y++) {
        const uint16_t *restrict tuleva =
            vali + (size_t)rajaa(y + R + 1, h) * (size_t)w;
        const uint16_t *restrict poistuva =
            vali + (size_t)rajaa(y - R, h) * (size_t)w;
        uint8_t *restrict kohde = ulos + (size_t)y * (size_t)w;
        for (int x = 0; x < w; x++) {
            kohde[x] = keskiarvo(summat[x]);
            summat[x] = (uint16_t)(summat[x] + tuleva[x] - poistuva[x]);
        }
    }
}
// @loppu v4

static Kuva luo_kuva(int w, int h)
{
    Kuva k = {w, h, malloc((size_t)w * (size_t)h)};
    if (k.data == NULL) {
        perror("malloc");
        exit(EXIT_FAILURE);
    }
    Satunnainen r = {99};
    for (int y = 0; y < h; y++) {
        for (int x = 0; x < w; x++) {
            int liuku = (x * 255 / w + y * 128 / h) / 2;
            int kohina = (int)satunnainen_alle(&r, 64) - 32;
            k.data[(size_t)y * (size_t)w + (size_t)x] =
                (uint8_t)rajaa(liuku + kohina + 64, 256);
        }
    }
    return k;
}

// FNV-1a-tiiviste kuvan vertailuun.
static uint32_t tiiviste(const uint8_t *p, size_t n)
{
    uint32_t h = 2166136261u;
    for (size_t i = 0; i < n; i++) {
        h = (h ^ p[i]) * 16777619u;
    }
    return h;
}

typedef struct {
    const Kuva *kuva;
    uint16_t *vali, *summat;
    uint8_t *ulos;
    int versio;
} Tila;

static void aja(void *p)
{
    Tila *t = p;
    switch (t->versio) {
    case 1: sumenna_v1(t->kuva, t->ulos); break;
    case 2: sumenna_v2(t->kuva, t->vali, t->ulos); break;
    case 3: sumenna_v3(t->kuva, t->vali, t->ulos); break;
    default: sumenna_v4(t->kuva, t->vali, t->summat, t->ulos); break;
    }
    kayta(t->ulos);
}

int main(int argc, char **argv)
{
    int koko = mittaustila(argc, argv) ? 2048 : 123;    // 123: pariton
    if (argc == 3 && strcmp(argv[1], "--kerran") == 0) {
        koko = atoi(argv[2]);
    }
    Kuva k = luo_kuva(koko, koko);
    size_t n = (size_t)koko * (size_t)koko;
    uint16_t *vali = malloc(n * sizeof *vali);
    uint16_t *summat = malloc((size_t)koko * sizeof *summat);
    uint8_t *ulos = malloc(n);
    if (vali == NULL || summat == NULL || ulos == NULL) {
        return EXIT_FAILURE;
    }
    double vertailu = 0;
    uint32_t viite = 0;
    bool samat = true;
    if (mittaustila(argc, argv)) {
        printf("laatikkosumennus %dx%d, R = %d\n", koko, koko, R);
    }
    for (int v = 1; v <= 4; v++) {
        Tila t = {&k, vali, summat, ulos, v};
        if (mittaustila(argc, argv)) {
            char nimi[16];
            snprintf(nimi, sizeof nimi, "vaihe %d", v);
            Tilasto s = mittaa(aja, &t, v == 1 ? 3 : 11);
            tulosta_mittaus(nimi, s, vertailu);
            vertailu = v == 1 ? s.mediaani : vertailu;
        } else {
            aja(&t);
        }
        uint32_t h = tiiviste(ulos, n);
        viite = v == 1 ? h : viite;
        samat = samat && h == viite;
    }
    printf("tiiviste %08x, kaikki vaiheet samat: %s\n", viite,
           samat ? "kylla" : "ei");
    free(k.data);
    free(vali);
    free(summat);
    free(ulos);
    return samat ? 0 : 1;
}
