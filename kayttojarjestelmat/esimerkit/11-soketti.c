// UNIX-soketit: datagrammit säilyttävät viestirajat, ja SCM_RIGHTS
// siirtää avoimen tiedostokuvaajan toiselle prosessille.
#define _GNU_SOURCE
#include <fcntl.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <sys/wait.h>
#include <unistd.h>

#include "tarkista.h"

// @alku laheta
// @alku lahetys
static void laheta_kuvaaja(int soketti, int fd) {
    char tavu = 'k';
    struct iovec iov = {.iov_base = &tavu, .iov_len = 1};
    union {                              // tasattu ohjauspuskuri
        char puskuri[CMSG_SPACE(sizeof(int))];
        struct cmsghdr tasaus;
    } ohjaus = {};
    struct msghdr viesti = {.msg_iov = &iov, .msg_iovlen = 1,
                            .msg_control = ohjaus.puskuri,
                            .msg_controllen = sizeof ohjaus.puskuri};
    struct cmsghdr *c = CMSG_FIRSTHDR(&viesti);
    c->cmsg_level = SOL_SOCKET;
    c->cmsg_type = SCM_RIGHTS;
    c->cmsg_len = CMSG_LEN(sizeof(int));
    memcpy(CMSG_DATA(c), &fd, sizeof fd);
    TARKISTA(sendmsg(soketti, &viesti, 0));
}
// @loppu lahetys

static int vastaanota_kuvaaja(int soketti) {
    char tavu;
    struct iovec iov = {.iov_base = &tavu, .iov_len = 1};
    union {
        char puskuri[CMSG_SPACE(sizeof(int))];
        struct cmsghdr tasaus;
    } ohjaus;
    struct msghdr viesti = {.msg_iov = &iov, .msg_iovlen = 1,
                            .msg_control = ohjaus.puskuri,
                            .msg_controllen = sizeof ohjaus.puskuri};
    TARKISTA(recvmsg(soketti, &viesti, 0));
    struct cmsghdr *c = CMSG_FIRSTHDR(&viesti);
    int fd = -1;
    if (c && c->cmsg_type == SCM_RIGHTS) {
        memcpy(&fd, CMSG_DATA(c), sizeof fd);
    }
    return fd;
}
// @loppu laheta

int main(void) {
    // @alku datagrammit
    int pari[2];
    TARKISTA(socketpair(AF_UNIX, SOCK_DGRAM, 0, pari));
    TARKISTA(send(pari[0], "eka", 3, 0));
    TARKISTA(send(pari[0], "toka viesti", 11, 0));
    char puskuri[64];
    for (int i = 0; i < 2; i++) {        // kukin recv saa yhden viestin
        ssize_t n = TARKISTA(recv(pari[1], puskuri, sizeof puskuri, 0));
        printf("datagrammi %d: %zd tavua \"%.*s\"\n", i + 1, n, (int)n,
               puskuri);
    }
    close(pari[0]);
    close(pari[1]);
    // @loppu datagrammit

    // @alku siirto
    int fd = TARKISTA(open("salainen.txt", O_RDWR | O_CREAT | O_TRUNC,
                           0600));
    TARKISTA(write(fd, "vain kuvaajan haltijalle\n", 25));
    TARKISTA(socketpair(AF_UNIX, SOCK_STREAM, 0, pari));
    fflush(stdout);
    pid_t pid = TARKISTA(fork());
    if (pid == 0) {
        close(pari[0]);
        int saatu = vastaanota_kuvaaja(pari[1]);
        char rivi[64] = {};
        TARKISTA(pread(saatu, rivi, sizeof rivi - 1, 0));
        printf("lapsi luki saamastaan kuvaajasta: %s", rivi);
        fflush(stdout);
        _exit(0);
    }
    close(pari[1]);
    laheta_kuvaaja(pari[0], fd);
    TARKISTA(close(fd));                 // lapsen kopio pysyy auki
    TARKISTA(waitpid(pid, nullptr, 0));
    close(pari[0]);
    // @loppu siirto

    // @alku nimetty
    struct sockaddr_un osoite = {.sun_family = AF_UNIX};
    strcpy(osoite.sun_path, "palvelin.sock");
    int palvelin = TARKISTA(socket(AF_UNIX, SOCK_STREAM, 0));
    TARKISTA(bind(palvelin, (struct sockaddr *)&osoite, sizeof osoite));
    TARKISTA(listen(palvelin, 1));
    int asiakas = TARKISTA(socket(AF_UNIX, SOCK_STREAM, 0));
    TARKISTA(connect(asiakas, (struct sockaddr *)&osoite, sizeof osoite));
    int yhteys = TARKISTA(accept(palvelin, nullptr, nullptr));
    struct ucred tunnus;
    socklen_t pituus = sizeof tunnus;
    TARKISTA(getsockopt(yhteys, SOL_SOCKET, SO_PEERCRED, &tunnus,
                        &pituus));
    printf("vertaisen PID oma: %s, UID oma: %s\n",
           tunnus.pid == getpid() ? "kyllä" : "ei",
           tunnus.uid == getuid() ? "kyllä" : "ei");
    close(yhteys);
    close(asiakas);
    close(palvelin);
    TARKISTA(unlink("palvelin.sock"));
    // @loppu nimetty
    return 0;
}
