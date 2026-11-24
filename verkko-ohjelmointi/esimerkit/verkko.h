// Esimerkkien yhteiset apufunktiot: virheentarkistus, kokonaiset luvut
// ja kirjoitukset, silmukkaosoitteen palvelin ja asiakas sekä
// testiprosessit. Otsake kelpaa sekä C23:lle että C++23:lle.
#ifndef VERKKO_H
#define VERKKO_H

#include <arpa/inet.h>
#include <errno.h>
#include <netinet/in.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/prctl.h>
#include <sys/socket.h>
#include <sys/wait.h>
#include <unistd.h>

// @alku tarkista
// POSIX-kutsut palauttavat virheessä -1 ja asettavat errno-muuttujan.
static inline long tarkista_(long arvo, const char *kutsu, int rivi) {
    if (arvo == -1) {
        fprintf(stderr, "rivi %d: %s: %s\n", rivi, kutsu,
                strerror(errno));
        exit(EXIT_FAILURE);
    }
    return arvo;
}
#define TARKISTA(kutsu) tarkista_((long)(kutsu), #kutsu, __LINE__)
// @loppu tarkista

// @alku kaikki
// Kirjoittaa koko puskurin. send voi kirjoittaa vähemmän kuin pyydettiin
// (estämätön soketti, signaali), joten loput kirjoitetaan silmukassa.
// MSG_NOSIGNAL: katkennut yhteys palauttaa EPIPE eikä tapa prosessia.
static inline int kirjoita_kaikki(int fd, const void *data, size_t n) {
    const char *p = (const char *)data;
    while (n > 0) {
        ssize_t k = send(fd, p, n, MSG_NOSIGNAL);
        if (k == -1) {
            if (errno == EINTR) {
                continue;
            }
            return -1;
        }
        p += k;
        n -= (size_t)k;
    }
    return 0;
}

// Lukee täsmälleen n tavua. Palauttaa 1, kun kaikki saatiin, 0, jos
// yhteys sulkeutui siististi ennen ensimmäistä tavua, ja -1 virheessä.
// Sulkeutuminen kesken viestin on virhe (errno = EPROTO).
static inline int lue_tasan(int fd, void *data, size_t n) {
    char *p = (char *)data;
    size_t saatu = 0;
    while (saatu < n) {
        ssize_t k = recv(fd, p + saatu, n - saatu, 0);
        if (k == 0) {
            if (saatu == 0) {
                return 0;
            }
            errno = EPROTO;
            return -1;
        }
        if (k == -1) {
            if (errno == EINTR) {
                continue;
            }
            return -1;
        }
        saatu += (size_t)k;
    }
    return 1;
}
// @loppu kaikki

// @alku kuuntele
// Palvelinsoketti silmukkaosoitteeseen 127.0.0.1. Portti 0 pyytää
// ytimeltä vapaan portin, ja getsockname kertoo, minkä se valitsi.
static inline int kuuntele(uint16_t *portti) {
    int fd = (int)TARKISTA(socket(AF_INET, SOCK_STREAM, 0));
    struct sockaddr_in osoite = {};
    osoite.sin_family = AF_INET;
    osoite.sin_port = htons(0);
    osoite.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    TARKISTA(bind(fd, (struct sockaddr *)&osoite, sizeof osoite));
    TARKISTA(listen(fd, SOMAXCONN));
    socklen_t pituus = sizeof osoite;
    TARKISTA(getsockname(fd, (struct sockaddr *)&osoite, &pituus));
    *portti = ntohs(osoite.sin_port);
    return fd;
}

// Asiakassoketti, joka on yhdistetty porttiin 127.0.0.1:portti.
static inline int yhdista(uint16_t portti) {
    int fd = (int)TARKISTA(socket(AF_INET, SOCK_STREAM, 0));
    struct sockaddr_in osoite = {};
    osoite.sin_family = AF_INET;
    osoite.sin_port = htons(portti);
    osoite.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    TARKISTA(connect(fd, (struct sockaddr *)&osoite, sizeof osoite));
    return fd;
}
// @loppu kuuntele

// @alku prosessit
// Ajaa funktion lapsiprosessissa. Lapsi kuolee, jos vanhempi kuolee
// (PR_SET_PDEATHSIG), ja vahtikoira lopettaa sen, jos se jumiutuu.
static inline pid_t kaynnista(int (*tehtava)(void *), void *arg) {
    fflush(stdout);                  // muuten puskuri tulostuu kahdesti
    pid_t pid = (pid_t)TARKISTA(fork());
    if (pid == 0) {
        TARKISTA(prctl(PR_SET_PDEATHSIG, SIGKILL));
        alarm(20);
        int koodi = tehtava(arg);
        fflush(stdout);
        _exit(koodi);
    }
    return pid;
}

// Odottaa lapsen päättymisen. Palauttaa lapsen paluuarvon, tai -1, jos
// signaali lopetti lapsen.
static inline int odota(pid_t pid) {
    int tila;
    while (waitpid(pid, &tila, 0) == -1) {
        if (errno != EINTR) {
            perror("waitpid");
            exit(EXIT_FAILURE);
        }
    }
    if (WIFSIGNALED(tila)) {
        fprintf(stderr, "lapsi kuoli signaaliin %d\n", WTERMSIG(tila));
        return -1;
    }
    return WEXITSTATUS(tila);
}
// @loppu prosessit

// Testin vahtikoira: jumiutunut esimerkki kaatuu eikä jää odottamaan.
static inline void vahtikoira(void) { alarm(30); }

// @alku satunnainen
// Toistettava näennäissatunnaisuus (xorshift64*): sama siemen antaa joka
// koneella saman jonon. Käytetään häviöiden ja sumean syötteen tuottoon.
typedef struct { uint64_t tila; } satunnainen;

static inline uint64_t satunnaisluku(satunnainen *s) {
    s->tila ^= s->tila >> 12;
    s->tila ^= s->tila << 25;
    s->tila ^= s->tila >> 27;
    return s->tila * 0x2545F4914F6CDD1DULL;
}

// Tasajakautunut luku väliltä [0, n). Pieni vinouma ei haittaa tässä.
static inline uint32_t satunnainen_alle(satunnainen *s, uint32_t n) {
    return (uint32_t)(satunnaisluku(s) >> 32) % n;
}
// @loppu satunnainen

#endif
