// Mittarin päivittäiset muutokset: millä yhtenäisellä jaksolla kasvu oli
// suurin? Sama vastaus kolmella algoritmilla, joiden työmäärät eroavat
// kertaluokilla. Työ mitataan yhteenlaskujen määränä.
#include <stdio.h>
#include <stdlib.h>

#include "satunnainen.h"

enum { N = 400 };

typedef struct {
    long summa;
    int alku, loppu;     // jakso [alku, loppu]
} Jakso;

static long yhteenlaskuja;

// @alku kuutio
// Kaikki jaksot, ja jokaisen summa lasketaan alusta: noin n^3 / 6.
static Jakso kuutio(const int *x, int n)
{
    Jakso paras = { x[0], 0, 0 };
    for (int i = 0; i < n; i++) {
        for (int j = i; j < n; j++) {
            long s = 0;
            for (int k = i; k <= j; k++) {
                s += x[k];
                yhteenlaskuja++;
            }
            if (s > paras.summa) {
                paras = (Jakso){ s, i, j };
            }
        }
    }
    return paras;
}
// @loppu kuutio

// @alku nelio
// Sama alkukohta jatkaa edellisen jakson summaa: noin n^2 / 2.
static Jakso nelio(const int *x, int n)
{
    Jakso paras = { x[0], 0, 0 };
    for (int i = 0; i < n; i++) {
        long s = 0;
        for (int j = i; j < n; j++) {
            s += x[j];
            yhteenlaskuja++;
            if (s > paras.summa) {
                paras = (Jakso){ s, i, j };
            }
        }
    }
    return paras;
}
// @loppu nelio

// @alku lineaarinen
// Kadanen algoritmi: paras kohtaan j päättyvä jakso on joko pelkkä
// x[j] tai paras kohtaan j - 1 päättyvä jakso jatkettuna. Yksi kierros.
static Jakso lineaarinen(const int *x, int n)
{
    Jakso paras = { x[0], 0, 0 };
    long nykyinen = 0;
    int alku = 0;
    for (int j = 0; j < n; j++) {
        if (nykyinen <= 0) {        // aloita uusi jakso
            nykyinen = x[j];
            alku = j;
        } else {
            nykyinen += x[j];
        }
        yhteenlaskuja++;
        if (nykyinen > paras.summa) {
            paras = (Jakso){ nykyinen, alku, j };
        }
    }
    return paras;
}
// @loppu lineaarinen

static void tulosta(const char *nimi, Jakso j)
{
    printf("%-8s summa %4ld, päivät %3d..%3d, yhteenlaskuja %9ld\n",
           nimi, j.summa, j.alku, j.loppu, yhteenlaskuja);
    yhteenlaskuja = 0;
}

int main(void)
{
    int x[N];
    Satunnainen s = { 2026 };
    for (int i = 0; i < N; i++) {
        x[i] = (int)satunnainen_alle(&s, 101) - 50;   // -50..50
    }
    tulosta("O(n^3):", kuutio(x, N));
    tulosta("O(n^2):", nelio(x, N));
    tulosta("O(n):", lineaarinen(x, N));
    return EXIT_SUCCESS;
}
