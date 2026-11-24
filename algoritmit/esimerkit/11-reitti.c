// Reitinhaku ruutukartalla leveyshaulla (BFS). Jokainen siirto
// naapuriruutuun maksaa saman verran, joten leveyshaku löytää lyhimmän
// reitin: se käsittelee ruudut etäisyyden mukaan kasvavassa
// järjestyksessä. Edeltäjätaulukosta reitti luetaan takaperin.
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

enum { K = 9, L = 25 };                 // kartan korkeus ja leveys

static char kartta[K][L + 1] = {
    "#########################",
    "#A....#.........#.......#",
    "#.###.#.#######.#.#####.#",
    "#...#...#.....#...#...#.#",
    "###.#####.###.#####.#.#.#",
    "#...#.....#.#.......#...#",
    "#.###.#####.#########.###",
    "#.....#.........#......B#",
    "#########################",
};

// @alku bfs
// Palauttaa lyhimmän reitin pituuden A:sta B:hen tai -1. Jono on
// taulukko, koska jokainen ruutu lisätään siihen enintään kerran.
static int leveyshaku(int ay, int ax, int by, int bx, int *kasiteltyja)
{
    static int etaisyys[K][L], edeltaja[K][L];
    static int jono[K * L];
    for (int y = 0; y < K; y++) {
        for (int x = 0; x < L; x++) {
            etaisyys[y][x] = -1;
        }
    }
    int alku = 0, loppu = 0;
    etaisyys[ay][ax] = 0;
    jono[loppu++] = ay * L + ax;
    while (alku < loppu) {
        int y = jono[alku] / L, x = jono[alku] % L;
        alku++;
        if (y == by && x == bx) {
            break;
        }
        static const int dy[] = { -1, 1, 0, 0 }, dx[] = { 0, 0, -1, 1 };
        for (int s = 0; s < 4; s++) {
            int ny = y + dy[s], nx = x + dx[s];
            if (kartta[ny][nx] != '#' && etaisyys[ny][nx] < 0) {
                etaisyys[ny][nx] = etaisyys[y][x] + 1;
                edeltaja[ny][nx] = y * L + x;
                jono[loppu++] = ny * L + nx;
            }
        }
    }
    *kasiteltyja = alku;
    // Merkitään reitti kartalle kulkemalla edeltäjiä B:stä A:han.
    if (etaisyys[by][bx] > 0) {
        for (int v = edeltaja[by][bx]; v != ay * L + ax;
             v = edeltaja[v / L][v % L]) {
            kartta[v / L][v % L] = '*';
        }
    }
    return etaisyys[by][bx];
}
// @loppu bfs

int main(void)
{
    int ay = 0, ax = 0, by = 0, bx = 0;
    for (int y = 0; y < K; y++) {
        for (int x = 0; x < L; x++) {
            if (kartta[y][x] == 'A') {
                ay = y;
                ax = x;
            } else if (kartta[y][x] == 'B') {
                by = y;
                bx = x;
            }
        }
    }
    int kasiteltyja;
    int pituus = leveyshaku(ay, ax, by, bx, &kasiteltyja);
    for (int y = 0; y < K; y++) {
        printf("%s\n", kartta[y]);
    }
    printf("reitin pituus %d askelta, käsiteltyjä ruutuja %d\n",
           pituus, kasiteltyja);
    return EXIT_SUCCESS;
}
