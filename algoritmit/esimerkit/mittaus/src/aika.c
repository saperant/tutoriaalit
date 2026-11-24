// Ajoitusmittaus optimoidulla käännöksellä: lisäyslajittelu,
// lomituslajittelu, kantalukulajittelu ja kirjaston qsort samoilla
// satunnaisilla luvuilla. Tulostetaan vain vertailujen tulokset
// väljillä rajoilla, jotta mittaus ei ole herkkä koneen kuormalle.
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#include "../../satunnainen.h"

static double sekunnit(void)
{
    struct timespec t;
    timespec_get(&t, TIME_UTC);
    return (double)t.tv_sec + (double)t.tv_nsec * 1e-9;
}

static void lisays(uint32_t *a, int n)
{
    for (int i = 1; i < n; i++) {
        uint32_t x = a[i];
        int j = i - 1;
        while (j >= 0 && a[j] > x) {
            a[j + 1] = a[j];
            j--;
        }
        a[j + 1] = x;
    }
}

static void lomitus(uint32_t *a, uint32_t *apu, int lo, int hi)
{
    if (hi - lo < 2) {
        return;
    }
    int keski = lo + (hi - lo) / 2, i = lo, j = keski, k = lo;
    lomitus(a, apu, lo, keski);
    lomitus(a, apu, keski, hi);
    while (i < keski && j < hi) {
        apu[k++] = a[j] < a[i] ? a[j++] : a[i++];
    }
    while (i < keski) {
        apu[k++] = a[i++];
    }
    while (j < hi) {
        apu[k++] = a[j++];
    }
    memcpy(a + lo, apu + lo, (size_t)(hi - lo) * sizeof *a);
}

static void kantaluku(uint32_t *a, uint32_t *apu, int n)
{
    for (int siirto = 0; siirto < 32; siirto += 8) {
        int alku[257] = { 0 };
        for (int i = 0; i < n; i++) {
            alku[((a[i] >> siirto) & 0xFF) + 1]++;
        }
        for (int k = 0; k < 256; k++) {
            alku[k + 1] += alku[k];
        }
        for (int i = 0; i < n; i++) {
            apu[alku[(a[i] >> siirto) & 0xFF]++] = a[i];
        }
        memcpy(a, apu, (size_t)n * sizeof *a);
    }
}

static int vertaa(const void *x, const void *y)
{
    uint32_t a = *(const uint32_t *)x, b = *(const uint32_t *)y;
    return (a > b) - (a < b);
}

// @alku mittaus
enum { PIENI = 40000, SUURI = 1 << 22 };

int main(void)
{
    uint32_t *alku = malloc(SUURI * sizeof *alku);
    uint32_t *a = malloc(SUURI * sizeof *a);
    uint32_t *b = malloc(SUURI * sizeof *b);
    uint32_t *apu = malloc(SUURI * sizeof *apu);
    if (alku == nullptr || a == nullptr || b == nullptr || apu == nullptr) {
        return EXIT_FAILURE;
    }
    Satunnainen s = { 1 };
    for (int i = 0; i < SUURI; i++) {
        alku[i] = (uint32_t)satunnainen_seuraava(&s);
    }

    // n = 40 000: O(n^2) vastaan O(n log n).
    memcpy(a, alku, PIENI * sizeof *a);
    memcpy(b, alku, PIENI * sizeof *b);
    double t0 = sekunnit();
    lisays(a, PIENI);
    double t1 = sekunnit();
    lomitus(b, apu, 0, PIENI);
    double t2 = sekunnit();
    printf("lisäys ja lomitus samat: %s\n",
           memcmp(a, b, PIENI * sizeof *a) == 0 ? "kyllä" : "ei");
    printf("lisäys vähintään 10 kertaa hitaampi kuin lomitus: %s\n",
           t1 - t0 > 10 * (t2 - t1) ? "kyllä" : "ei");

    // n = 4 194 304: kantaluku O(n) vastaan qsort O(n log n).
    memcpy(a, alku, SUURI * sizeof *a);
    memcpy(b, alku, SUURI * sizeof *b);
    t0 = sekunnit();
    qsort(a, SUURI, sizeof *a, vertaa);
    t1 = sekunnit();
    kantaluku(b, apu, SUURI);
    t2 = sekunnit();
    printf("qsort ja kantaluku samat: %s\n",
           memcmp(a, b, SUURI * sizeof *a) == 0 ? "kyllä" : "ei");
    printf("kantaluku vähintään 2 kertaa nopeampi kuin qsort: %s\n",
           t1 - t0 > 2 * (t2 - t1) ? "kyllä" : "ei");
    free(alku);
    free(a);
    free(b);
    free(apu);
    return EXIT_SUCCESS;
}
// @loppu mittaus
