// Tapahtumasilmukka takaisinkutsuilla: epoll kertoo valmiit kuvaajat ja
// silmukka kutsuu niihin rekisteröidyt käsittelijät. Lähtevä data
// puskuroidaan, kun ydin ei ota enempää (EAGAIN), ja joutilas yhteys
// suljetaan ajastimella (timerfd).
#define _GNU_SOURCE
#include <fcntl.h>
#include <sys/epoll.h>
#include <sys/timerfd.h>

#include "verkko.h"

enum { MAARA = 4 << 20, RAJA = 1 << 20 };  // 4 MiB vastaus, 1 MiB raja
static uint16_t portti;

// @alku silmukka
typedef struct silmukka silmukka;
typedef void (*kasittelija)(silmukka *, void *tila, uint32_t tapahtumat);

typedef struct {                         // epoll_event.data.ptr
    kasittelija kutsu;
    void *tila;
} kohde;

struct silmukka {
    int ep;
    int jaljella;                        // palveltavat yhteydet; 0 = lopeta
};

static void seuraa(silmukka *s, int op, int fd, uint32_t tapahtumat,
                   kohde *k) {
    struct epoll_event e = {.events = tapahtumat, .data.ptr = k};
    TARKISTA(epoll_ctl(s->ep, op, fd, &e));
}

static void aja(silmukka *s) {
    while (s->jaljella > 0) {
        struct epoll_event valmiit[16];
        int n = (int)TARKISTA(epoll_wait(s->ep, valmiit, 16, -1));
        for (int i = 0; i < n; i++) {
            kohde *k = (kohde *)valmiit[i].data.ptr;
            k->kutsu(s, k->tila, valmiit[i].events);
        }
    }
}
// @loppu silmukka

// @alku yhteys
typedef struct {
    int fd, ajastin;
    kohde soketti, aika;
    char *ulos;                          // lähtevä data [alku, loppu)
    size_t alku, loppu;
    bool odotti_kirjoitusta;
} yhteys;

static void sulje(silmukka *s, yhteys *y) {
    close(y->fd);                        // poistuvat myös epollista
    close(y->ajastin);
    free(y->ulos);
    free(y);
    s->jaljella--;
}

static void nollaa_ajastin(yhteys *y) {  // joutilasaika 200 ms
    struct itimerspec t = {.it_value.tv_nsec = 200'000'000};
    TARKISTA(timerfd_settime(y->ajastin, 0, &t, nullptr));
}

// Kirjoittaa puskuria, kunnes se tyhjenee tai ydin ei ota enempää.
// EPOLLOUT on päällä vain, kun lähtevää on jonossa; muuten se herättäisi
// silmukan jatkuvasti, koska tyhjä lähetyspuskuri on aina kirjoitettava.
static void kirjoita(silmukka *s, yhteys *y) {
    while (y->alku < y->loppu) {
        ssize_t n = send(y->fd, y->ulos + y->alku, y->loppu - y->alku,
                         MSG_NOSIGNAL);
        if (n == -1 && errno == EAGAIN) {
            break;
        }
        if (n == -1) {
            sulje(s, y);
            return;
        }
        y->alku += (size_t)n;
        nollaa_ajastin(y);               // eteneminen ei ole joutilaisuutta
    }
    bool jonossa = y->alku < y->loppu;
    y->odotti_kirjoitusta = y->odotti_kirjoitusta || jonossa;
    // Vastapaine: kun lähtevää on yli rajan, uusia pyyntöjä ei lueta.
    uint32_t t = (jonossa ? EPOLLOUT : 0) |
                 (y->loppu - y->alku > RAJA ? 0 : EPOLLIN);
    seuraa(s, EPOLL_CTL_MOD, y->fd, t, &y->soketti);
}
// @loppu yhteys

static bool odotettiin_kirjoitusta;      // tulostetaan lopuksi

