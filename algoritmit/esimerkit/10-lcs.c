// Pisin yhteinen osajono (LCS): pisin jono, joka saadaan kummastakin
// merkkijonosta poistamalla merkkejä järjestystä muuttamatta. Taulukko
// p[i][j] on alkuosien a[0..i) ja b[0..j) LCS:n pituus. Tulos
// tarkistetaan raa'alla haulla, joka kokeilee a:n kaikki osajonot.
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "satunnainen.h"

enum { MAX = 64 };

// @alku lcs
// p[i][j] = p[i-1][j-1] + 1,              jos a[i-1] == b[j-1]
//         = max(p[i-1][j], p[i][j-1]),    muuten
// Rekonstruktio kulkee taulukon oikeasta alakulmasta takaisin alkuun.
static int p[MAX + 1][MAX + 1];

static int lcs(const char *a, const char *b, char *tulos)
{
    int n = (int)strlen(a), m = (int)strlen(b);
    for (int i = 0; i <= n; i++) {
        for (int j = 0; j <= m; j++) {
            if (i == 0 || j == 0) {
                p[i][j] = 0;
            } else if (a[i - 1] == b[j - 1]) {
                p[i][j] = p[i - 1][j - 1] + 1;
            } else {
                p[i][j] = p[i - 1][j] > p[i][j - 1] ? p[i - 1][j]
                                                    : p[i][j - 1];
            }
        }
    }
    int k = p[n][m];
    tulos[k] = '\0';
    for (int i = n, j = m; i > 0 && j > 0;) {
        if (a[i - 1] == b[j - 1]) {
            tulos[--k] = a[i - 1];
            i--;
            j--;
        } else if (p[i - 1][j] >= p[i][j - 1]) {
            i--;
        } else {
            j--;
        }
    }
    return p[n][m];
}
// @loppu lcs

// Tulostaa lcs-kutsun täyttämän taulukon ja merkitsee tähdellä
// ruudut, joiden kautta rekonstruktio kulkee. Kirjan kuva piirretään
// tästä tulosteesta (kaaviot/tee.py).
static void tulosta_taulukko(const char *a, const char *b)
{
    int n = (int)strlen(a), m = (int)strlen(b);
    static bool polku[MAX + 1][MAX + 1];
    memset(polku, 0, sizeof polku);
    int i = n, j = m;
    polku[i][j] = true;
    while (i > 0 && j > 0) {                // sama sääntö kuin lcs:ssä
        if (a[i - 1] == b[j - 1]) {
            i--;
            j--;
        } else if (p[i - 1][j] >= p[i][j - 1]) {
            i--;
        } else {
            j--;
        }
        polku[i][j] = true;
    }
    printf("taulukko %s / %s, rekonstruktion polku tähdellä:\n     -", a, b);
    for (j = 0; j < m; j++) {
        printf("  %c", b[j]);
    }
    printf("\n");
    for (i = 0; i <= n; i++) {
        printf("  %c", i == 0 ? '-' : a[i - 1]);
        for (j = 0; j <= m; j++) {
            printf(" %c%d", polku[i][j] ? '*' : ' ', p[i][j]);
        }
        printf("\n");
    }
}

static bool osajono(const char *x, const char *y)   // onko x y:n osajono?
{
    for (; *y != '\0'; y++) {
        if (*x == *y) {
            x++;
        }
    }
    return *x == '\0';
}

static int raaka(const char *a, const char *b)
{
    int n = (int)strlen(a), paras = 0;
    char x[MAX + 1];
    for (unsigned joukko = 0; joukko < (1u << n); joukko++) {
        int k = 0;
        for (int i = 0; i < n; i++) {
            if (joukko >> i & 1) {
                x[k++] = a[i];
            }
        }
        x[k] = '\0';
        if (k > paras && osajono(x, b)) {
            paras = k;
        }
    }
    return paras;
}

int main(void)
{
    char tulos[MAX + 1];
    const char *parit[][2] = {
        { "ALGORITMI", "LOGARITMI" },
        { "GCATGCGTA", "GATTACAGC" },
        { "kissa", "koira" },
    };
    for (int i = 0; i < 3; i++) {
        int k = lcs(parit[i][0], parit[i][1], tulos);
        printf("%-10s %-10s %d %s\n", parit[i][0], parit[i][1], k, tulos);
    }
    tulosta_taulukko(parit[2][0], parit[2][1]);     // viimeisin lcs-kutsu

    Satunnainen s = { 31 };
    int virheita = 0;
    for (int k = 0; k < 500; k++) {
        char a[13], b[13];
        int n = (int)satunnainen_alle(&s, 13);
        int m = (int)satunnainen_alle(&s, 13);
        for (int i = 0; i < n; i++) {
            a[i] = (char)('A' + satunnainen_alle(&s, 4));
        }
        for (int i = 0; i < m; i++) {
            b[i] = (char)('A' + satunnainen_alle(&s, 4));
        }
        a[n] = b[m] = '\0';
        int pituus = lcs(a, b, tulos);
        // Pituus on optimi, ja jono on todella molempien osajono.
        if (pituus != raaka(a, b) || (int)strlen(tulos) != pituus ||
            !osajono(tulos, a) || !osajono(tulos, b)) {
            virheita++;
        }
    }
    printf("raakatesti: 500 paria, %d virhettä\n", virheita);
    return EXIT_SUCCESS;
}
