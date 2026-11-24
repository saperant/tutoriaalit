// Sama palvelin epollilla reunaliipaisussa. Ydin pitää seurattavien
// joukon itse, joten jokainen kierros maksaa valmiiden eikä kaikkien
// sokettien verran. Tapahtuman mukana tulee osoitin yhteyden tilaan.
#define _GNU_SOURCE
#include <fcntl.h>
#include <sys/epoll.h>

#include "nelio.h"

enum { ASIAKKAITA = 200, KIERROKSIA = 5 };
static uint16_t portti;

static int kuormittaja(void *) {
    return kuormita(portti, ASIAKKAITA, KIERROKSIA) == 0 ? 0 : 1;
}

// @alku hyvaksy
// Reunaliipaisussa hyväksytään, kunnes jono on tyhjä (EAGAIN).
static int hyvaksy_kaikki(int ep, int kuuntelija) {
    int uusia = 0;
    int fd;
    while ((fd = accept4(kuuntelija, nullptr, nullptr, SOCK_NONBLOCK)) >= 0) {
        yhteys *y = (yhteys *)calloc(1, sizeof *y);
        y->fd = fd;
        struct epoll_event e = {.events = EPOLLIN | EPOLLET, .data.ptr = y};
        TARKISTA(epoll_ctl(ep, EPOLL_CTL_ADD, fd, &e));
        uusia++;
    }
    if (errno != EAGAIN) {
        TARKISTA(-1);
    }
    return uusia;
}
// @loppu hyvaksy

// @alku lue
// Lukee kaiken saatavilla olevan. Palauttaa käsitellyt pyynnöt tai -1,
// kun yhteys on suljettava.
static int lue_kaikki(yhteys *y) {
    int yhteensa = 0;
    for (;;) {
        ssize_t n = recv(y->fd, y->sisaan + y->n, sizeof y->sisaan - y->n, 0);
        if (n == -1 && errno == EAGAIN) {
            return yhteensa;             // kaikki luettu: odota uutta reunaa
        }
        if (n <= 0) {
            return -1;                   // vastapuoli sulki tai virhe
        }
        y->n += (size_t)n;
        int k = kasittele_rivit(y);
        if (k < 0) {
            return -1;
        }
        yhteensa += k;
    }
}
// @loppu lue

int main(void) {
    vahtikoira();
    int kuuntelija = kuuntele(&portti);
    pid_t pid = kaynnista(kuormittaja, nullptr);

    // @alku silmukka
    int ep = (int)TARKISTA(epoll_create1(EPOLL_CLOEXEC));
    struct epoll_event e = {.events = EPOLLIN | EPOLLET, .data.ptr = nullptr};
    TARKISTA(fcntl(kuuntelija, F_SETFL, O_NONBLOCK));
    TARKISTA(epoll_ctl(ep, EPOLL_CTL_ADD, kuuntelija, &e));
    int avoinna = 0, palveltu = 0, pyyntoja = 0;
    while (palveltu < ASIAKKAITA || avoinna > 0) {
        struct epoll_event valmiit[64];
        int n = (int)TARKISTA(epoll_wait(ep, valmiit, 64, -1));
        for (int i = 0; i < n; i++) {
            yhteys *y = (yhteys *)valmiit[i].data.ptr;
            if (y == nullptr) {          // kuuntelija
                int uusia = hyvaksy_kaikki(ep, kuuntelija);
                palveltu += uusia;
                avoinna += uusia;
                continue;
            }
            int k = lue_kaikki(y);
            if (k < 0) {
                close(y->fd);            // close poistaa myös epollista
                free(y);
                avoinna--;
            } else {
                pyyntoja += k;
            }
        }
    }
    // @loppu silmukka
    printf("epoll: %d yhteyttä, %d pyyntöä\n", palveltu, pyyntoja);
    close(ep);
    close(kuuntelija);
    return odota(pid);
}
