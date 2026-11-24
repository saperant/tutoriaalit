// Herätysajastimen testi: asettaa herätyksen laitteelle /dev/herate ja
// odottaa sitä poll()-kutsulla.
//
// Käyttö: heratetesti sekunnit [kertaa]
#include <errno.h>
#include <fcntl.h>
#include <poll.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

// @alku odota
int main(int argc, char **argv)
{
    setvbuf(stdout, NULL, _IOLBF, 0);
    if (argc < 2) {
        fprintf(stderr, "käyttö: %s sekunnit [kertaa]\n", argv[0]);
        return 2;
    }
    int sekunnit = atoi(argv[1]);
    int kertaa = argc > 2 ? atoi(argv[2]) : 1;
    int fd = open("/dev/herate", O_RDWR | O_NONBLOCK);
    char rivi[64];
    if (fd < 0) {
        printf("open: %s\n", strerror(errno));
        return 1;
    }
    if (read(fd, rivi, sizeof rivi) < 0) {
        printf("luku ennen herätystä: %s\n", strerror(errno));
    }
    if (write(fd, argv[1], strlen(argv[1])) < 0) {
        printf("asetus: %s\n", strerror(errno));
        return 1;
    }
    for (int i = 0; i < kertaa; i++) {
        struct pollfd p = {.fd = fd, .events = POLLIN};
        // Väljä aikaraja: QEMU:n kello voi jätättää kuormitetulla koneella.
        if (poll(&p, 1, (sekunnit + 3) * 1000) != 1) {
            printf("ei herätystä %d sekunnissa\n", sekunnit + 3);
            return 1;
        }
        ssize_t n = read(fd, rivi, sizeof rivi);
        printf("%.*s", (int)n, rivi);
    }
    close(fd);
    return 0;
}
// @loppu odota
