// Signaali keskeyttää estävän järjestelmäkutsun: ilman SA_RESTART-
// lippua kutsu palauttaa EINTR-virheen, lipun kanssa ydin jatkaa sitä.
#define _GNU_SOURCE
#include <signal.h>
#include <sys/time.h>
#include <unistd.h>

#include "tarkista.h"

static int putki[2];

// @alku kasittelija
// Käsittelijässä saa kutsua vain async-signal-safe-funktioita.
// write kuuluu niihin, printf ja malloc eivät.
static void herata(int) {
    int talteen = errno;                 // käsittelijä ei saa muuttaa
    (void)write(putki[1], "!", 1);       // keskeytetyn koodin errnoa
    errno = talteen;
}
// @loppu kasittelija

// @alku kokeile
static void kokeile(int liput) {
    struct sigaction sa = {.sa_handler = herata, .sa_flags = liput};
    sigemptyset(&sa.sa_mask);
    TARKISTA(sigaction(SIGALRM, &sa, nullptr));
    struct itimerval ajastin = {.it_value = {.tv_usec = 20'000}};
    TARKISTA(setitimer(ITIMER_REAL, &ajastin, nullptr));  // 20 ms

    char c;
    ssize_t n = read(putki[0], &c, 1);   // estää, kunnes signaali tulee
    if (n == -1) {
        printf("%-14s read = -1, errno %s\n",
               liput ? "SA_RESTART:" : "ilman lippua:",
               strerrorname_np(errno));
        TARKISTA(read(putki[0], &c, 1));   // käsittelijän kirjoittama
    } else {
        printf("%-14s read = %zd, luettiin '%c'\n",
               liput ? "SA_RESTART:" : "ilman lippua:", n, c);
    }
}
// @loppu kokeile

int main(void) {
    TARKISTA(pipe(putki));
    kokeile(0);
    kokeile(SA_RESTART);
    return 0;
}
