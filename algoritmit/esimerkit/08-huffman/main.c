// Huffman-pakkaus tiedostoon ja takaisin. Luetaan teksti syötteestä,
// rakennetaan koodi, kirjoitetaan pakattu tiedosto pakattu.huf ja
// puretaan se. Otsikossa ovat merkkien frekvenssit, joista purkaja
// rakentaa täsmälleen saman puun.
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "huffman.h"

// @alku bitit
typedef struct {
    FILE *f;
    int tavu, bitteja;  // keräyspuskuri: täysi tavu kirjoitetaan
} Kirjoittaja;

static void kirjoita_bitti(Kirjoittaja *k, int bitti)
{
    k->tavu = (k->tavu << 1) | bitti;
    if (++k->bitteja == 8) {
        fputc(k->tavu, k->f);
        k->tavu = k->bitteja = 0;
    }
}

static void tyhjenna(Kirjoittaja *k)  // täytetään viimeinen tavu nollilla
{
    while (k->bitteja != 0) {
        kirjoita_bitti(k, 0);
    }
}
// @loppu bitit

static void kirjoita_luku(FILE *f, unsigned long x, int tavuja)
{
    for (int i = 0; i < tavuja; i++) {
        fputc((int)((x >> (8 * i)) & 0xFF), f);
    }
}

// Palauttaa -1, jos tiedosto loppui kesken.
static long lue_luku(FILE *f, int tavuja)
{
    long x = 0;
    for (int i = 0; i < tavuja; i++) {
        int c = fgetc(f);
        if (c == EOF) {
            return -1;
        }
        x |= (long)c << (8 * i);
    }
    return x;
}

// @alku pakkaa
static bool pakkaa(const unsigned char *data, long n, const char *nimi)
{
    long frekvenssi[MERKKEJA] = { 0 };
    for (long i = 0; i < n; i++) {
        frekvenssi[data[i]]++;
    }
    static Puu p;
    huffman_rakenna(&p, frekvenssi);

    FILE *f = fopen(nimi, "wb");
    if (f == nullptr) {
        return false;
    }
    int eri = 0;
    for (int m = 0; m < MERKKEJA; m++) {
        eri += frekvenssi[m] > 0;
    }
    kirjoita_luku(f, (unsigned long)n, 4);       // otsikko
    kirjoita_luku(f, (unsigned long)eri, 2);
    for (int m = 0; m < MERKKEJA; m++) {
        if (frekvenssi[m] > 0) {
            kirjoita_luku(f, (unsigned long)m, 1);
            kirjoita_luku(f, (unsigned long)frekvenssi[m], 4);
        }
    }
    Kirjoittaja k = { f, 0, 0 };                 // data
    for (long i = 0; i < n; i++) {
        Koodi c = p.koodi[data[i]];
        for (int b = c.pituus - 1; b >= 0; b--) {
            kirjoita_bitti(&k, (int)((c.bitit >> b) & 1));
        }
    }
    tyhjenna(&k);
    return fclose(f) == 0;
}
// @loppu pakkaa

// @alku pura
static unsigned char *pura(const char *nimi, long *n)
{
    FILE *f = fopen(nimi, "rb");
    if (f == nullptr) {
        return nullptr;
    }
    *n = lue_luku(f, 4);
    long eri = lue_luku(f, 2);
    long frekvenssi[MERKKEJA] = { 0 };
    bool ehja = *n >= 0 && eri >= 0 && eri <= MERKKEJA;
    for (long i = 0; ehja && i < eri; i++) {
        long m = lue_luku(f, 1), maara = lue_luku(f, 4);
        ehja = m >= 0 && maara >= 0;
        if (ehja) {
            frekvenssi[m] = maara;
        }
    }
    if (!ehja) {
        fclose(f);
        return nullptr;
    }
    static Puu p;
    huffman_rakenna(&p, frekvenssi);

    unsigned char *ulos = malloc((size_t)*n + 1);
    if (ulos == nullptr) {
        fclose(f);
        return nullptr;
    }
    int tavu = 0, jaljella = 0;
    for (long i = 0; i < *n; i++) {
        int s = p.juuri;
        do {                    // kuljetaan juuresta lehteen bitti kerrallaan
            if (jaljella == 0) {
                if ((tavu = fgetc(f)) == EOF) {
                    free(ulos);
                    fclose(f);
                    return nullptr;
                }
                jaljella = 8;
            }
            int bitti = (tavu >> --jaljella) & 1;
            if (p.solmut[s].vasen >= 0) {
                s = bitti ? p.solmut[s].oikea : p.solmut[s].vasen;
            }
        } while (p.solmut[s].vasen >= 0);
        ulos[i] = (unsigned char)p.solmut[s].merkki;
    }
    fclose(f);
    return ulos;
}
// @loppu pura

