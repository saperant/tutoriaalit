// SIGCHLD tiedostokuvaajana: signalfd muuttaa asynkronisen signaalin
// tavalliseksi luettavaksi tapahtumaksi, jota voi odottaa pollilla.
#define _GNU_SOURCE
#include <poll.h>
#include <signal.h>
#include <sys/signalfd.h>
#include <sys/wait.h>
#include <unistd.h>

#include "tarkista.h"

enum { LAPSIA = 5 };

int main(void) {
    // @alku signalfd
    sigset_t joukko;
    sigemptyset(&joukko);
    sigaddset(&joukko, SIGCHLD);
    TARKISTA(sigprocmask(SIG_BLOCK, &joukko, nullptr));  // ei käsittelijää
    int sfd = TARKISTA(signalfd(-1, &joukko, SFD_CLOEXEC));

    for (int i = 0; i < LAPSIA; i++) {
        if (TARKISTA(fork()) == 0) {
            _exit(i + 1);
        }
    }
    int korjattu = 0, koodit[LAPSIA + 1] = {};
    while (korjattu < LAPSIA) {
        struct pollfd p = {.fd = sfd, .events = POLLIN};
        TARKISTA(poll(&p, 1, -1));
        struct signalfd_siginfo tieto;
        TARKISTA(read(sfd, &tieto, sizeof tieto));
        // Useat SIGCHLD:t voivat yhdistyä yhdeksi: korjataan kaikki.
        int tila;
        for (pid_t pid; (pid = waitpid(-1, &tila, WNOHANG)) > 0;) {
            koodit[WEXITSTATUS(tila)]++;
            korjattu++;
        }
    }
    printf("korjattu %d lasta, koodit:", korjattu);
    for (int k = 1; k <= LAPSIA; k++) {
        printf(" %d", koodit[k] ? k : 0);
    }
    printf("\n");
    TARKISTA(close(sfd));
    // @loppu signalfd
    return 0;
}
