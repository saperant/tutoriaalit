// Sivunkorvausalgoritmit: FIFO, LRU, Clock (toinen mahdollisuus) ja
// optimaalinen OPT. Kukin laskee sivuvirheet viittausjonolle.
#include <stdio.h>
#include <string.h>

typedef enum { FIFO, LRU, CLOCK, OPT } algoritmi_t;
static const char *const NIMET[] = {"FIFO", "LRU", "Clock", "OPT"};
enum { MAKS_KEHYKSIA = 8, TYHJA = -1 };

// @alku tila
typedef struct {
    int sivu[MAKS_KEHYKSIA];         // kehyksen sivu tai TYHJA
    long viimeksi[MAKS_KEHYKSIA];    // LRU: viimeisin käyttöhetki
    bool kaytetty[MAKS_KEHYKSIA];    // Clock: käyttöbitti
    int n, osoitin;                  // FIFO ja Clock: kiertävä osoitin
} kehykset_t;
// @loppu tila

// @alku uhri
// Valitsee korvattavan kehyksen. Jono ja kohta tarvitaan vain OPT:lle,
// joka katsoo tulevaisuuteen eikä siksi ole toteutettavissa.
static int uhri(algoritmi_t a, kehykset_t *k, const int *jono, int pit,
                int kohta) {
    int valittu = 0;
    switch (a) {
    case FIFO:
        valittu = k->osoitin;
        k->osoitin = (k->osoitin + 1) % k->n;
        break;
    case LRU:
        for (int i = 1; i < k->n; i++) {
            if (k->viimeksi[i] < k->viimeksi[valittu]) {
                valittu = i;
            }
        }
        break;
    case CLOCK:
        while (k->kaytetty[k->osoitin]) {    // toinen mahdollisuus
            k->kaytetty[k->osoitin] = false;
            k->osoitin = (k->osoitin + 1) % k->n;
        }
        valittu = k->osoitin;
        k->osoitin = (k->osoitin + 1) % k->n;
        break;
    case OPT: {
        int kaukaisin = -1;              // seuraava käyttö kauimpana
        for (int i = 0; i < k->n; i++) {
            int seur = kohta + 1;
            while (seur < pit && jono[seur] != k->sivu[i]) {
                seur++;
            }
            if (seur > kaukaisin) {
                kaukaisin = seur;
                valittu = i;
            }
        }
        break;
    }
    }
    return valittu;
}
// @loppu uhri

// @alku aja
static int sivuvirheet(algoritmi_t a, const int *jono, int pit,
                       int kehyksia, bool jalki) {
    kehykset_t k = {.n = kehyksia};
    memset(k.sivu, TYHJA, sizeof k.sivu);
    int virheita = 0;
    for (int t = 0; t < pit; t++) {
        int i = 0;
        while (i < k.n && k.sivu[i] != jono[t]) {
            i++;
        }
        bool virhe = i == k.n;
        if (virhe) {                     // sivuvirhe: tyhjä tai uhri
            virheita++;
            i = 0;
            while (i < k.n && k.sivu[i] != TYHJA) {
                i++;
            }
            if (i == k.n) {
                i = uhri(a, &k, jono, pit, t);
            } else if (a == FIFO || a == CLOCK) {
                k.osoitin = (i + 1) % k.n;
            }
            k.sivu[i] = jono[t];
        }
        k.viimeksi[i] = t;
        k.kaytetty[i] = true;
        if (jalki) {
            printf("%2d:", jono[t]);
            for (int j = 0; j < k.n; j++) {
                if (k.sivu[j] == TYHJA) {
                    printf("  .");
                } else {
                    printf(" %2d", k.sivu[j]);
                }
            }
            printf("%s\n", virhe ? "  *" : "");
        }
    }
    return virheita;
}
// @loppu aja

static void taulukko(const char *nimi, const int *jono, int pit) {
    printf("%s:", nimi);
    for (int i = 0; i < pit; i++) {
        printf(" %d", jono[i]);
    }
    printf("\nkehyksiä");
    for (algoritmi_t a = FIFO; a <= OPT; a++) {
        printf(" %5s", NIMET[a]);
    }
    printf("\n");
    for (int k = 1; k <= 5; k++) {
        printf("%8d", k);
        for (algoritmi_t a = FIFO; a <= OPT; a++) {
            printf(" %5d", sivuvirheet(a, jono, pit, k, false));
        }
        printf("\n");
    }
}

int main(void) {
    // @alku jonot
    const int perus[] = {7, 0, 1, 2, 0, 3, 0, 4, 2, 3,
                         0, 3, 2, 1, 2, 0, 1, 7, 0, 1};
    const int belady[] = {1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5};
    const int silmukka[] = {1, 2, 3, 4, 1, 2, 3, 4, 1, 2, 3, 4};
    // @loppu jonot
    taulukko("perusjono", perus, sizeof perus / sizeof perus[0]);
    taulukko("\nBeladyn jono", belady, sizeof belady / sizeof belady[0]);
    taulukko("\nsilmukka", silmukka, sizeof silmukka / sizeof silmukka[0]);
    printf("\nClock, 3 kehystä, perusjonon alku (* = sivuvirhe):\n");
    sivuvirheet(CLOCK, perus, 10, 3, true);
    return 0;
}
