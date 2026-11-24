// UDP: jokainen sendto on oma datagramminsa, joka saapuu kokonaan tai ei
// lainkaan. Näytetään viestirajat, katkaisu, enimmäiskoko ja yhdistetyn
// UDP-soketin virheilmoitus suljettuun porttiin.
#define _GNU_SOURCE
#include <poll.h>

#include "verkko.h"

// @alku soketti
static int udp_soketti(struct sockaddr_in *osoite) {
    int fd = (int)TARKISTA(socket(AF_INET, SOCK_DGRAM, 0));
    *osoite = (struct sockaddr_in){.sin_family = AF_INET,
                                   .sin_addr.s_addr = htonl(INADDR_LOOPBACK)};
    TARKISTA(bind(fd, (struct sockaddr *)osoite, sizeof *osoite));
    socklen_t pituus = sizeof *osoite;
    TARKISTA(getsockname(fd, (struct sockaddr *)osoite, &pituus));
    return fd;
}
// @loppu soketti

static const char *virhe(ssize_t tulos) {
    return tulos >= 0 ? "onnistui" : strerrorname_np(errno);
}

int main(void) {
    vahtikoira();
    struct sockaddr_in a_os, b_os;
    int a = udp_soketti(&a_os);
    int b = udp_soketti(&b_os);

    // @alku rajat
    static char data[65536];
    size_t koot[] = {5, 0, 1200};
    for (size_t i = 0; i < 3; i++) {
        TARKISTA(sendto(a, data, koot[i], 0, (struct sockaddr *)&b_os,
                        sizeof b_os));
    }
    for (size_t i = 0; i < 3; i++) {
        struct sockaddr_in lahettaja;
        socklen_t pituus = sizeof lahettaja;
        ssize_t n = TARKISTA(recvfrom(b, data, sizeof data, 0,
                                      (struct sockaddr *)&lahettaja,
                                      &pituus));
        printf("datagrammi %zu: %4zd tavua, lähettäjä a: %s\n", i + 1, n,
               lahettaja.sin_port == a_os.sin_port ? "kyllä" : "ei");
    }
    // @loppu rajat

    // @alku katkaisu
    TARKISTA(sendto(a, data, 100, 0, (struct sockaddr *)&b_os,
                    sizeof b_os));
    char pieni[10];
    ssize_t n = TARKISTA(recv(b, pieni, sizeof pieni, MSG_TRUNC));
    printf("10 tavun puskuriin: datagrammin todellinen koko %zd, "
           "loput hävisivät\n", n);
    ssize_t k = sendto(a, data, 65508, 0, (struct sockaddr *)&b_os,
                       sizeof b_os);
    printf("65508 tavun datagrammi: %s\n", virhe(k));
    // @loppu katkaisu

    // @alku suljettu
    struct sockaddr_in suljettu;
    close(udp_soketti(&suljettu));       // portti, jossa ei ole ketään
    k = sendto(a, "x", 1, 0, (struct sockaddr *)&suljettu,
               sizeof suljettu);
    printf("sendto suljettuun porttiin: %s\n", virhe(k));
    struct pollfd p = {.fd = a, .events = POLLIN};
    TARKISTA(poll(&p, 1, 200));
    printf("yhdistämätön soketti, recv: %s\n",
           virhe(recv(a, pieni, sizeof pieni, MSG_DONTWAIT)));

    TARKISTA(connect(a, (struct sockaddr *)&suljettu, sizeof suljettu));
    printf("yhdistetty soketti, send: %s\n", virhe(send(a, "x", 1, 0)));
    TARKISTA(poll(&p, 1, 2000));         // ICMP-virhe herättää (POLLERR)
    printf("yhdistetty soketti, recv: %s\n",
           virhe(recv(a, pieni, sizeof pieni, MSG_DONTWAIT)));
    // @loppu suljettu
    close(a);
    close(b);
    return 0;
}
