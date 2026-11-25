// Kasvava rengaspuskuri eli pakka: lisäys ja poisto vakioajassa
// kummastakin päästä. Kun puskuri täyttyy, alkiot kopioidaan uuteen,
// kaksi kertaa suurempaan taulukkoon loogisessa järjestyksessä.
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "satunnainen.h"

// @alku pakka
typedef struct {
    int *data;
    size_t kapasiteetti;        // 0 tai kahden potenssi
    size_t alku;                // ensimmäisen alkion paikka
    size_t maara;
} Pakka;

// Looginen paikka i on taulukon paikka (alku + i) mod kapasiteetti.
static size_t paikka(const Pakka *p, size_t i)
{
    return (p->alku + i) & (p->kapasiteetti - 1);
}

// Sudenkuoppa: realloc ei riitä. Jos data kiertää taulukon reunan
// yli, alkuosa jäisi vanhan taulukon loppuun ja uusi tila tulisi
// keskelle jonoa. Alkiot kopioidaan siksi yksi kerrallaan loogisessa
// järjestyksessä uuden taulukon alkuun.
static bool kasvata(Pakka *p)
{
    size_t uusi = p->kapasiteetti ? 2 * p->kapasiteetti : 8;
    int *data = malloc(uusi * sizeof *data);
    if (data == nullptr) {
        return false;
    }
    for (size_t i = 0; i < p->maara; i++) {
        data[i] = p->data[paikka(p, i)];
    }
    free(p->data);
    p->data = data;
    p->kapasiteetti = uusi;
    p->alku = 0;
    return true;
}

static bool lisaa_loppuun(Pakka *p, int arvo)
{
    if (p->maara == p->kapasiteetti && !kasvata(p)) {
        return false;
    }
    p->data[paikka(p, p->maara++)] = arvo;
    return true;
}

static bool lisaa_alkuun(Pakka *p, int arvo)
{
    if (p->maara == p->kapasiteetti && !kasvata(p)) {
        return false;
    }
    p->alku = (p->alku - 1) & (p->kapasiteetti - 1);   // kiertää taakse
    p->data[p->alku] = arvo;
    p->maara++;
    return true;
}

static int poista_alusta(Pakka *p)          // kutsuja varmistaa maara > 0
{
    int arvo = p->data[p->alku];
    p->alku = paikka(p, 1);
    p->maara--;
    return arvo;
}

static int poista_lopusta(Pakka *p)
{
    return p->data[paikka(p, --p->maara)];
}
// @loppu pakka

// Taulukon sisältö paikoittain; vapaa paikka on -. Kirjan kuva
// kasvatuksesta piirretään näistä riveistä (kaaviot/tee.py).
static void nayta(const Pakka *p, const char *tila)
{
    printf("%s [", tila);
    for (size_t i = 0; i < p->kapasiteetti; i++) {
        bool kaytossa = ((i - p->alku) & (p->kapasiteetti - 1)) < p->maara;
        if (kaytossa) {
            printf("%d", p->data[i]);
        } else {
            printf("-");
        }
        printf("%s", i + 1 < p->kapasiteetti ? " " : "");
    }
    printf("] alku %zu, määrä %zu\n", p->alku, p->maara);
}

int main(void)
{
    // Jono, joka kiertää reunan yli ja täyttyy: 1..8 loogisessa
    // järjestyksessä, alku paikassa 5.
    Pakka p = {};
    bool ok = true;
    for (int i = 0; i < 5; i++) {
        ok &= lisaa_loppuun(&p, 0);
    }
    for (int i = 0; i < 5; i++) {
        poista_alusta(&p);
    }
    for (int i = 1; i <= 8; i++) {
        ok &= lisaa_loppuun(&p, i);
    }
    nayta(&p, "täysi:     ");
    ok &= lisaa_loppuun(&p, 9);
    nayta(&p, "kasvatettu:");

    // @alku vertailu
    // Vertailu referenssiin: tavallinen taulukko, jossa alkuun lisäys
    // ja alusta poisto siirtävät kaikkia alkioita.
    enum { RAJA = 4096 };
    static int ref[RAJA];
    size_t n = 0;
    Pakka q = {};
    Satunnainen s = {5};
    for (int kierros = 0; ok && kierros < 200000; kierros++) {
        int arvo = (int)satunnainen_alle(&s, 1000);
        // Painotus: lisäyksiä hieman enemmän, jotta kasvatus toistuu.
        switch (satunnainen_alle(&s, 5)) {
        case 0:
        case 1:
            if (n < RAJA) {
                ok &= lisaa_loppuun(&q, arvo);
                ref[n++] = arvo;
            }
            break;
        case 2:
            if (n < RAJA) {
                ok &= lisaa_alkuun(&q, arvo);
                memmove(ref + 1, ref, n * sizeof ref[0]);
                ref[0] = arvo;
                n++;
            }
            break;
        case 3:
            if (n > 0) {
                ok &= poista_alusta(&q) == ref[0];
                memmove(ref, ref + 1, --n * sizeof ref[0]);
            }
            break;
        default:
            if (n > 0) {
                ok &= poista_lopusta(&q) == ref[--n];
            }
        }
        ok &= q.maara == n
              && (n == 0 || q.data[paikka(&q, n / 2)] == ref[n / 2]);
    }
    printf("vertailutesti: 200000 operaatiota, %s, kapasiteetti lopussa "
           "%zu\n", ok ? "ei eroja" : "EROJA", q.kapasiteetti);
    // @loppu vertailu
    free(p.data);
    free(q.data);
    return ok ? EXIT_SUCCESS : EXIT_FAILURE;
}
