// fork kopioi prosessin, waitpid odottaa lapsen päättymistä.
#define _GNU_SOURCE
#include <sys/wait.h>
#include <unistd.h>

#include "tarkista.h"

int main(void) {
    // @alku fork
    int laskuri = 10;
    fflush(stdout);                      // ks. 02-puskuri.c
    pid_t pid = TARKISTA(fork());
    if (pid == 0) {                      // lapsi
        laskuri += 1;
        printf("lapsi: laskuri = %d\n", laskuri);
        fflush(stdout);
        _exit(7);
    }
    int tila;                            // vanhempi
    TARKISTA(waitpid(pid, &tila, 0));
    printf("vanhempi: laskuri = %d\n", laskuri);
    if (WIFEXITED(tila)) {
        printf("lapsi päättyi koodilla %d\n", WEXITSTATUS(tila));
    }
    // @loppu fork

    // @alku monta
    pid_t lapset[3];
    for (int i = 0; i < 3; i++) {
        lapset[i] = TARKISTA(fork());
        if (lapset[i] == 0) {
            _exit(10 + i);
        }
    }
    for (int i = 2; i >= 0; i--) {       // kiinteä järjestys
        TARKISTA(waitpid(lapset[i], &tila, 0));
        printf("lapsi %d: koodi %d\n", i, WEXITSTATUS(tila));
    }
    printf("wait ilman lapsia: %s\n",
           wait(nullptr) == -1 && errno == ECHILD ? "ECHILD" : "?");
    // @loppu monta
    return 0;
}
