#define _GNU_SOURCE
// Monen kuvaajan odottaminen: estämätön luku ja poll. Kaksi lasta
// kirjoittaa omaan putkeensa eri aikoina, ja vanhempi palvelee
// kumpaakin yhdellä säikeellä.
#include <fcntl.h>
#include <poll.h>
#include <sys/wait.h>
#include <unistd.h>

#include "tarkista.h"

enum { LAPSIA = 2 };

int main(void) {
    int luku[LAPSIA];
    int lupa[LAPSIA];      // vanhempi antaa näillä kirjoitusvuoron
    for (int i = 0; i < LAPSIA; i++) {
        int data[2], ohjaus[2];
        TARKISTA(pipe2(data, O_CLOEXEC));
        TARKISTA(pipe2(ohjaus, O_CLOEXEC));
        if (TARKISTA(fork()) == 0) {
            // Lapsi sulkee päät, joita se ei käytä: omien putkiensa
            // vastapäät ja aiemmilta lapsilta perityt. Muuten kukaan
            // ei koskaan näe tiedoston loppua.
            TARKISTA(close(data[0]));
            TARKISTA(close(ohjaus[1]));
            for (int j = 0; j < i; j++) {
                TARKISTA(close(luku[j]));
                TARKISTA(close(lupa[j]));
            }
            char merkki;
            // Lapsi odottaa lupaa, kirjoittaa viestin ja lopettaa.
            while (read(ohjaus[0], &merkki, 1) == 1) {
                char viesti[32];
                int n = snprintf(viesti, sizeof viesti, "lapsi %d: %c",
                                 i, merkki);
                TARKISTA(write(data[1], viesti, (size_t)n));
            }
            _exit(0);
        }
        TARKISTA(close(data[1]));
        TARKISTA(close(ohjaus[0]));
        luku[i] = data[0];
        lupa[i] = ohjaus[1];
    }

    // @alku eagain
    // Estämätön kuvaaja: tyhjä putki ei pysäytä lukijaa, vaan read
    // palauttaa virheen EAGAIN.
    int liput = (int)TARKISTA(fcntl(luku[0], F_GETFL));
    TARKISTA(fcntl(luku[0], F_SETFL, liput | O_NONBLOCK));
    char puskuri[32];
    ssize_t n = read(luku[0], puskuri, sizeof puskuri);
    printf("tyhjä putki, O_NONBLOCK: %s\n",
           n == -1 ? strerrorname_np(errno) : "dataa");
    // @loppu eagain

    // @alku poll
    struct pollfd kuvaajat[LAPSIA] = {
        {.fd = luku[0], .events = POLLIN},
        {.fd = luku[1], .events = POLLIN},
    };
    printf("ei dataa, aikaraja 0: poll palautti %d\n",
           poll(kuvaajat, LAPSIA, 0));

    // Kirjoitusvuorot: lapsi 1, lapsi 0, lapsi 1. Sen jälkeen
    // lupaputket suljetaan yksi kerrallaan, jolloin lapset lopettavat
    // (ja tuloste on joka ajossa samassa järjestyksessä).
    const int vuorot[] = {1, 0, 1};
    int vuoro = 0, auki = LAPSIA;
    TARKISTA(write(lupa[vuorot[vuoro]], "a", 1));
    while (auki > 0) {
        TARKISTA(poll(kuvaajat, LAPSIA, -1));    // odota mitä tahansa
        for (int i = 0; i < LAPSIA; i++) {
            if (!(kuvaajat[i].revents & (POLLIN | POLLHUP))) {
                continue;
            }
            n = TARKISTA(read(kuvaajat[i].fd, puskuri, sizeof puskuri));
            if (n == 0) {                  // kirjoittaja sulki putken
                printf("kuvaaja %d: loppu\n", i);
                kuvaajat[i].fd = -1;       // poll ohittaa negatiiviset
                if (--auki > 0) {
                    TARKISTA(close(lupa[1]));
                }
                continue;
            }
            printf("kuvaaja %d: %.*s\n", i, (int)n, puskuri);
            if (++vuoro < 3) {
                char merkki = (char)('a' + vuoro);
                TARKISTA(write(lupa[vuorot[vuoro]], &merkki, 1));
            } else {
                TARKISTA(close(lupa[0]));
            }
        }
    }
    // @loppu poll

    for (int i = 0; i < LAPSIA; i++) {
        TARKISTA(close(luku[i]));
        TARKISTA(wait(nullptr));
    }
}