static void nayta_merkki(int m)
{
    if (m == ' ') {
        printf("' ' ");
    } else if (m == '\n') {
        printf("\\n  ");
    } else if (m > ' ' && m < 127) {
        printf("'%c' ", m);
    } else {
        printf("x%02X ", m);
    }
}

int main(void)
{
    static unsigned char data[1 << 16];
    long n = (long)fread(data, 1, sizeof data, stdin);
    long frekvenssi[MERKKEJA] = { 0 };
    for (long i = 0; i < n; i++) {
        frekvenssi[data[i]]++;
    }
    static Puu p;
    huffman_rakenna(&p, frekvenssi);

    int eri = 0;
    long bitteja = 0;
    double entropia = 0;
    for (int m = 0; m < MERKKEJA; m++) {
        if (frekvenssi[m] > 0) {
            eri++;
            bitteja += frekvenssi[m] * p.koodi[m].pituus;
            double q = (double)frekvenssi[m] / (double)n;
            entropia -= q * log2(q);
        }
    }
    printf("syöte: %ld tavua, %d eri tavuarvoa\n", n, eri);
    printf("merkki määrä  koodi\n");
    bool kaytetty[MERKKEJA] = { false };
    for (int r = 0; r < 6 && r < eri; r++) {  // yleisimmät merkit
        int paras = -1;
        for (int m = 0; m < MERKKEJA; m++) {
            if (!kaytetty[m] && frekvenssi[m] > 0 &&
                (paras < 0 || frekvenssi[m] > frekvenssi[paras])) {
                paras = m;
            }
        }
        kaytetty[paras] = true;
        nayta_merkki(paras);
        printf("   %5ld  ", frekvenssi[paras]);
        for (int b = p.koodi[paras].pituus - 1; b >= 0; b--) {
            putchar((int)((p.koodi[paras].bitit >> b) & 1) + '0');
        }
        printf("\n");
    }
    printf("keskimäärin %.3f bittiä/merkki, entropia %.3f\n",
           (double)bitteja / (double)n, entropia);

    if (!pakkaa(data, n, "pakattu.huf")) {
        perror("pakattu.huf");
        return EXIT_FAILURE;
    }
    FILE *f = fopen("pakattu.huf", "rb");
    if (f == nullptr) {
        perror("pakattu.huf");
        return EXIT_FAILURE;
    }
    fseek(f, 0, SEEK_END);
    long koko = ftell(f);
    fclose(f);
    printf("pakattu.huf: %ld tavua (otsikko %d, data %ld), %.1f %%\n",
           koko, 6 + 5 * eri, (bitteja + 7) / 8,
           100.0 * (double)koko / (double)n);

    long m;
    unsigned char *purettu = pura("pakattu.huf", &m);
    if (purettu == nullptr) {
        perror("pakattu.huf");
        return EXIT_FAILURE;
    }
    printf("purettu: %s\n", m == n && memcmp(purettu, data, (size_t)n) == 0
                                ? "sama kuin syöte" : "VIRHE");
    free(purettu);
    return EXIT_SUCCESS;
}
