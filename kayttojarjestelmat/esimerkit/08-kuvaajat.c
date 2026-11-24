// Tiedostokuvaajat: pienin vapaa numero, dup2-uudelleenohjaus ja
// forkissa jaettu tiedostosijainti.
#define _GNU_SOURCE
#include <fcntl.h>
#include <sys/wait.h>
#include <unistd.h>

#include "tarkista.h"

static void nayta(const char *nimi) {
    char puskuri[128] = {};
    int fd = TARKISTA(open(nimi, O_RDONLY));
    TARKISTA(read(fd, puskuri, sizeof puskuri - 1));
    TARKISTA(close(fd));
    for (char *c = puskuri; *c; c++) {
        if (*c == '\n') {
            *c = '|';
        }
    }
    printf("%s: %s\n", nimi, puskuri);
}

static int luo(const char *nimi, int liput) {
    return (int)TARKISTA(open(nimi, O_WRONLY | O_CREAT | liput, 0644));
}

int main(void) {
    // @alku pienin
    int a = luo("a.txt", O_TRUNC);
    int b = luo("b.txt", O_TRUNC);
    TARKISTA(close(a));
    int c = luo("c.txt", O_TRUNC);
    printf("a = %d, b = %d, c = %d\n", a, b, c);
    TARKISTA(close(b));
    TARKISTA(close(c));
    // @loppu pienin

    // @alku dup2
    fflush(stdout);
    int talteen = (int)TARKISTA(dup(STDOUT_FILENO));
    int loki = luo("loki.txt", O_TRUNC);
    TARKISTA(dup2(loki, STDOUT_FILENO)); // 1 osoittaa nyt tiedostoon
    TARKISTA(close(loki));
    printf("tämä menee tiedostoon\n");
    fflush(stdout);
    TARKISTA(dup2(talteen, STDOUT_FILENO));  // palautetaan
    TARKISTA(close(talteen));
    nayta("loki.txt");
    // @loppu dup2

    // @alku jaettu
    int fd = luo("jaettu.txt", O_TRUNC);
    pid_t pid = TARKISTA(fork());
    if (pid == 0) {                      // sama avoin tiedosto:
        TARKISTA(write(fd, "lapsi\n", 6));   // sijainti on yhteinen
        _exit(0);
    }
    TARKISTA(waitpid(pid, nullptr, 0));
    TARKISTA(write(fd, "vanhempi\n", 9));
    TARKISTA(close(fd));
    nayta("jaettu.txt");

    int x = luo("erilliset.txt", O_TRUNC);   // kaksi avointa tiedostoa:
    int y = luo("erilliset.txt", 0);         // kummallakin oma sijainti
    TARKISTA(write(x, "AAAAAA\n", 7));
    TARKISTA(write(y, "BB", 2));             // kirjoittaa päälle
    TARKISTA(close(x));
    TARKISTA(close(y));
    nayta("erilliset.txt");

    x = luo("lisays.txt", O_TRUNC | O_APPEND);
    y = luo("lisays.txt", O_APPEND);         // aina tiedoston loppuun
    TARKISTA(write(x, "AAAAAA\n", 7));
    TARKISTA(write(y, "BB\n", 3));
    TARKISTA(close(x));
    TARKISTA(close(y));
    nayta("lisays.txt");
    // @loppu jaettu
    return 0;
}
