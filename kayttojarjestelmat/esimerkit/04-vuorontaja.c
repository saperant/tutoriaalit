// Vuorontamisalgoritmien simulaattori. Aika etenee yksikön kerrallaan,
// ja joka hetkellä algoritmi valitsee suoritettavan prosessin.
#include <stdio.h>
#include <string.h>

// @alku tyypit
typedef struct {
    char nimi;
    int saapuu, kesto, prioriteetti;     // pienempi = tärkeämpi
} prosessi_t;

typedef enum { FCFS, SJF, SRTF, RR, PRIO } algoritmi_t;
static const char *const NIMET[] = {"FCFS", "SJF", "SRTF", "RR q=2",
                                    "PRIO"};

enum { MAKS = 8, AIKAA = 64 };

typedef struct {
    int jono[MAKS], pituus;              // valmiusjono
    int jaljella[MAKS], valmis[MAKS];
    char aikajana[AIKAA + 1];
    int keskeytyksia;      // kesken vaihdettu prosessi
} tila_t;
// @loppu tyypit

static void lisaa(tila_t *t, int p, bool alkuun) {
    int kohta = alkuun ? 0 : t->pituus;
    memmove(&t->jono[kohta + 1], &t->jono[kohta],
            (size_t)(t->pituus - kohta) * sizeof t->jono[0]);
    t->jono[kohta] = p;
    t->pituus++;
}

static void poista(tila_t *t, int kohta) {
    memmove(&t->jono[kohta], &t->jono[kohta + 1],
            (size_t)(t->pituus - kohta - 1) * sizeof t->jono[0]);
    t->pituus--;
}

// @alku valitse
// Palauttaa valitun prosessin paikan valmiusjonossa.
static int valitse(algoritmi_t a, const tila_t *t,
                   const prosessi_t *p) {
    int paras = 0;
    for (int i = 1; i < t->pituus; i++) {
        int x = t->jono[i], y = t->jono[paras];
        bool parempi = false;
        switch (a) {
        case FCFS: case RR: break;                  // jonon kärki
        case SJF:  parempi = p[x].kesto < p[y].kesto; break;
        case SRTF: parempi = t->jaljella[x] < t->jaljella[y]; break;
        case PRIO: parempi = p[x].prioriteetti < p[y].prioriteetti;
                   break;
        }
        if (parempi) {
            paras = i;
        }
    }
    return paras;
}
// @loppu valitse

// @alku simuloi
static void simuloi(algoritmi_t a, const prosessi_t *p, int n,
                    tila_t *t) {
    *t = (tila_t){};
    for (int i = 0; i < n; i++) {
        t->jaljella[i] = p[i].kesto;
    }
    int ajossa = -1, edellinen = -1, kvantti = 0, valmiita = 0;
    for (int aika = 0; valmiita < n && aika < AIKAA; aika++) {
        for (int i = 0; i < n; i++) {    // saapujat jonon perälle
            if (p[i].saapuu == aika) {
                lisaa(t, i, false);
            }
        }
        // Keskeyttävät algoritmit vertaavat ajossa olevaa muihin
        // joka hetki; jonon kärjessä se voittaa tasapelit.
        if (ajossa >= 0 && (a == SRTF || a == PRIO)) {
            lisaa(t, ajossa, true);
            ajossa = -1;
        } else if (ajossa >= 0 && a == RR && kvantti == 2) {
            lisaa(t, ajossa, false);     // kvantti täynnä: perälle
            ajossa = -1;
        }
        if (ajossa < 0 && t->pituus > 0) {
            int kohta = valitse(a, t, p);
            ajossa = t->jono[kohta];
            poista(t, kohta);
            kvantti = 0;
            t->keskeytyksia += edellinen >= 0 && ajossa != edellinen;
        }
        if (ajossa < 0) {
            t->aikajana[aika] = '-';     // suoritin joutilaana
            continue;
        }
        t->aikajana[aika] = p[ajossa].nimi;
        kvantti++;
        edellinen = ajossa;
        if (--t->jaljella[ajossa] == 0) {
            t->valmis[ajossa] = aika + 1;
            valmiita++;
            ajossa = edellinen = -1;
        }
    }
}
// @loppu simuloi

int main(void) {
    // @alku data
    const prosessi_t p[] = {
        {'A', 0, 7, 3}, {'B', 2, 4, 1}, {'C', 4, 1, 4}, {'D', 5, 4, 2},
    };
    // @loppu data
    const int n = sizeof p / sizeof p[0];
    printf("        aikajana           odotus ka. läpimeno ka. "
           "keskeytyksiä\n");
    for (algoritmi_t a = FCFS; a <= PRIO; a++) {
        tila_t t;
        simuloi(a, p, n, &t);
        int odotus = 0, lapimeno = 0;
        for (int i = 0; i < n; i++) {
            lapimeno += t.valmis[i] - p[i].saapuu;
            odotus += t.valmis[i] - p[i].saapuu - p[i].kesto;
        }
        printf("%-7s %-18s %10.2f %12.2f %12d\n", NIMET[a], t.aikajana,
               (double)odotus / n, (double)lapimeno / n, t.keskeytyksia);
    }
    return 0;
}
