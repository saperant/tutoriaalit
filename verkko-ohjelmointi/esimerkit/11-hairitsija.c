// Vikojen injektointi: välityspalvelin asiakkaan ja palvelimen välissä
// pilkkoo tavuvirran 1-8 tavun paloiksi ja voi katkaista yhteyden
// kesken. Asiakkaan kehyskäsittelyn on kestettävä molemmat.
#define _GNU_SOURCE
#include <netinet/tcp.h>
#include <poll.h>

#include "verkko.h"

enum { VIESTEJA = 20, KATKAISU = 300 };
static uint16_t palvelin_portti, valittaja_portti;
static int palvelin_k, valittaja_k;

// Kaikupalvelin pituusetuliitteisille viesteille (luku 3).
static int palvelin(void *) {
    for (int i = 0; i < 2; i++) {
        int fd = (int)TARKISTA(accept(palvelin_k, nullptr, nullptr));
        uint32_t otsake;
        char data[256];
        while (lue_tasan(fd, &otsake, 4) == 1 &&
               ntohl(otsake) <= sizeof data &&
               lue_tasan(fd, data, ntohl(otsake)) == 1 &&
               kirjoita_kaikki(fd, &otsake, 4) == 0 &&
               kirjoita_kaikki(fd, data, ntohl(otsake)) == 0) {
        }
        close(fd);
    }
    return 0;
}

// @alku valittaja
// Välittää dataa kumpaankin suuntaan satunnaisina paloina. Jos raja > 0,
// yhteys katkaistaan, kun palvelimelta on välitetty raja tavua.
static void valita(int asiakas, int palvelin, long raja, satunnainen *s) {
    int paalla = 1;
    setsockopt(asiakas, IPPROTO_TCP, TCP_NODELAY, &paalla, sizeof paalla);
    setsockopt(palvelin, IPPROTO_TCP, TCP_NODELAY, &paalla, sizeof paalla);
    struct pollfd p[2] = {{.fd = asiakas, .events = POLLIN},
                          {.fd = palvelin, .events = POLLIN}};
    long valitetty = 0;
    for (;;) {
        TARKISTA(poll(p, 2, -1));
        for (int i = 0; i < 2; i++) {
            if (p[i].revents == 0) {
                continue;
            }
            char pala[8];
            size_t koko = 1 + satunnainen_alle(s, 8);
            if (i == 1 && raja > 0 && valitetty + (long)koko > raja) {
                koko = (size_t)(raja - valitetty);
            }
            ssize_t n = recv(p[i].fd, pala, koko, 0);
            if (n <= 0 || kirjoita_kaikki(p[1 - i].fd, pala, (size_t)n)) {
                return;                  // jompikumpi sulki
            }
            valitetty += i == 1 ? n : 0;
            if (raja > 0 && valitetty >= raja) {
                return;                  // vika: katkaisu kesken
            }
        }
    }
}

static int valittaja(void *) {
    satunnainen s = {5};
    long rajat[2] = {0, KATKAISU};
    for (int i = 0; i < 2; i++) {
        int a = (int)TARKISTA(accept(valittaja_k, nullptr, nullptr));
        int p = yhdista(palvelin_portti);
        valita(a, p, rajat[i], &s);
        close(a);
        close(p);
    }
    return 0;
}
// @loppu valittaja

// @alku asiakas
// Lähettää viestit ja tarkistaa kaiut. Palauttaa ehjinä saadut.
static int asiakas(int *virhe) {
    int fd = yhdista(valittaja_portti);
    int ehjia = 0;
    *virhe = 0;
    for (int i = 0; i < VIESTEJA; i++) {
        char data[256], kaiku[256];
        uint32_t koko = (uint32_t)(i * 13 % 200 + 1);
        memset(data, 'a' + i, koko);
        uint32_t otsake = htonl(koko), vastaus;
        TARKISTA(kirjoita_kaikki(fd, &otsake, 4));
        TARKISTA(kirjoita_kaikki(fd, data, koko));
        int t = lue_tasan(fd, &vastaus, 4);
        if (t == 1) {
            t = lue_tasan(fd, kaiku, koko);
        }
        if (t != 1) {
            *virhe = t == 0 ? EPROTO : errno;
            break;
        }
        ehjia += vastaus == otsake && memcmp(data, kaiku, koko) == 0;
    }
    close(fd);
    return ehjia;
}
// @loppu asiakas

int main(void) {
    vahtikoira();
    palvelin_k = kuuntele(&palvelin_portti);
    valittaja_k = kuuntele(&valittaja_portti);
    pid_t pa = kaynnista(palvelin, nullptr);
    pid_t pv = kaynnista(valittaja, nullptr);
    const char *nimet[2] = {"pilkkova", "katkaiseva"};
    for (int i = 0; i < 2; i++) {
        int virhe;
        int ehjia = asiakas(&virhe);
        printf("%-10s: %2d/%d viestiä ehjänä, %s\n", nimet[i], ehjia,
               VIESTEJA, virhe ? strerrorname_np(virhe) : "ei virheitä");
    }
    close(palvelin_k);
    close(valittaja_k);
    return odota(pv) | odota(pa);
}
