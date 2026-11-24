// Matriisitulo kahdella silmukkajärjestyksellä ja lohkottuna. Ilman
// argumentteja ohjelma tarkistaa tulokset pienellä matriisilla;
// argumentilla "mittaa" se vertaa aikoja (Makefile, optimoituna).
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

enum { LOHKO = 64 };
static int N = 128;             // "mittaa": 512

static double sekunnit(void)
{
    struct timespec t;
    timespec_get(&t, TIME_UTC);        // C11:n vakiokirjastossa
    return (double)t.tv_sec + (double)t.tv_nsec * 1e-9;
}

// @alku ijk
// C = A B, kaikki N x N rivijärjestyksessä.
static void ijk(const double *a, const double *b, double *c)
{
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            double s = 0.0;
            for (int k = 0; k < N; k++) {
                s += a[i * N + k] * b[k * N + j];   // b sarakkeittain
            }
            c[i * N + j] = s;
        }
    }
}
// @loppu ijk

// @alku ikj
static void ikj(const double *a, const double *b, double *c)
{
    memset(c, 0, sizeof(double) * (size_t)N * (size_t)N);
    for (int i = 0; i < N; i++) {
        for (int k = 0; k < N; k++) {
            double aik = a[i * N + k];
            for (int j = 0; j < N; j++) {
                c[i * N + j] += aik * b[k * N + j];  // kaikki riveittäin
            }
        }
    }
}
// @loppu ikj

// @alku lohkottu
static void lohkottu(const double *a, const double *b, double *c)
{
    memset(c, 0, sizeof(double) * (size_t)N * (size_t)N);
    for (int ii = 0; ii < N; ii += LOHKO) {
        for (int kk = 0; kk < N; kk += LOHKO) {
            for (int jj = 0; jj < N; jj += LOHKO) {
                // LOHKO x LOHKO -osamatriisit mahtuvat välimuistiin.
                for (int i = ii; i < ii + LOHKO; i++) {
                    for (int k = kk; k < kk + LOHKO; k++) {
                        double aik = a[i * N + k];
                        for (int j = jj; j < jj + LOHKO; j++) {
                            c[i * N + j] += aik * b[k * N + j];
                        }
                    }
                }
            }
        }
    }
}
// @loppu lohkottu

typedef void (*Tulo)(const double *, const double *, double *);

static double paras_aika(Tulo f, const double *a, const double *b,
                         double *c)
{
    double paras = 1e9;
    for (int kierros = 0; kierros < 2; kierros++) {
        double t0 = sekunnit();
        f(a, b, c);
        double t = sekunnit() - t0;
        paras = t < paras ? t : paras;
    }
    return paras;
}

static double suurin_ero(const double *x, const double *y)
{
    double ero = 0.0;
    for (int i = 0; i < N * N; i++) {
        ero = fmax(ero, fabs(x[i] - y[i]));
    }
    return ero;
}

int main(int argc, char **argv)
{
    bool mittaa = argc > 1 && strcmp(argv[1], "mittaa") == 0;
    if (mittaa) {
        N = 512;
    }
    size_t koko = sizeof(double) * (size_t)N * (size_t)N;
    double *a = malloc(koko), *b = malloc(koko);
    double *c1 = malloc(koko), *c2 = malloc(koko), *c3 = malloc(koko);
    if (!a || !b || !c1 || !c2 || !c3) {
        return 1;
    }
    for (int i = 0; i < N * N; i++) {
        a[i] = sin(i * 0.001);
        b[i] = cos(i * 0.002);
    }
    double t1 = paras_aika(ijk, a, b, c1);
    double t2 = paras_aika(ikj, a, b, c2);
    double t3 = paras_aika(lohkottu, a, b, c3);
    printf("tulokset samat (ero < 1e-9): %s\n",
           suurin_ero(c1, c2) < 1e-9 && suurin_ero(c1, c3) < 1e-9
               ? "kyllä" : "ei");
    printf("liukulukuoperaatioita %.0f miljoonaa\n",
           2.0 * N * N * N / 1e6);
    if (mittaa) {
        printf("ikj vähintään 2 kertaa nopeampi kuin ijk: %s\n",
               t1 > 2.0 * t2 ? "kyllä" : "ei");
        printf("lohkottu vähintään 2 kertaa nopeampi kuin ijk: %s\n",
               t1 > 2.0 * t3 ? "kyllä" : "ei");
    }
    free(a);
    free(b);
    free(c1);
    free(c2);
    free(c3);
    return 0;
}
