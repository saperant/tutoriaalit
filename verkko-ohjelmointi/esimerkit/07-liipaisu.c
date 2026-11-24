// Estämätön I/O ja epollin kaksi tilaa. Tasoliipaisu ilmoittaa niin
// kauan kuin dataa on luettavissa, reunaliipaisu vain uuden datan
// saapuessa.
#define _GNU_SOURCE
#include <fcntl.h>
#include <sys/epoll.h>

#include "verkko.h"

// Yhdistetty TCP-pari samassa prosessissa (silmukkaosoite).
static void tcp_pari(int *a, int *b) {
    uint16_t portti;
    int kuuntelija = kuuntele(&portti);
    *a = yhdista(portti);                // ydin hoitaa kättelyn
    *b = (int)TARKISTA(accept(kuuntelija, nullptr, nullptr));
    close(kuuntelija);
}

// @alku estamaton
static void aseta_estamaton(int fd) {
    int liput = (int)TARKISTA(fcntl(fd, F_GETFL));
    TARKISTA(fcntl(fd, F_SETFL, liput | O_NONBLOCK));
}
// @loppu estamaton

// Montako sokettia on valmiina. ms = kauanko odotetaan ensimmäistä.
static int tapahtumia(int ep, int ms) {
    struct epoll_event e[4];
    return (int)TARKISTA(epoll_wait(ep, e, 4, ms));
}

int main(void) {
    int lahettaja, vastaanottaja;
    tcp_pari(&lahettaja, &vastaanottaja);
    char puskuri[256];

    // @alku eagain
    aseta_estamaton(vastaanottaja);
    ssize_t n = recv(vastaanottaja, puskuri, sizeof puskuri, 0);
    printf("tyhjä estämätön soketti: %s\n",
           n == -1 ? strerrorname_np(errno) : "dataa");
    // @loppu eagain

    // @alku tilat
    int taso = (int)TARKISTA(epoll_create1(EPOLL_CLOEXEC));
    int reuna = (int)TARKISTA(epoll_create1(EPOLL_CLOEXEC));
    struct epoll_event e = {.events = EPOLLIN, .data.fd = vastaanottaja};
    TARKISTA(epoll_ctl(taso, EPOLL_CTL_ADD, vastaanottaja, &e));
    e.events = EPOLLIN | EPOLLET;
    TARKISTA(epoll_ctl(reuna, EPOLL_CTL_ADD, vastaanottaja, &e));

    TARKISTA(kirjoita_kaikki(lahettaja, puskuri, 100));
    int r = tapahtumia(reuna, 2000);     // odota, että data on perillä
    printf("100 tavua saapui:       taso %d, reuna %d\n",
           tapahtumia(taso, 0), r);
    TARKISTA(recv(vastaanottaja, puskuri, 10, 0));
    r = tapahtumia(reuna, 0);
    printf("luettu 10, 90 jäljellä: taso %d, reuna %d\n",
           tapahtumia(taso, 0), r);
    TARKISTA(kirjoita_kaikki(lahettaja, puskuri, 1));
    r = tapahtumia(reuna, 2000);         // uusi data = uusi reuna
    printf("1 tavu lisää:           taso %d, reuna %d\n",
           tapahtumia(taso, 0), r);
    // @loppu tilat

    // @alku tyhjenna
    // Reunaliipaisussa luetaan aina EAGAINiin asti: muuten loput jäävät
    // lukematta, eikä uutta ilmoitusta tule.
    long yhteensa = 0;
    while ((n = recv(vastaanottaja, puskuri, sizeof puskuri, 0)) > 0) {
        yhteensa += n;
    }
    printf("tyhjennys luki %ld tavua ja päättyi: %s\n", yhteensa,
           n == -1 ? strerrorname_np(errno) : "yhteys suljettu");
    // @loppu tyhjenna

    // @alku sulkeminen
    e.events = EPOLLIN | EPOLLRDHUP;
    TARKISTA(epoll_ctl(taso, EPOLL_CTL_MOD, vastaanottaja, &e));
    close(lahettaja);
    struct epoll_event saatu;
    TARKISTA(epoll_wait(taso, &saatu, 1, 2000));
    printf("vastapuoli sulki: EPOLLRDHUP %s\n",
           saatu.events & EPOLLRDHUP ? "kyllä" : "ei");
    // @loppu sulkeminen
    close(vastaanottaja);
    close(taso);
    close(reuna);
    return 0;
}
