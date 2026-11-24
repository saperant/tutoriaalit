// Prosessin tilat /proc/<pid>/stat-tiedostosta: R, S, T ja Z.
#define _GNU_SOURCE
#include <signal.h>
#include <sys/wait.h>
#include <unistd.h>

#include "tarkista.h"

// @alku tila
// Tila on kolmas kenttä: "pid (nimi) T ...". Nimessä voi olla
// välilyöntejä ja sulkeita, joten haetaan viimeinen ')'.
static char tila(pid_t pid) {
    char polku[64];
    snprintf(polku, sizeof polku, "/proc/%d/stat", (int)pid);
    FILE *f = fopen(polku, "r");
    if (f == nullptr) {
        return '-';                      // prosessia ei enää ole
    }
    char rivi[512];
    char *ok = fgets(rivi, sizeof rivi, f);
    fclose(f);
    char *sulku = ok ? strrchr(rivi, ')') : nullptr;
    return sulku && sulku[1] == ' ' ? sulku[2] : '?';
}
// @loppu tila

// Tilan vaihtuminen vie hetken: odotetaan enintään sekunti.
static char odota(pid_t pid, char haluttu) {
    for (int i = 0; i < 1000 && tila(pid) != haluttu; i++) {
        usleep(1000);
    }
    return tila(pid);
}

static volatile sig_atomic_t lopeta;
static void kasittelija(int) { lopeta = 1; }

int main(void) {
    struct sigaction sa = {.sa_handler = kasittelija};
    TARKISTA(sigaction(SIGUSR1, &sa, nullptr));

    // @alku elinkaari
    pid_t pid = TARKISTA(fork());
    if (pid == 0) {
        while (!lopeta) {}               // laskee: R
        for (;;) {
            pause();                     // odottaa: S
        }
    }
    printf("laskee:     %c\n", odota(pid, 'R'));
    TARKISTA(kill(pid, SIGUSR1));
    printf("odottaa:    %c\n", odota(pid, 'S'));

    int t;
    TARKISTA(kill(pid, SIGSTOP));
    TARKISTA(waitpid(pid, &t, WUNTRACED));
    printf("pysäytetty: %c (WIFSTOPPED %d)\n", odota(pid, 'T'),
           WIFSTOPPED(t));
    TARKISTA(kill(pid, SIGCONT));
    TARKISTA(waitpid(pid, &t, WCONTINUED));
    printf("jatkaa:     %c (WIFCONTINUED %d)\n", odota(pid, 'S'),
           WIFCONTINUED(t));

    TARKISTA(kill(pid, SIGTERM));
    siginfo_t tieto;                     // WNOWAIT: ei vielä korjata
    TARKISTA(waitid(P_PID, (id_t)pid, &tieto, WEXITED | WNOWAIT));
    printf("zombi:      %c (SIG%s)\n", tila(pid),
           sigabbrev_np(tieto.si_status));
    TARKISTA(waitpid(pid, nullptr, 0));
    printf("korjattu:   %c\n", tila(pid));
    // @loppu elinkaari
    return 0;
}
