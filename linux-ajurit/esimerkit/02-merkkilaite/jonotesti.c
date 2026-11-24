// Käyttäjätilan testi viestijonoajurille: ajetaan QEMU:ssa ladatun
// jono.ko:n kanssa. Jokainen vaihe tulostaa tuloksensa.
#include <errno.h>
#include <fcntl.h>
#include <poll.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>

#include "jono.h"

static void tila(int fd)
{
    struct jono_tila t;
    if (ioctl(fd, JONO_TILA, &t) != 0) {
        printf("JONO_TILA: %s\n", strerror(errno));
        return;
    }
    printf("tila: %u/%u tavua\n", t.kaytetty, t.koko);
}

static void nayta_poll(int fd)
{
    struct pollfd p = {.fd = fd, .events = POLLIN | POLLOUT};
    poll(&p, 1, 0);
    printf("poll:%s%s\n", (p.revents & POLLIN) ? " luettavissa" : "",
           (p.revents & POLLOUT) ? " kirjoitettavissa" : "");
}

// @alku perus
static void perustoiminnot(void)
{
    char puskuri[128];
    int fd = open("/dev/jono0", O_RDWR | O_NONBLOCK);
    if (fd < 0) {
        printf("open: %s\n", strerror(errno));
        return;
    }
    ssize_t n = read(fd, puskuri, sizeof puskuri);
    printf("luku tyhjästä: %zd (%s)\n", n, strerror(errno));
    nayta_poll(fd);

    n = write(fd, "lampotila 21\n", 13);
    printf("kirjoitettiin %zd tavua\n", n);
    tila(fd);
    nayta_poll(fd);

    n = read(fd, puskuri, sizeof puskuri);
    printf("luettiin %zd tavua: %.*s", n, (int)n, puskuri);

    // Ydin tarkistaa käyttäjän osoittimen: virheellinen osoite on
    // EFAULT, ei kaatuminen. (volatile estää kääntäjää varoittamasta.)
    volatile uintptr_t huono = 16;
    n = write(fd, (const void *)huono, 4);
    printf("kirjoitus osoitteesta 16: %zd (%s)\n", n, strerror(errno));
    n = ioctl(fd, _IO('x', 9));
    printf("tuntematon ioctl: %zd (%s)\n", n, strerror(errno));
    // @loppu perus

    // @alku taysi
    size_t yhteensa = 0;
    while ((n = write(fd, "0123456789", 10)) > 0) {
        yhteensa += (size_t)n;
    }
    printf("täyteen: %zu tavua, sitten %s\n", yhteensa, strerror(errno));
    nayta_poll(fd);
    ioctl(fd, JONO_TYHJENNA);
    tila(fd);
    close(fd);
    // @loppu taysi
}

// @alku esto
// Lapsi lukee estävästi ja nukkuu ytimessä, kunnes vanhempi kirjoittaa.
static void estava_luku(void)
{
    fflush(stdout);
    pid_t lapsi = fork();
    if (lapsi == 0) {
        char puskuri[64];
        int fd = open("/dev/jono1", O_RDONLY);
        ssize_t n = read(fd, puskuri, sizeof puskuri);
        printf("lapsi heräsi: %.*s", (int)n, puskuri);
        _exit(0);
    }
    struct timespec viive = {0, 200000000};
    nanosleep(&viive, NULL);
    int fd = open("/dev/jono1", O_WRONLY);
    printf("vanhempi kirjoittaa\n");
    fflush(stdout);
    if (write(fd, "kello 12\n", 9) != 9) {
        printf("kirjoitus: %s\n", strerror(errno));
    }
    waitpid(lapsi, NULL, 0);
    close(fd);
}
// @loppu esto

int main(void)
{
    setvbuf(stdout, NULL, _IOLBF, 0);
    perustoiminnot();
    estava_luku();
    return 0;
}
