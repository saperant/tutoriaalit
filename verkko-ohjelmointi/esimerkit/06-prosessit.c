// Prosessi asiakasta kohden: palvelin hyväksyy yhteyden ja haarauttaa
// työprosessin, joka palvelee sen. SIGCHLD-käsittelijä korjaa päättyneet
// työprosessit, jotta zombeja ei kerry.
#define _GNU_SOURCE
#include "verkko.h"

enum { ASIAKKAITA = 4, PYYNTOJA = 100 };
static uint16_t portti;
static int kuuntelija;

// @alku palvele
// Rivipohjainen protokolla: "NELIO x" -> "x*x". stdio puskuroi, joten
// lukemiseen ja kirjoittamiseen tarvitaan omat FILE-oliot. Rivi luetaan
// fgets-kutsulla: fscanf-muodon "\n" odottaisi seuraavaa riviä.
static void palvele(int fd) {
    FILE *sisaan = fdopen(fd, "r");
    FILE *ulos = fdopen(dup(fd), "w");
    char rivi[64];
    long x;
    while (fgets(rivi, sizeof rivi, sisaan) != nullptr &&
           sscanf(rivi, "NELIO %ld", &x) == 1) {
        fprintf(ulos, "%ld\n", x * x);
        fflush(ulos);                    // vastaus heti verkkoon
    }
    fclose(ulos);
    fclose(sisaan);
}
// @loppu palvele

// @alku korjaa
static volatile sig_atomic_t korjattu;

static void sigchld(int) {
    int talteen = errno;                 // käsittelijä ei saa muuttaa errnoa
    while (waitpid(-1, nullptr, WNOHANG) > 0) {
        korjattu++;
    }
    errno = talteen;
}
// @loppu korjaa

// @alku palvelin
static int palvelin(void *) {
    struct sigaction sa = {.sa_handler = sigchld,
                           .sa_flags = SA_RESTART | SA_NOCLDSTOP};
    sigemptyset(&sa.sa_mask);
    TARKISTA(sigaction(SIGCHLD, &sa, nullptr));
    for (int i = 0; i < ASIAKKAITA; i++) {
        int yhteys = (int)TARKISTA(accept(kuuntelija, nullptr, nullptr));
        pid_t pid = (pid_t)TARKISTA(fork());
        if (pid == 0) {
            close(kuuntelija);           // työprosessi ei hyväksy uusia
            palvele(yhteys);
            _exit(0);
        }
        close(yhteys);                   // vanhempi ei palvele itse
    }
    sigset_t chld, vanha;                // estä SIGCHLD tarkistuksen ja
    sigemptyset(&chld);                  // odotuksen välissä, muuten
    sigaddset(&chld, SIGCHLD);           // herätys voisi hukkua
    TARKISTA(sigprocmask(SIG_BLOCK, &chld, &vanha));
    while (korjattu < ASIAKKAITA) {
        sigsuspend(&vanha);              // sallii SIGCHLD:n odottaessa
    }
    printf("palvelin: %d yhteyttä, %d työprosessia korjattu, ", ASIAKKAITA,
           (int)korjattu);
    printf("zombeja: %s\n", waitpid(-1, nullptr, WNOHANG) == -1 &&
                                    errno == ECHILD ? "ei" : "on");
    return 0;
}
// @loppu palvelin

static int asiakas(void *arg) {
    long kerroin = (long)(intptr_t)arg;
    int fd = yhdista(portti);
    FILE *sisaan = fdopen(fd, "r");
    FILE *ulos = fdopen(dup(fd), "w");
    int oikein = 0;
    for (long i = 1; i <= PYYNTOJA; i++) {
        long x = kerroin * 1000 + i, vastaus;
        char rivi[64];
        fprintf(ulos, "NELIO %ld\n", x);
        fflush(ulos);
        if (fgets(rivi, sizeof rivi, sisaan) != nullptr &&
            sscanf(rivi, "%ld", &vastaus) == 1 && vastaus == x * x) {
            oikein++;
        }
    }
    fclose(ulos);
    fclose(sisaan);
    return oikein == PYYNTOJA ? 0 : 1;
}

int main(void) {
    vahtikoira();
    kuuntelija = kuuntele(&portti);
    pid_t palvelimen = kaynnista(palvelin, nullptr);
    close(kuuntelija);
    pid_t asiakkaat[ASIAKKAITA];
    for (int i = 0; i < ASIAKKAITA; i++) {
        asiakkaat[i] = kaynnista(asiakas, (void *)(intptr_t)i);
    }
    int virheita = 0;
    for (int i = 0; i < ASIAKKAITA; i++) {
        virheita += odota(asiakkaat[i]) != 0;
    }
    virheita += odota(palvelimen) != 0;
    printf("asiakkaat: %d x %d pyyntöä, virheitä %d\n", ASIAKKAITA,
           PYYNTOJA, virheita);
    return virheita;
}
