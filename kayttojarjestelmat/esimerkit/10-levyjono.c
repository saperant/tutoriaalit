// Levyn vuorontamisalgoritmit: missä järjestyksessä pyynnöt palvellaan,
// jotta lukupää liikkuu mahdollisimman vähän.
#include <stdio.h>
#include <stdlib.h>

// @alku algoritmit
enum { N = 8, MAKS = 200 };          // urat 0..199
typedef enum { FCFS, SSTF, SCAN, CLOOK } algoritmi_t;
static const char *const NIMET[] = {"FCFS", "SSTF", "SCAN", "C-LOOK"};

static int jarjestys(algoritmi_t a, const int *pyynnot, int paa,
                     int *ulos) {
    bool tehty[N] = {}, kaannytty = false;
    int liike = 0;
    for (int k = 0; k < N; k++) {
        int valittu = -1;
        for (int i = 0; i < N; i++) {
            if (tehty[i]) {
                continue;
            }
            int p = pyynnot[i], v = valittu < 0 ? 0 : pyynnot[valittu];
            bool parempi = valittu < 0;
            switch (a) {
            case FCFS: break;                    // saapumisjärjestys
            case SSTF:                           // lähin ensin
                parempi = parempi || abs(p - paa) < abs(v - paa);
                break;
            case SCAN:                           // ylöspäin, sitten alas
            case CLOOK: {                        // ylöspäin, sitten alusta
                bool py = p >= paa, vy = v >= paa;
                if (!parempi && py != vy) {
                    parempi = py;                // ylempänä olevat ensin
                } else if (!parempi && py) {
                    parempi = p < v;             // lähin ylempi
                } else if (!parempi) {
                    parempi = a == SCAN ? p > v : p < v;
                }
                break;
            }
            }
            if (parempi) {
                valittu = i;
            }
        }
        int kohde = pyynnot[valittu];
        if (a == SCAN && kohde < paa && !kaannytty) {
            liike += MAKS - 1 - paa;             // käydään levyn päässä
            paa = MAKS - 1;
            kaannytty = true;
        }
        liike += abs(kohde - paa);
        paa = kohde;
        tehty[valittu] = true;
        ulos[k] = kohde;
    }
    return liike;
}
// @loppu algoritmit

int main(void) {
    // @alku aja
    const int pyynnot[N] = {98, 183, 37, 122, 14, 124, 65, 67};
    const int paa = 53;
    printf("pää uralla %d, pyynnöt:", paa);
    for (int i = 0; i < N; i++) {
        printf(" %d", pyynnot[i]);
    }
    printf("\n");
    for (algoritmi_t a = FCFS; a <= CLOOK; a++) {
        int ulos[N];
        int liike = jarjestys(a, pyynnot, paa, ulos);
        printf("%-7s liike %3d:", NIMET[a], liike);
        for (int i = 0; i < N; i++) {
            printf(" %d", ulos[i]);
        }
        printf("\n");
    }
    // @loppu aja
    return 0;
}
