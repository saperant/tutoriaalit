// TCP on tavuvirta: lähetysten rajat eivät säily, ja yksi recv voi
// palauttaa vähemmän kuin pyydettiin. Molemmat näytetään.
#define _GNU_SOURCE
#include <poll.h>

#include "verkko.h"

enum { ISO = 1 << 20 };                  // 1 MiB
static uint16_t portti;

static uint32_t summa(const unsigned char *p, size_t n) {
    uint32_t s = 0;
    for (size_t i = 0; i < n; i++) {
        s = s * 31 + p[i];
    }
    return s;
}

// @alku lahettaja
static int kaksi_lahetysta(void *) {
    int fd = yhdista(portti);
    TARKISTA(kirjoita_kaikki(fd, "eka viesti\n", 11));
    TARKISTA(kirjoita_kaikki(fd, "toka viesti\n", 12));
    TARKISTA(close(fd));
    return 0;
}
// @loppu lahettaja

static int iso_lahetys(void *) {
    unsigned char *data = (unsigned char *)malloc(ISO);
    for (size_t i = 0; i < ISO; i++) {
        data[i] = (unsigned char)(i * 7);
    }
    int fd = yhdista(portti);
    TARKISTA(kirjoita_kaikki(fd, data, ISO));  // estyy, kunnes perillä
    TARKISTA(close(fd));
    free(data);
    return 0;
}

int main(void) {
    vahtikoira();
    int kuuntelija = kuuntele(&portti);

    // @alku yhdessa
    pid_t pid = kaynnista(kaksi_lahetysta, nullptr);
    int yhteys = (int)TARKISTA(accept(kuuntelija, nullptr, nullptr));
    struct pollfd p = {.fd = yhteys, .events = POLLRDHUP};
    TARKISTA(poll(&p, 1, 5000));         // FIN perillä: kaikki data jonossa
    char puskuri[64];
    ssize_t n = TARKISTA(recv(yhteys, puskuri, sizeof puskuri, 0));
    printf("yksi recv sai %zd tavua: %.*s", n, (int)n, puskuri);
    // @loppu yhdessa
    close(yhteys);
    odota(pid);

    // @alku vajaa
    int pieni = 16 * 1024;               // pieni vastaanottopuskuri
    TARKISTA(setsockopt(kuuntelija, SOL_SOCKET, SO_RCVBUF, &pieni,
                        sizeof pieni));
    pid = kaynnista(iso_lahetys, nullptr);
    yhteys = (int)TARKISTA(accept(kuuntelija, nullptr, nullptr));
    unsigned char *data = (unsigned char *)malloc(ISO);
    n = TARKISTA(recv(yhteys, data, ISO, 0));
    printf("1. recv pyysi %d tavua, sai vähemmän: %s\n", ISO,
           n < ISO ? "kyllä" : "ei");
    if (lue_tasan(yhteys, data + n, ISO - (size_t)n) != 1) {
        return 1;
    }
    // @loppu vajaa
    uint32_t odotettu = 0;
    for (size_t i = 0; i < ISO; i++) {
        odotettu = odotettu * 31 + (unsigned char)(i * 7);
    }
    printf("lue_tasan luki loput, tarkistussumma täsmää: %s\n",
           summa(data, ISO) == odotettu ? "kyllä" : "ei");
    free(data);
    close(yhteys);
    odota(pid);
    close(kuuntelija);
    return 0;
}
