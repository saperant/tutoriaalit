// Binäärihakupuu: jokaisen solmun vasemmassa alipuussa on pienemmät
// ja oikeassa suuremmat avaimet. Haku, lisäys ja poisto kulkevat yhden
// polun juuresta alas, joten niiden hinta on puun korkeus.
#include <stdio.h>
#include <stdlib.h>

#include "satunnainen.h"

// @alku solmu
typedef struct solmu {
    int avain;
    struct solmu *vasen, *oikea;
} Solmu;
// @loppu solmu

// @alku lisaa
// Palauttaa false, jos muisti loppui. Jo olemassa oleva avain on ok.
static bool lisaa(Solmu **juuri, int avain)
{
    Solmu **p = juuri;
    while (*p != nullptr) {
        if (avain == (*p)->avain) {
            return true;
        }
        p = avain < (*p)->avain ? &(*p)->vasen : &(*p)->oikea;
    }
    *p = malloc(sizeof **p);
    if (*p == nullptr) {
        return false;
    }
    **p = (Solmu){avain, nullptr, nullptr};
    return true;
}

static bool sisaltaa(const Solmu *s, int avain)
{
    while (s != nullptr && s->avain != avain) {
        s = avain < s->avain ? s->vasen : s->oikea;
    }
    return s != nullptr;
}
// @loppu lisaa

// @alku poista
// Kolme tapausta: lehti tai yksi lapsi – solmu korvataan lapsellaan;
// kaksi lasta – avain korvataan seuraajalla (oikean alipuun pienin),
// ja seuraaja, jolla ei ole vasenta lasta, poistetaan.
static void poista(Solmu **juuri, int avain)
{
    Solmu **p = juuri;
    while (*p != nullptr && (*p)->avain != avain) {
        p = avain < (*p)->avain ? &(*p)->vasen : &(*p)->oikea;
    }
    Solmu *s = *p;
    if (s == nullptr) {
        return;
    }
    if (s->vasen != nullptr && s->oikea != nullptr) {
        Solmu **seuraaja = &s->oikea;
        while ((*seuraaja)->vasen != nullptr) {
            seuraaja = &(*seuraaja)->vasen;
        }
        s->avain = (*seuraaja)->avain;
        p = seuraaja;
        s = *p;
    }
    *p = s->vasen != nullptr ? s->vasen : s->oikea;
    free(s);
}
// @loppu poista

// @alku invariantti
// Jokaisen avaimen on oltava avoimella välillä (ala, yla), jonka
// esivanhemmat määräävät. Pelkkä vanhemman ja lapsen vertailu ei riitä.
static bool kunnossa(const Solmu *s, long ala, long yla)
{
    if (s == nullptr) {
        return true;
    }
    return ala < s->avain && s->avain < yla
           && kunnossa(s->vasen, ala, s->avain)
           && kunnossa(s->oikea, s->avain, yla);
}
// @loppu invariantti

static int korkeus(const Solmu *s)
{
    if (s == nullptr) {
        return 0;
    }
    int v = korkeus(s->vasen), o = korkeus(s->oikea);
    return 1 + (v > o ? v : o);
}

// @alku sisajarjestys
static void sisajarjestys(const Solmu *s)
{
    if (s != nullptr) {
        sisajarjestys(s->vasen);
        printf(" %d", s->avain);
        sisajarjestys(s->oikea);
    }
}
// @loppu sisajarjestys

static void vapauta(Solmu *s)
{
    if (s != nullptr) {
        vapauta(s->vasen);
        vapauta(s->oikea);
        free(s);
    }
}

int main(void)
{
    // Pieni puu: poistetaan solmu, jolla on kaksi lasta.
    Solmu *puu = nullptr;
    const int avaimet[] = {50, 30, 70, 20, 40, 60, 80, 35};
    for (size_t i = 0; i < sizeof avaimet / sizeof avaimet[0]; i++) {
        if (!lisaa(&puu, avaimet[i])) {
            return EXIT_FAILURE;
        }
    }
    printf("sisäjärjestys:");
    sisajarjestys(puu);
    poista(&puu, 30);
    printf("\n30 poistettu: ");
    sisajarjestys(puu);
    printf("\njuuren vasen lapsi nyt %d\n", puu->vasen->avain);
    vapauta(puu);

    // @alku korkeus
    // Sama 1000 avainta järjestyksessä ja satunnaisessa järjestyksessä.
    enum { N = 1000 };
    Solmu *jarjestys = nullptr, *satunnainen = nullptr;
    static int sekoitettu[N];
    for (int i = 0; i < N; i++) {
        sekoitettu[i] = i;
    }
    Satunnainen s = {11};
    for (int i = N - 1; i > 0; i--) {           // Fisher–Yates
        int j = (int)satunnainen_alle(&s, (uint32_t)i + 1);
        int apu = sekoitettu[i];
        sekoitettu[i] = sekoitettu[j];
        sekoitettu[j] = apu;
    }
    for (int i = 0; i < N; i++) {
        if (!lisaa(&jarjestys, i) || !lisaa(&satunnainen, sekoitettu[i])) {
            return EXIT_FAILURE;
        }
    }
    printf("korkeus, %d avainta järjestyksessä: %d\n", N,
           korkeus(jarjestys));
    printf("korkeus, %d avainta satunnaisesti:  %d\n", N,
           korkeus(satunnainen));
    // @loppu korkeus
    vapauta(jarjestys);
    vapauta(satunnainen);

    // @alku vertailu
    // Satunnaistettu vertailu totuusarvotaulukkoon.
    static bool mukana[512];
    Solmu *testi = nullptr;
    bool samat = true;
    for (int n = 0; n < 100000 && samat; n++) {
        int avain = (int)satunnainen_alle(&s, 512);
        switch (satunnainen_alle(&s, 3)) {
        case 0:
            samat = lisaa(&testi, avain);
            mukana[avain] = true;
            break;
        case 1:
            poista(&testi, avain);
            mukana[avain] = false;
            break;
        default:
            samat = sisaltaa(testi, avain) == mukana[avain];
        }
        samat = samat && kunnossa(testi, -1, 512);
    }
    printf("vertailutesti: 100000 operaatiota, %s\n",
           samat ? "ei eroja, invariantti voimassa" : "EROJA");
    // @loppu vertailu
    vapauta(testi);
    return samat ? EXIT_SUCCESS : EXIT_FAILURE;
}
