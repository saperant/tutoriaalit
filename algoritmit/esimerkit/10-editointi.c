// Editointietäisyys (Levenshtein): pienin määrä yhden merkin lisäyksiä,
// poistoja ja korvauksia, joilla a muuttuu b:ksi. Taulukosta luetaan
// myös itse muokkaukset. Tulos tarkistetaan suoralla rekursiolla, joka
// on eksponentiaalinen mutta ilmeisesti oikein.
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "satunnainen.h"

enum { MAX = 32 };

static int min3(int x, int y, int z)
{
    int m = x < y ? x : y;
    return m < z ? m : z;
}

// @alku etaisyys
// e[i][j] = etäisyys alkuosien a[0..i) ja b[0..j) välillä:
//   e[i][0] = i, e[0][j] = j
//   e[i][j] = min(e[i-1][j] + 1,                  poista a[i-1]
//                 e[i][j-1] + 1,                  lisää b[j-1]
//                 e[i-1][j-1] + (a[i-1] != b[j-1]))  korvaa tai pidä
static int e[MAX + 1][MAX + 1];

static int etaisyys(const char *a, const char *b)
{
    int n = (int)strlen(a), m = (int)strlen(b);
    for (int i = 0; i <= n; i++) {
        for (int j = 0; j <= m; j++) {
            if (i == 0 || j == 0) {
                e[i][j] = i + j;
            } else {
                e[i][j] = min3(e[i - 1][j] + 1, e[i][j - 1] + 1,
                               e[i - 1][j - 1] + (a[i - 1] != b[j - 1]));
            }
        }
    }
    return e[n][m];
}
// @loppu etaisyys

// @alku kohdistus
// Kuljetaan taulukkoa takaperin ja valitaan askel, joka selittää arvon.
// Rivit kirjoitetaan lopusta alkuun ja käännetään lopuksi.
static void kohdistus(const char *a, const char *b)
{
    char ra[2 * MAX + 1], rb[2 * MAX + 1], op[2 * MAX + 1];
    int k = 0;
    for (int i = (int)strlen(a), j = (int)strlen(b); i > 0 || j > 0; k++) {
        if (i > 0 && j > 0 &&
            e[i][j] == e[i - 1][j - 1] + (a[i - 1] != b[j - 1])) {
            ra[k] = a[--i];
            rb[k] = b[--j];
            op[k] = ra[k] == rb[k] ? '=' : '~';    // pidä tai korvaa
        } else if (i > 0 && e[i][j] == e[i - 1][j] + 1) {
            ra[k] = a[--i];
            rb[k] = '-';
            op[k] = 'x';                            // poista
        } else {
            ra[k] = '-';
            rb[k] = b[--j];
            op[k] = '+';                            // lisää
        }
    }
    const char *rivit[] = { ra, rb, op };
    for (int r = 0; r < 3; r++) {
        printf("  ");
        for (int t = k - 1; t >= 0; t--) {
            printf(" %c", rivit[r][t]);
        }
        printf("\n");
    }
}
// @loppu kohdistus

// Tulostaa etaisyys-kutsun täyttämän taulukon ja merkitsee tähdellä
// ruudut, joiden kautta kohdistus kulkee (sama sääntö kuin yllä).
// Kirjan kuva piirretään tästä tulosteesta (kaaviot/tee.py).
static void tulosta_taulukko(const char *a, const char *b)
{
    int n = (int)strlen(a), m = (int)strlen(b);
    static bool polku[MAX + 1][MAX + 1];
    memset(polku, 0, sizeof polku);
    int i = n, j = m;
    polku[i][j] = true;
    while (i > 0 || j > 0) {
        if (i > 0 && j > 0 &&
            e[i][j] == e[i - 1][j - 1] + (a[i - 1] != b[j - 1])) {
            i--;
            j--;
        } else if (i > 0 && e[i][j] == e[i - 1][j] + 1) {
            i--;
        } else {
            j--;
        }
        polku[i][j] = true;
    }
    printf("taulukko %s / %s, kohdistuksen polku tähdellä:\n     -", a, b);
    for (j = 0; j < m; j++) {
        printf("  %c", b[j]);
    }
    printf("\n");
    for (i = 0; i <= n; i++) {
        printf("  %c", i == 0 ? '-' : a[i - 1]);
        for (j = 0; j <= m; j++) {
            printf(" %c%d", polku[i][j] ? '*' : ' ', e[i][j]);
        }
        printf("\n");
    }
}

static int raaka(const char *a, const char *b)
{
    if (*a == '\0') {
        return (int)strlen(b);
    }
    if (*b == '\0') {
        return (int)strlen(a);
    }
    return min3(raaka(a + 1, b) + 1, raaka(a, b + 1) + 1,
                raaka(a + 1, b + 1) + (*a != *b));
}

int main(void)
{
    const char *parit[][2] = {
        { "kissa", "koira" },
        { "algoritmi", "logaritmi" },
        { "lauantai", "sunnuntai" },
    };
    for (int i = 0; i < 3; i++) {
        printf("%s -> %s: etäisyys %d\n", parit[i][0], parit[i][1],
               etaisyys(parit[i][0], parit[i][1]));
        kohdistus(parit[i][0], parit[i][1]);
    }
    tulosta_taulukko(parit[2][0], parit[2][1]);     // viimeisin kutsu

    Satunnainen s = { 37 };
    int virheita = 0;
    for (int k = 0; k < 300; k++) {
        char a[8], b[8];
        int n = (int)satunnainen_alle(&s, 8);
        int m = (int)satunnainen_alle(&s, 8);
        for (int i = 0; i < n; i++) {
            a[i] = (char)('a' + satunnainen_alle(&s, 3));
        }
        for (int i = 0; i < m; i++) {
            b[i] = (char)('a' + satunnainen_alle(&s, 3));
        }
        a[n] = b[m] = '\0';
        virheita += etaisyys(a, b) != raaka(a, b);
    }
    printf("raakatesti: 300 paria, %d virhettä\n", virheita);
    return EXIT_SUCCESS;
}