// @alku kasittelijat
static void soketti_valmis(silmukka *s, void *tila, uint32_t t) {
    yhteys *y = (yhteys *)tila;
    if (t & EPOLLOUT) {
        kirjoita(s, y);
        return;
    }
    char pyynto[64];
    ssize_t n = recv(y->fd, pyynto, sizeof pyynto - 1, 0);
    if (n <= 0) {
        if (n == 0 || errno != EAGAIN) {
            odotettiin_kirjoitusta |= y->odotti_kirjoitusta;
            sulje(s, y);
        }
        return;
    }
    nollaa_ajastin(y);
    pyynto[n] = '\0';
    size_t koko;
    if (sscanf(pyynto, "ANNA %zu", &koko) == 1 && koko <= MAARA) {
        y->ulos = (char *)realloc(y->ulos, koko);
        for (size_t i = 0; i < koko; i++) {
            y->ulos[i] = (char)('a' + i % 26);
        }
        y->alku = 0;
        y->loppu = koko;
        kirjoita(s, y);
    }
}

static void aika_loppui(silmukka *s, void *tila, uint32_t) {
    yhteys *y = (yhteys *)tila;
    uint64_t kertoja;
    TARKISTA(read(y->ajastin, &kertoja, sizeof kertoja));
    printf("palvelin: joutilas yhteys suljetaan\n");
    sulje(s, y);
}

static void uusi_yhteys(silmukka *s, void *tila, uint32_t) {
    int kuuntelija = *(int *)tila;
    yhteys *y = (yhteys *)calloc(1, sizeof *y);
    y->fd = (int)TARKISTA(accept4(kuuntelija, nullptr, nullptr,
                                  SOCK_NONBLOCK));
    int pieni = 16 * 1024;               // pieni puskuri: EAGAIN varmasti
    TARKISTA(setsockopt(y->fd, SOL_SOCKET, SO_SNDBUF, &pieni,
                        sizeof pieni));
    y->ajastin = (int)TARKISTA(timerfd_create(CLOCK_MONOTONIC,
                                              TFD_NONBLOCK));
    y->soketti = (kohde){soketti_valmis, y};
    y->aika = (kohde){aika_loppui, y};
    seuraa(s, EPOLL_CTL_ADD, y->fd, EPOLLIN, &y->soketti);
    seuraa(s, EPOLL_CTL_ADD, y->ajastin, EPOLLIN, &y->aika);
    nollaa_ajastin(y);
}
// @loppu kasittelijat

static int lataaja(void *) {
    int fd = yhdista(portti);
    char pyynto[32];
    int n = snprintf(pyynto, sizeof pyynto, "ANNA %d\n", MAARA);
    TARKISTA(kirjoita_kaikki(fd, pyynto, (size_t)n));
    char *data = (char *)malloc(MAARA);
    bool ok = lue_tasan(fd, data, MAARA) == 1;
    for (size_t i = 0; ok && i < MAARA; i++) {
        ok = data[i] == (char)('a' + i % 26);
    }
    free(data);
    close(fd);
    return ok ? 0 : 1;
}

static int joutilas(void *) {
    int fd = yhdista(portti);
    char c;
    ssize_t n = recv(fd, &c, 1, 0);      // ei lähetä mitään
    close(fd);
    return n == 0 ? 0 : 1;               // palvelin sulki
}

int main(void) {
    vahtikoira();
    int kuuntelija = kuuntele(&portti);
    silmukka s = {.ep = (int)TARKISTA(epoll_create1(EPOLL_CLOEXEC)),
                  .jaljella = 2};        // kaksi asiakasta
    kohde hyvaksy = {uusi_yhteys, &kuuntelija};
    seuraa(&s, EPOLL_CTL_ADD, kuuntelija, EPOLLIN, &hyvaksy);
    pid_t a = kaynnista(lataaja, nullptr);
    pid_t b = kaynnista(joutilas, nullptr);
    aja(&s);
    int virheita = (odota(a) != 0) + (odota(b) != 0);
    printf("lataaja sai 4 MiB ehjänä: %s\n", virheita == 0 ? "kyllä" : "ei");
    printf("lähetys jatkui EPOLLOUT-tapahtumista: %s\n",
           odotettiin_kirjoitusta ? "kyllä" : "ei");
    close(s.ep);
    close(kuuntelija);
    return virheita;
}
