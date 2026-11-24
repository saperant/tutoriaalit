// Yhteyden sulkemisen muodot: puolisulkeminen shutdown-kutsulla,
// kirjoitus suljettuun yhteyteen (EPIPE ja SIGPIPE) ja yhteyden
// katkaisu RST-segmentillä.
#define _GNU_SOURCE
#include <poll.h>

#include "verkko.h"

static uint16_t portti;

// @alku puoli
// Asiakas lähettää koko pyynnön ja sulkee oman kirjoitussuuntansa.
// Palvelin tietää pyynnön päättyneen, kun recv palauttaa 0, ja vastaa
// samaa yhteyttä pitkin.
static int puoliksi(void *) {
    int fd = yhdista(portti);
    const char *pyynto = "laske nämä tavut";
    TARKISTA(kirjoita_kaikki(fd, pyynto, strlen(pyynto)));
    TARKISTA(shutdown(fd, SHUT_WR));     // lähettää FIN-segmentin
    char vastaus[64] = {};
    size_t n = 0;
    ssize_t k;
    while ((k = TARKISTA(recv(fd, vastaus + n, sizeof vastaus - 1 - n,
                              0))) > 0) {
        n += (size_t)k;
    }
    printf("asiakas: vastaus \"%s\"\n", vastaus);
    TARKISTA(close(fd));
    return 0;
}
// @loppu puoli

// @alku epipe
// Palvelin on jo sulkenut yhteyden. Ensimmäinen kirjoitus menee
// verkkoon, ja vastapuoli vastaa siihen RST-segmentillä. Seuraava
// kirjoitus epäonnistuu: EPIPE ja oletuksena signaali SIGPIPE.
static int kirjoita_suljettuun(void *lippu) {
    int liput = *(int *)lippu;           // 0 tai MSG_NOSIGNAL
    int fd = yhdista(portti);
    char c;
    TARKISTA(recv(fd, &c, 1, 0));        // 0 = palvelin sulki (FIN)
    ssize_t k = send(fd, "a", 1, liput);
    printf("1. send: %s\n", k == 1 ? "onnistui" : strerrorname_np(errno));
    fflush(stdout);                      // ennen mahdollista SIGPIPEä
    struct pollfd odotus = {.fd = fd, .events = 0};
    TARKISTA(poll(&odotus, 1, 2000));    // odota RST:tä (POLLERR)
    k = send(fd, "b", 1, liput);
    printf("2. send: %s\n", k == 1 ? "onnistui" : strerrorname_np(errno));
    close(fd);
    return 0;
}
// @loppu epipe

static int lue_nollattu(void *) {
    int fd = yhdista(portti);
    char c;
    ssize_t k = recv(fd, &c, 1, 0);
    printf("recv: %s\n", k == -1 ? strerrorname_np(errno) : "dataa");
    close(fd);
    return 0;
}

int main(void) {
    vahtikoira();
    int kuuntelija = kuuntele(&portti);

    pid_t pid = kaynnista(puoliksi, nullptr);
    int yhteys = (int)TARKISTA(accept(kuuntelija, nullptr, nullptr));
    char puskuri[256];
    long tavuja = 0;
    ssize_t k;
    while ((k = TARKISTA(recv(yhteys, puskuri, sizeof puskuri, 0))) > 0) {
        tavuja += k;
    }
    int n = snprintf(puskuri, sizeof puskuri, "%ld tavua", tavuja);
    TARKISTA(kirjoita_kaikki(yhteys, puskuri, (size_t)n));
    TARKISTA(close(yhteys));
    odota(pid);

    puts("-- kirjoitus suljettuun yhteyteen, MSG_NOSIGNAL:");
    int liput = MSG_NOSIGNAL;
    pid = kaynnista(kirjoita_suljettuun, &liput);
    TARKISTA(close((int)TARKISTA(accept(kuuntelija, nullptr, nullptr))));
    odota(pid);

    puts("-- sama ilman lippua:");
    liput = 0;
    pid = kaynnista(kirjoita_suljettuun, &liput);
    TARKISTA(close((int)TARKISTA(accept(kuuntelija, nullptr, nullptr))));
    int tila;
    TARKISTA(waitpid(pid, &tila, 0));
    printf("lapsi: %s\n", WIFSIGNALED(tila)
               ? sigabbrev_np(WTERMSIG(tila)) : "päättyi itse");

    // @alku rst
    puts("-- palvelin katkaisee yhteyden (SO_LINGER, aika 0):");
    pid = kaynnista(lue_nollattu, nullptr);
    yhteys = (int)TARKISTA(accept(kuuntelija, nullptr, nullptr));
    struct linger heti = {.l_onoff = 1, .l_linger = 0};
    TARKISTA(setsockopt(yhteys, SOL_SOCKET, SO_LINGER, &heti,
                        sizeof heti));
    TARKISTA(close(yhteys));             // RST eikä FIN
    // @loppu rst
    odota(pid);
    TARKISTA(close(kuuntelija));
    return 0;
}
