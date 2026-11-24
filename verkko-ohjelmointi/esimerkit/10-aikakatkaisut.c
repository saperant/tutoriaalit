// Aikakatkaisut: yhteyden muodostus määräajassa, vastauksen odotus
// SO_RCVTIMEO-valitsimella ja kuolleen vastapuolen havaitseminen
// keepalive-asetuksilla.
#define _GNU_SOURCE
#include <fcntl.h>
#include <netinet/tcp.h>
#include <poll.h>

#include "verkko.h"

// @alku yhdista
// connect estämättömänä: EINPROGRESS ja poll kirjoitettavuutta, sitten
// lopputulos SO_ERROR-valitsimesta. Palauttaa estävän soketin tai -1.
static int yhdista_maaraajassa(const struct sockaddr_in *osoite, int ms) {
    int fd = (int)TARKISTA(socket(AF_INET, SOCK_STREAM | SOCK_NONBLOCK, 0));
    if (connect(fd, (const struct sockaddr *)osoite, sizeof *osoite) == -1) {
        if (errno != EINPROGRESS) {
            close(fd);
            return -1;                   // esim. ECONNREFUSED heti
        }
        struct pollfd p = {.fd = fd, .events = POLLOUT};
        if (TARKISTA(poll(&p, 1, ms)) == 0) {
            close(fd);
            errno = ETIMEDOUT;
            return -1;
        }
        int virhe;
        socklen_t pituus = sizeof virhe;
        TARKISTA(getsockopt(fd, SOL_SOCKET, SO_ERROR, &virhe, &pituus));
        if (virhe != 0) {
            close(fd);
            errno = virhe;
            return -1;
        }
    }
    TARKISTA(fcntl(fd, F_SETFL, 0));     // takaisin estäväksi
    return fd;
}
// @loppu yhdista

static const char *tulos(int fd) {
    return fd >= 0 ? "yhteys" : strerrorname_np(errno);
}

int main(void) {
    vahtikoira();
    // @alku jono
    // Kuuntelija, jonka jonoon mahtuu yksi yhteys eikä kukaan hyväksy
    // niitä: seuraavan asiakkaan SYN-segmentit pudotetaan.
    int kuuntelija = (int)TARKISTA(socket(AF_INET, SOCK_STREAM, 0));
    struct sockaddr_in osoite = {.sin_family = AF_INET,
                                 .sin_addr.s_addr = htonl(INADDR_LOOPBACK)};
    TARKISTA(bind(kuuntelija, (struct sockaddr *)&osoite, sizeof osoite));
    TARKISTA(listen(kuuntelija, 0));
    socklen_t pituus = sizeof osoite;
    TARKISTA(getsockname(kuuntelija, (struct sockaddr *)&osoite, &pituus));

    int eka = yhdista_maaraajassa(&osoite, 500);
    printf("1. yhteys:               %s\n", tulos(eka));
    int toka = yhdista_maaraajassa(&osoite, 500);
    printf("2. yhteys, jono täynnä:  %s\n", tulos(toka));
    // @loppu jono

    // @alku suljettu
    struct sockaddr_in suljettu = osoite;
    int apu = (int)TARKISTA(socket(AF_INET, SOCK_STREAM, 0));
    suljettu.sin_port = 0;
    TARKISTA(bind(apu, (struct sockaddr *)&suljettu, sizeof suljettu));
    pituus = sizeof suljettu;
    TARKISTA(getsockname(apu, (struct sockaddr *)&suljettu, &pituus));
    close(apu);                          // portti vapaa, ei kuuntelijaa
    printf("suljettu portti:         %s\n",
           tulos(yhdista_maaraajassa(&suljettu, 500)));
    // @loppu suljettu

    // @alku rcvtimeo
    // Yhteys syntyi, mutta palvelin ei vastaa: recv palaa määräajassa.
    struct timeval aika = {.tv_usec = 200'000};
    TARKISTA(setsockopt(eka, SOL_SOCKET, SO_RCVTIMEO, &aika, sizeof aika));
    char c;
    ssize_t n = recv(eka, &c, 1, 0);
    printf("vastauksen odotus:       %s\n",
           n == -1 ? strerrorname_np(errno) : "dataa");
    // @loppu rcvtimeo

    // @alku keepalive
    // Keepalive: 30 s hiljaisuuden jälkeen koetus 5 s välein, ja kolmen
    // vastaamattoman jälkeen yhteys katkeaa (ETIMEDOUT). TCP_USER_TIMEOUT
    // rajaa, kauanko lähetetty data saa olla kuittaamatta.
    int arvot[][3] = {{SOL_SOCKET, SO_KEEPALIVE, 1},
                      {IPPROTO_TCP, TCP_KEEPIDLE, 30},
                      {IPPROTO_TCP, TCP_KEEPINTVL, 5},
                      {IPPROTO_TCP, TCP_KEEPCNT, 3},
                      {IPPROTO_TCP, TCP_USER_TIMEOUT, 20000}};
    const char *nimet[] = {"SO_KEEPALIVE", "TCP_KEEPIDLE", "TCP_KEEPINTVL",
                           "TCP_KEEPCNT", "TCP_USER_TIMEOUT"};
    for (int i = 0; i < 5; i++) {
        TARKISTA(setsockopt(eka, arvot[i][0], arvot[i][1], &arvot[i][2],
                            sizeof(int)));
        int luettu;
        pituus = sizeof luettu;
        TARKISTA(getsockopt(eka, arvot[i][0], arvot[i][1], &luettu,
                            &pituus));
        printf("%-17s = %d\n", nimet[i], luettu);
    }
    // @loppu keepalive
    close(eka);
    close(kuuntelija);
    return 0;
}
