// diff-työkalun ydin: kahden tiedostoversion rivien pisin yhteinen
// osajono kertoo, mitkä rivit pysyivät ennallaan. Muut rivit on
// poistettu (-) tai lisätty (+). Taulukko lasketaan loppuosille, jotta
// muutokset voidaan tulostaa alusta loppuun.
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

enum { MAX_RIVEJA = 64 };

// @alku diff
static void diff(const char *const *a, int n, const char *const *b, int m)
{
    // p[i][j] = loppuosien a[i..n) ja b[j..m) LCS:n pituus.
    static int p[MAX_RIVEJA + 1][MAX_RIVEJA + 1];
    for (int i = n; i >= 0; i--) {
        for (int j = m; j >= 0; j--) {
            if (i == n || j == m) {
                p[i][j] = 0;
            } else if (strcmp(a[i], b[j]) == 0) {
                p[i][j] = p[i + 1][j + 1] + 1;
            } else {
                p[i][j] = p[i + 1][j] > p[i][j + 1] ? p[i + 1][j]
                                                    : p[i][j + 1];
            }
        }
    }
    int poistoja = 0, lisayksia = 0;
    int i = 0, j = 0;
    while (i < n || j < m) {
        if (i < n && j < m && strcmp(a[i], b[j]) == 0) {
            printf("  %s\n", a[i++]);
            j++;
        } else if (j == m || (i < n && p[i + 1][j] >= p[i][j + 1])) {
            printf("- %s\n", a[i++]);
            poistoja++;
        } else {
            printf("+ %s\n", b[j++]);
            lisayksia++;
        }
    }
    printf("ennallaan %d, poistettu %d, lisätty %d\n",
           p[0][0], poistoja, lisayksia);
}
// @loppu diff

int main(void)
{
    const char *const vanha[] = {
        "[palvelin]",
        "osoite = 0.0.0.0",
        "portti = 8080",
        "lokitaso = info",
        "# tietokanta",
        "[tietokanta]",
        "nimi = kurssit",
        "yhteyksia = 10",
    };
    const char *const uusi[] = {
        "[palvelin]",
        "osoite = 0.0.0.0",
        "portti = 8443",
        "tls = kylla",
        "lokitaso = info",
        "# tietokanta",
        "[tietokanta]",
        "nimi = kurssit",
        "yhteyksia = 25",
        "aikakatkaisu = 30",
    };
    diff(vanha, 8, uusi, 10);
    return EXIT_SUCCESS;
}
