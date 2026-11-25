// Graafin kolme esitystapaa: vierekkäisyysmatriisi, vierekkäisyyslistat
// ja CSR (compressed sparse row). Sama harva tieverkkoa muistuttava
// graafi kaikissa kolmessa; verrataan muistia ja tarkistetaan, että
// naapurit ovat samat.
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#include "satunnainen.h"

enum { SOLMUJA = 2000, KAARIA = 6000 };   // suuntaamaton, kaari kahdesti

typedef struct {
    uint32_t a, b;
} Kaari;

// @alku lista
typedef struct naapuri {
    uint32_t solmu;
    struct naapuri *seuraava;
} Naapuri;
// @loppu lista

// @alku csr
// CSR: kaikkien solmujen naapurit yhdessä taulukossa peräkkäin.
// Solmun v naapurit ovat kohde[alku[v]] ... kohde[alku[v + 1] - 1].
typedef struct {
    uint32_t *alku;             // n + 1 alkiota
    uint32_t *kohde;            // 2 * m alkiota
} Csr;

static bool csr_rakenna(Csr *g, uint32_t n, const Kaari *kaaret, size_t m)
{
    g->alku = calloc(n + 1, sizeof *g->alku);
    g->kohde = malloc(2 * m * sizeof *g->kohde);
    uint32_t *paikka = malloc(n * sizeof *paikka);
    if (g->alku == nullptr || g->kohde == nullptr || paikka == nullptr) {
        free(paikka);
        return false;
    }
    for (size_t i = 0; i < m; i++) {        // 1. asteluvut
        g->alku[kaaret[i].a + 1]++;
        g->alku[kaaret[i].b + 1]++;
    }
    for (uint32_t v = 0; v < n; v++) {      // 2. kumulatiivinen summa
        g->alku[v + 1] += g->alku[v];
        paikka[v] = g->alku[v];
    }
    for (size_t i = 0; i < m; i++) {        // 3. naapurit paikoilleen
        g->kohde[paikka[kaaret[i].a]++] = kaaret[i].b;
        g->kohde[paikka[kaaret[i].b]++] = kaaret[i].a;
    }
    free(paikka);
    return true;
}
// @loppu csr

// Viiden solmun graafi matriisina ja CSR-taulukoina. Kirjan kuva
// kolmesta esitystavasta piirretään näistä riveistä (kaaviot/tee.py).
static bool pieni_graafi(void)
{
    enum { N = 5, M = 5 };
    const Kaari kaaret[M] = {{0, 1}, {0, 2}, {1, 2}, {1, 3}, {3, 4}};
    Csr g;
    if (!csr_rakenna(&g, N, kaaret, M)) {
        return false;
    }
    printf("pieni graafi: %d solmua, kaaret", N);
    for (int i = 0; i < M; i++) {
        printf(" %u-%u", kaaret[i].a, kaaret[i].b);
    }
    printf("\nmatriisi:\n");
    for (uint32_t u = 0; u < N; u++) {
        for (uint32_t v = 0; v < N; v++) {
            bool kaari = false;
            for (uint32_t i = g.alku[u]; i < g.alku[u + 1]; i++) {
                kaari |= g.kohde[i] == v;
            }
            printf(" %d", kaari);
        }
        printf("\n");
    }
    printf("CSR alku: ");
    for (uint32_t v = 0; v <= N; v++) {
        printf(" %u", g.alku[v]);
    }
    printf("\nCSR kohde:");
    for (uint32_t i = 0; i < 2 * M; i++) {
        printf(" %u", g.kohde[i]);
    }
    printf("\n\n");
    free(g.alku);
    free(g.kohde);
    return true;
}

int main(void)
{
    if (!pieni_graafi()) {
        return EXIT_FAILURE;
    }
    static Kaari kaaret[KAARIA];
    Satunnainen s = {3};
    for (int i = 0; i < KAARIA; i++) {
        uint32_t a = (uint32_t)i % SOLMUJA;   // rengas + satunnaiset
        uint32_t b = i < SOLMUJA ? (a + 1) % SOLMUJA
                     : satunnainen_alle(&s, SOLMUJA);
        kaaret[i] = (Kaari){a, b == a ? (a + 1) % SOLMUJA : b};
    }

    // @alku matriisi
    // Matriisi: bitti jokaista solmuparia kohti, kaaresta riippumatta.
    size_t rivi = (SOLMUJA + 7) / 8;
    uint8_t *matriisi = calloc(SOLMUJA * rivi, 1);
    if (matriisi == nullptr) {
        return EXIT_FAILURE;
    }
    for (int i = 0; i < KAARIA; i++) {
        uint32_t a = kaaret[i].a, b = kaaret[i].b;
        matriisi[a * rivi + b / 8] |= (uint8_t)(1u << (b % 8));
        matriisi[b * rivi + a / 8] |= (uint8_t)(1u << (a % 8));
    }
    // @loppu matriisi

    Naapuri **listat = calloc(SOLMUJA, sizeof *listat);
    Naapuri *solmut = malloc(2 * KAARIA * sizeof *solmut);
    if (listat == nullptr || solmut == nullptr) {
        return EXIT_FAILURE;
    }
    for (int i = 0; i < KAARIA; i++) {
        uint32_t a = kaaret[i].a, b = kaaret[i].b;
        solmut[2 * i] = (Naapuri){b, listat[a]};
        listat[a] = &solmut[2 * i];
        solmut[2 * i + 1] = (Naapuri){a, listat[b]};
        listat[b] = &solmut[2 * i + 1];
    }

    Csr g;
    if (!csr_rakenna(&g, SOLMUJA, kaaret, KAARIA)) {
        return EXIT_FAILURE;
    }

    // Jokaisen listan ja CSR-rivin naapurin on oltava matriisissa, ja
    // naapureiden määrä on solmun aste kaikissa esityksissä.
    bool samat = true;
    for (uint32_t v = 0; v < SOLMUJA; v++) {
        uint32_t aste = 0;
        for (const Naapuri *n = listat[v]; n != nullptr; n = n->seuraava) {
            samat &= (matriisi[v * rivi + n->solmu / 8]
                      >> (n->solmu % 8)) & 1;
            aste++;
        }
        samat &= aste == g.alku[v + 1] - g.alku[v];
        // @alku naapurit
        for (uint32_t i = g.alku[v]; i < g.alku[v + 1]; i++) {
            uint32_t naapuri = g.kohde[i];
            samat &= (matriisi[v * rivi + naapuri / 8] >> (naapuri % 8)) & 1;
        }
        // @loppu naapurit
    }

    printf("%d solmua, %d kaarta\n", SOLMUJA, KAARIA);
    printf("matriisi: %8zu tavua\n", (size_t)SOLMUJA * rivi);
    printf("listat:   %8zu tavua\n", SOLMUJA * sizeof *listat
           + 2 * (size_t)KAARIA * sizeof(Naapuri));
    printf("CSR:      %8zu tavua\n", (SOLMUJA + 1) * sizeof *g.alku
           + 2 * (size_t)KAARIA * sizeof *g.kohde);
    printf("naapurit samat kaikissa esityksissä: %s\n",
           samat ? "kyllä" : "EI");
    free(matriisi);
    free(listat);
    free(solmut);
    free(g.alku);
    free(g.kohde);
    return samat ? EXIT_SUCCESS : EXIT_FAILURE;
}
