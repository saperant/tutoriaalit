// Signaalit: käsittelijä, estäminen ja odottavat signaalit.
// Tavalliset signaalit eivät jonoudu, reaaliaikaiset jonoutuvat.
#define _GNU_SOURCE
#include <signal.h>
#include <unistd.h>

#include "tarkista.h"

// @alku kasittelija
static volatile sig_atomic_t usr1, reaali, viimeisin_arvo;

static void kasittele_usr1(int) { usr1++; }

static void kasittele_reaali(int, siginfo_t *tieto, void *) {
    reaali++;
    viimeisin_arvo = tieto->si_value.sival_int;
}
// @loppu kasittelija

int main(void) {
    // @alku asenna
    struct sigaction sa = {.sa_handler = kasittele_usr1};
    sigemptyset(&sa.sa_mask);
    TARKISTA(sigaction(SIGUSR1, &sa, nullptr));
    struct sigaction sr = {.sa_sigaction = kasittele_reaali,
                           .sa_flags = SA_SIGINFO};
    sigemptyset(&sr.sa_mask);
    TARKISTA(sigaction(SIGRTMIN, &sr, nullptr));

    TARKISTA(raise(SIGUSR1));            // toimitetaan heti
    printf("ilman estoa: käsittelijä ajettiin %d kerran\n", (int)usr1);
    // @loppu asenna

    // @alku esto
    sigset_t estetyt, odottavat;
    sigemptyset(&estetyt);
    sigaddset(&estetyt, SIGUSR1);
    sigaddset(&estetyt, SIGRTMIN);
    TARKISTA(sigprocmask(SIG_BLOCK, &estetyt, nullptr));
    usr1 = 0;
    for (int i = 0; i < 3; i++) {
        TARKISTA(raise(SIGUSR1));
        TARKISTA(sigqueue(getpid(), SIGRTMIN,
                          (union sigval){.sival_int = 100 + i}));
    }
    TARKISTA(sigpending(&odottavat));
    printf("estettynä: SIGUSR1 odottaa %s, käsittelijä ajettu %d\n",
           sigismember(&odottavat, SIGUSR1) ? "kyllä" : "ei", (int)usr1);
    TARKISTA(sigprocmask(SIG_UNBLOCK, &estetyt, nullptr));
    printf("eston poiston jälkeen: SIGUSR1 %d kerran, SIGRTMIN %d "
           "kertaa\n", (int)usr1, (int)reaali);
    printf("viimeisen reaaliaikaisen signaalin arvo: %d\n",
           (int)viimeisin_arvo);
    // @loppu esto

    // @alku ohita
    signal(SIGUSR2, SIG_IGN);
    TARKISTA(raise(SIGUSR2));            // ei vaikutusta
    printf("SIGUSR2 ohitettiin, prosessi elää\n");
    // @loppu ohita
    return 0;
}
