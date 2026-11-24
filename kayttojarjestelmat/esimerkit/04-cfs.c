// CFS:n periaate: suoritetaan aina sitä tehtävää, jonka virtuaaliaika
// on pienin. Virtuaaliaika kasvaa sitä hitaammin, mitä suurempi
// tehtävän paino (pienempi nice-arvo) on.
#include <stdio.h>

// @alku paino
// Ytimen taulukosta (sched_prio_to_weight): nice 0 = 1024, ja jokainen
// nice-askel muuttaa painoa noin 1,25-kertaisesti.
static int paino(int nice) {
    static const int painot[] = {3121, 2501, 1991, 1586, 1277, 1024,
                                 820,  655,  526,  423,  335};
    return painot[nice + 5];             // nice -5 ... 5
}

typedef struct {
    char nimi;
    int nice;
    long long vaika;                     // virtuaaliaika, ns
    long long ajettu;                    // todellinen aika, ms
    bool mukana;
} tehtava_t;
// @loppu paino

enum { N = 4, VIIPALE_MS = 1 };

// @alku valitse
static int valitse(const tehtava_t *t) {
    int paras = -1;
    for (int i = 0; i < N; i++) {
        if (t[i].mukana && (paras < 0 || t[i].vaika < t[paras].vaika)) {
            paras = i;
        }
    }
    return paras;
}

static void aja(tehtava_t *t, int ms) {
    for (int k = 0; k < ms; k++) {
        tehtava_t *v = &t[valitse(t)];
        v->ajettu += VIIPALE_MS;
        v->vaika += VIIPALE_MS * 1'000'000LL * 1024 / paino(v->nice);
    }
}
// @loppu valitse

static void tulosta(const char *otsikko, tehtava_t *t, int ms) {
    printf("%s\n", otsikko);
    for (int i = 0; i < N; i++) {
        if (t[i].mukana) {
            printf("  %c nice %2d paino %4d: %4lld ms (%4.1f %%)\n",
                   t[i].nimi, t[i].nice, paino(t[i].nice), t[i].ajettu,
                   100.0 * (double)t[i].ajettu / ms);
        }
        t[i].ajettu = 0;
    }
}

int main(void) {
    // @alku aja
    tehtava_t t[N] = {
        {'A', 0, 0, 0, true}, {'B', 0, 0, 0, true},
        {'C', 5, 0, 0, true}, {'D', -5, 0, 0, false},
    };
    aja(t, 1000);
    tulosta("A, B ja C sekunnin ajan:", t, 1000);

    // Uusi tehtävä aloittaa pienimmästä virtuaaliajasta. Nollasta
    // aloittaessaan se saisi suorittimen yksin pitkäksi aikaa.
    long long pienin = t[valitse(t)].vaika;
    t[3].mukana = true;
    t[3].vaika = pienin;
    aja(t, 1000);
    tulosta("D (nice -5) mukaan:", t, 1000);
    // @loppu aja
    return 0;
}
