// Lukkiutumisen havaitseminen ja välttäminen: resurssien
// varausgraafin syklin etsintä ja pankkiirin algoritmi.
#include <stdio.h>
#include <string.h>

// @alku graafi
// Odotusgraafi: odottaa[i][j] = prosessi i odottaa resurssia, jota
// prosessi j pitää. Sykli = lukkiutuminen (kun resursseja on yksi
// kutakin).
enum { P = 4 };

// @alku sykli
static bool syvyyshaku(bool odottaa[P][P], int i, int tila[P],
                       int polku[P], int *pituus) {
    tila[i] = 1;                         // 1 = polulla, 2 = valmis
    polku[(*pituus)++] = i;
    for (int j = 0; j < P; j++) {
        if (!odottaa[i][j]) {
            continue;
        }
        if (tila[j] == 1) {              // takaisin polulle: sykli
            polku[(*pituus)++] = j;
            return true;
        }
        if (tila[j] == 0 && syvyyshaku(odottaa, j, tila, polku, pituus)) {
            return true;
        }
    }
    tila[i] = 2;
    (*pituus)--;
    return false;
}
// @loppu sykli

static void tarkista(const char *nimi, bool odottaa[P][P]) {
    int tila[P] = {}, polku[P + 1], pituus = 0;
    for (int i = 0; i < P; i++) {
        if (tila[i] == 0 && syvyyshaku(odottaa, i, tila, polku, &pituus)) {
            int alku = 0;                // sykli alkaa toistuvasta
            while (polku[alku] != polku[pituus - 1]) {
                alku++;
            }
            printf("%s: lukkiutuma", nimi);
            for (int k = alku; k < pituus; k++) {
                printf("%s P%d", k > alku ? " ->" : "", polku[k]);
            }
            printf("\n");
            return;
        }
    }
    printf("%s: ei syklejä\n", nimi);
}
// @loppu graafi

// @alku pankkiiri
enum { N = 5, R = 3 };

// @alku turvallinen
// Turvallinen tila: on järjestys, jossa jokainen prosessi saa
// enimmäistarpeensa ja päättyy, vapauttaen resurssinsa seuraaville.
static bool turvallinen(const int vapaa[R], const int varattu[N][R],
                        const int tarve[N][R], int jarjestys[N]) {
    int tyo[R];
    bool valmis[N] = {};
    memcpy(tyo, vapaa, sizeof tyo);
    for (int k = 0; k < N; k++) {
        int loytyi = -1;
        for (int i = 0; i < N && loytyi < 0; i++) {
            bool riittaa = !valmis[i];
            for (int r = 0; r < R && riittaa; r++) {
                riittaa = tarve[i][r] <= tyo[r];
            }
            if (riittaa) {
                loytyi = i;
            }
        }
        if (loytyi < 0) {
            return false;                // kukaan ei voi edetä
        }
        for (int r = 0; r < R; r++) {
            tyo[r] += varattu[loytyi][r];    // päättyy ja vapauttaa
        }
        valmis[loytyi] = true;
        jarjestys[k] = loytyi;
    }
    return true;
}
// @loppu turvallinen

// Pyyntö myönnetään vain, jos tila pysyy turvallisena.
static bool pyyda(int vapaa[R], int varattu[N][R], int tarve[N][R],
                  int p, const int pyynto[R]) {
    for (int r = 0; r < R; r++) {
        if (pyynto[r] > tarve[p][r] || pyynto[r] > vapaa[r]) {
            return false;
        }
    }
    for (int r = 0; r < R; r++) {        // kokeillaan
        vapaa[r] -= pyynto[r];
        varattu[p][r] += pyynto[r];
        tarve[p][r] -= pyynto[r];
    }
    int j[N];
    if (turvallinen(vapaa, varattu, tarve, j)) {
        return true;
    }
    for (int r = 0; r < R; r++) {        // perutaan
        vapaa[r] += pyynto[r];
        varattu[p][r] -= pyynto[r];
        tarve[p][r] += pyynto[r];
    }
    return false;
}
// @loppu pankkiiri

static void tulosta_jarjestys(const int vapaa[R], const int varattu[N][R],
                              const int tarve[N][R]) {
    int j[N];
    if (turvallinen(vapaa, varattu, tarve, j)) {
        printf("turvallinen, järjestys:");
        for (int k = 0; k < N; k++) {
            printf(" P%d", j[k]);
        }
        printf("\n");
    } else {
        printf("ei turvallinen\n");
    }
}

int main(void) {
    // @alku aja
    bool ketju[P][P] = {{[1] = true}, {[2] = true}, {[3] = true}, {}};
    bool rengas[P][P] = {{[1] = true}, {[2] = true}, {[0] = true}, {}};
    tarkista("ketju", ketju);
    tarkista("rengas", rengas);

    int vapaa[R] = {3, 3, 2};
    int varattu[N][R] = {{0, 1, 0}, {2, 0, 0}, {3, 0, 2},
                         {2, 1, 1}, {0, 0, 2}};
    int enimmillaan[N][R] = {{7, 5, 3}, {3, 2, 2}, {9, 0, 2},
                             {2, 2, 2}, {4, 3, 3}};
    int tarve[N][R];
    for (int i = 0; i < N; i++) {
        for (int r = 0; r < R; r++) {
            tarve[i][r] = enimmillaan[i][r] - varattu[i][r];
        }
    }
    printf("alkutila: ");
    tulosta_jarjestys(vapaa, varattu, tarve);
    printf("P1 pyytää (1,0,2): %s\n",
           pyyda(vapaa, varattu, tarve, 1, (int[R]){1, 0, 2})
               ? "myönnetty" : "odottaa");
    printf("P4 pyytää (3,3,0): %s\n",
           pyyda(vapaa, varattu, tarve, 4, (int[R]){3, 3, 0})
               ? "myönnetty" : "odottaa");
    printf("P0 pyytää (0,2,0): %s\n",
           pyyda(vapaa, varattu, tarve, 0, (int[R]){0, 2, 0})
               ? "myönnetty" : "odottaa");
    printf("lopputila: ");
    tulosta_jarjestys(vapaa, varattu, tarve);
    // @loppu aja
    return 0;
}
